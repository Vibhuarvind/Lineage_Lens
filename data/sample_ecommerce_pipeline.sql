-- E-commerce Data Pipeline Sample
-- This file contains a realistic data pipeline for an e-commerce platform

-- Raw data sources
CREATE TABLE raw_customers (
    customer_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    registration_date DATE,
    country VARCHAR(50)
);

CREATE TABLE raw_products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(200),
    category VARCHAR(100),
    price DECIMAL(10,2),
    supplier_id INT,
    created_date DATE
);

CREATE TABLE raw_orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date TIMESTAMP,
    status VARCHAR(20),
    total_amount DECIMAL(10,2)
);

CREATE TABLE raw_order_items (
    order_item_id INT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(10,2)
);

-- Staging layer - cleaned and validated data
CREATE TABLE staging_customers AS
SELECT 
    customer_id,
    TRIM(CONCAT(first_name, ' ', last_name)) as full_name,
    LOWER(email) as email,
    registration_date,
    UPPER(country) as country,
    CASE 
        WHEN registration_date >= '2023-01-01' THEN 'new'
        ELSE 'existing'
    END as customer_type
FROM raw_customers
WHERE email IS NOT NULL 
    AND email LIKE '%@%.%';

CREATE TABLE staging_products AS
SELECT 
    product_id,
    product_name,
    UPPER(category) as category,
    price,
    supplier_id,
    created_date,
    CASE 
        WHEN price > 100 THEN 'premium'
        WHEN price > 50 THEN 'standard'
        ELSE 'budget'
    END as price_tier
FROM raw_products
WHERE price > 0;

CREATE TABLE staging_orders AS
SELECT 
    o.order_id,
    o.customer_id,
    o.order_date,
    o.status,
    o.total_amount,
    DATE(o.order_date) as order_date_only,
    EXTRACT(YEAR FROM o.order_date) as order_year,
    EXTRACT(MONTH FROM o.order_date) as order_month
FROM raw_orders o
JOIN staging_customers c ON o.customer_id = c.customer_id
WHERE o.status != 'cancelled';

-- Mart layer - business logic and aggregations
CREATE TABLE customer_summary AS
SELECT 
    c.customer_id,
    c.full_name,
    c.email,
    c.country,
    c.customer_type,
    COUNT(o.order_id) as total_orders,
    SUM(o.total_amount) as lifetime_value,
    AVG(o.total_amount) as average_order_value,
    MIN(o.order_date) as first_order_date,
    MAX(o.order_date) as last_order_date,
    CASE 
        WHEN SUM(o.total_amount) > 1000 THEN 'high_value'
        WHEN SUM(o.total_amount) > 500 THEN 'medium_value'
        ELSE 'low_value'
    END as value_segment
FROM staging_customers c
LEFT JOIN staging_orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.full_name, c.email, c.country, c.customer_type;

CREATE TABLE product_performance AS
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.price_tier,
    COUNT(oi.order_item_id) as total_orders,
    SUM(oi.quantity) as total_quantity_sold,
    SUM(oi.quantity * oi.unit_price) as total_revenue,
    AVG(oi.unit_price) as average_selling_price,
    COUNT(DISTINCT o.customer_id) as unique_customers
FROM staging_products p
JOIN raw_order_items oi ON p.product_id = oi.product_id
JOIN staging_orders o ON oi.order_id = o.order_id
GROUP BY p.product_id, p.product_name, p.category, p.price_tier;

CREATE TABLE monthly_sales_summary AS
SELECT 
    o.order_year,
    o.order_month,
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    SUM(o.total_amount) as total_revenue,
    AVG(o.total_amount) as average_order_value,
    COUNT(DISTINCT oi.product_id) as products_sold
FROM staging_orders o
JOIN raw_order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_year, o.order_month
ORDER BY o.order_year, o.order_month;

-- Final business reports
CREATE TABLE executive_dashboard AS
SELECT 
    'Q' || CEIL(ms.order_month / 3.0) || ' ' || ms.order_year as quarter,
    SUM(ms.total_revenue) as quarterly_revenue,
    AVG(ms.total_orders) as avg_monthly_orders,
    COUNT(DISTINCT cs.customer_id) as active_customers,
    SUM(CASE WHEN cs.value_segment = 'high_value' THEN 1 ELSE 0 END) as high_value_customers,
    AVG(pp.total_revenue) as avg_product_revenue
FROM monthly_sales_summary ms
JOIN customer_summary cs ON 1=1  -- Cross join for aggregation
JOIN product_performance pp ON 1=1  -- Cross join for aggregation
GROUP BY ms.order_year, CEIL(ms.order_month / 3.0)
ORDER BY ms.order_year, CEIL(ms.order_month / 3.0);

-- Customer retention analysis
CREATE TABLE customer_retention_cohorts AS
SELECT 
    c.customer_id,
    c.value_segment,
    c.first_order_date,
    c.last_order_date,
    c.total_orders,
    DATEDIFF(c.last_order_date, c.first_order_date) as customer_lifespan_days,
    CASE 
        WHEN c.last_order_date >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY) THEN 'active'
        WHEN c.last_order_date >= DATE_SUB(CURRENT_DATE, INTERVAL 90 DAY) THEN 'at_risk'
        ELSE 'churned'
    END as retention_status
FROM customer_summary c
WHERE c.total_orders > 0;
