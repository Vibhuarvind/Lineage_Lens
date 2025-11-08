-- Financial Data Pipeline Sample
-- This file contains financial reporting and analytics pipeline

-- Source financial data
CREATE TABLE raw_transactions (
    transaction_id INT PRIMARY KEY,
    account_id VARCHAR(50),
    transaction_date DATE,
    amount DECIMAL(15,2),
    transaction_type VARCHAR(20),
    description TEXT,
    category VARCHAR(100),
    vendor_id VARCHAR(50)
);

CREATE TABLE raw_accounts (
    account_id VARCHAR(50) PRIMARY KEY,
    account_name VARCHAR(200),
    account_type VARCHAR(50),
    department VARCHAR(100),
    cost_center VARCHAR(50),
    manager_id VARCHAR(50)
);

CREATE TABLE raw_budget_allocations (
    budget_id INT PRIMARY KEY,
    account_id VARCHAR(50),
    fiscal_year INT,
    fiscal_quarter INT,
    budgeted_amount DECIMAL(15,2),
    category VARCHAR(100)
);

-- Cleansed financial data
CREATE TABLE clean_transactions AS
SELECT 
    transaction_id,
    account_id,
    transaction_date,
    amount,
    UPPER(transaction_type) as transaction_type,
    description,
    COALESCE(category, 'Uncategorized') as category,
    vendor_id,
    EXTRACT(YEAR FROM transaction_date) as fiscal_year,
    EXTRACT(QUARTER FROM transaction_date) as fiscal_quarter,
    EXTRACT(MONTH FROM transaction_date) as fiscal_month,
    CASE 
        WHEN transaction_type = 'DEBIT' THEN amount * -1
        ELSE amount
    END as signed_amount
FROM raw_transactions
WHERE amount != 0
    AND transaction_date IS NOT NULL;

CREATE TABLE account_hierarchy AS
SELECT 
    a.account_id,
    a.account_name,
    UPPER(a.account_type) as account_type,
    a.department,
    a.cost_center,
    a.manager_id,
    CASE 
        WHEN a.account_type IN ('REVENUE', 'INCOME') THEN 'INCOME_STATEMENT'
        WHEN a.account_type IN ('EXPENSE', 'COST') THEN 'INCOME_STATEMENT'
        WHEN a.account_type IN ('ASSET', 'LIABILITY', 'EQUITY') THEN 'BALANCE_SHEET'
        ELSE 'OTHER'
    END as financial_statement_category
FROM raw_accounts a;

-- Financial reporting tables
CREATE TABLE monthly_financials AS
SELECT 
    ct.fiscal_year,
    ct.fiscal_month,
    ah.department,
    ah.account_type,
    ah.financial_statement_category,
    COUNT(ct.transaction_id) as transaction_count,
    SUM(ct.signed_amount) as total_amount,
    AVG(ct.signed_amount) as average_transaction_amount,
    MIN(ct.signed_amount) as min_transaction,
    MAX(ct.signed_amount) as max_transaction
FROM clean_transactions ct
JOIN account_hierarchy ah ON ct.account_id = ah.account_id
GROUP BY ct.fiscal_year, ct.fiscal_month, ah.department, ah.account_type, ah.financial_statement_category;

CREATE TABLE budget_vs_actual AS
SELECT 
    ba.fiscal_year,
    ba.fiscal_quarter,
    ba.account_id,
    ah.account_name,
    ah.department,
    ba.budgeted_amount,
    COALESCE(SUM(ct.signed_amount), 0) as actual_amount,
    ba.budgeted_amount - COALESCE(SUM(ct.signed_amount), 0) as variance,
    CASE 
        WHEN ba.budgeted_amount != 0 THEN 
            (COALESCE(SUM(ct.signed_amount), 0) / ba.budgeted_amount) * 100
        ELSE 0
    END as budget_utilization_percent
FROM raw_budget_allocations ba
JOIN account_hierarchy ah ON ba.account_id = ah.account_id
LEFT JOIN clean_transactions ct ON ba.account_id = ct.account_id 
    AND ba.fiscal_year = ct.fiscal_year
    AND ba.fiscal_quarter = ct.fiscal_quarter
GROUP BY ba.fiscal_year, ba.fiscal_quarter, ba.account_id, ah.account_name, ah.department, ba.budgeted_amount;

-- Profitability analysis
CREATE TABLE profit_loss_statement AS
SELECT 
    mf.fiscal_year,
    mf.fiscal_month,
    mf.department,
    SUM(CASE WHEN mf.account_type = 'REVENUE' THEN mf.total_amount ELSE 0 END) as total_revenue,
    SUM(CASE WHEN mf.account_type = 'EXPENSE' THEN mf.total_amount ELSE 0 END) as total_expenses,
    SUM(CASE WHEN mf.account_type = 'COST' THEN mf.total_amount ELSE 0 END) as total_costs,
    SUM(CASE WHEN mf.account_type = 'REVENUE' THEN mf.total_amount ELSE 0 END) +
    SUM(CASE WHEN mf.account_type IN ('EXPENSE', 'COST') THEN mf.total_amount ELSE 0 END) as net_profit,
    CASE 
        WHEN SUM(CASE WHEN mf.account_type = 'REVENUE' THEN mf.total_amount ELSE 0 END) > 0 THEN
            (SUM(CASE WHEN mf.account_type = 'REVENUE' THEN mf.total_amount ELSE 0 END) +
             SUM(CASE WHEN mf.account_type IN ('EXPENSE', 'COST') THEN mf.total_amount ELSE 0 END)) /
            SUM(CASE WHEN mf.account_type = 'REVENUE' THEN mf.total_amount ELSE 0 END) * 100
        ELSE 0
    END as profit_margin_percent
FROM monthly_financials mf
WHERE mf.financial_statement_category = 'INCOME_STATEMENT'
GROUP BY mf.fiscal_year, mf.fiscal_month, mf.department;

-- Department performance
CREATE TABLE department_performance AS
SELECT 
    pls.department,
    AVG(pls.total_revenue) as avg_monthly_revenue,
    AVG(pls.total_expenses + pls.total_costs) as avg_monthly_expenses,
    AVG(pls.net_profit) as avg_monthly_profit,
    AVG(pls.profit_margin_percent) as avg_profit_margin,
    STDDEV(pls.net_profit) as profit_volatility,
    COUNT(*) as reporting_months,
    MAX(pls.net_profit) as best_month_profit,
    MIN(pls.net_profit) as worst_month_profit
FROM profit_loss_statement pls
GROUP BY pls.department;

-- Executive financial summary
CREATE TABLE executive_financial_summary AS
SELECT 
    pls.fiscal_year,
    CONCAT('Q', CEIL(pls.fiscal_month / 3.0)) as quarter,
    SUM(pls.total_revenue) as quarterly_revenue,
    SUM(pls.total_expenses + pls.total_costs) as quarterly_expenses,
    SUM(pls.net_profit) as quarterly_profit,
    COUNT(DISTINCT pls.department) as departments_reporting,
    AVG(dp.avg_profit_margin) as average_department_margin,
    SUM(CASE WHEN pls.net_profit > 0 THEN 1 ELSE 0 END) as profitable_department_months,
    MAX(bva.budget_utilization_percent) as highest_budget_utilization
FROM profit_loss_statement pls
JOIN department_performance dp ON pls.department = dp.department
LEFT JOIN budget_vs_actual bva ON pls.fiscal_year = bva.fiscal_year
GROUP BY pls.fiscal_year, CEIL(pls.fiscal_month / 3.0)
ORDER BY pls.fiscal_year, CEIL(pls.fiscal_month / 3.0);
