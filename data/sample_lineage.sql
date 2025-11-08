-- Sample Data Lineage SQL for Testing Lineage Lens
-- This file demonstrates a complete data pipeline

-- Source tables (these would be your raw data)
CREATE TABLE raw_customers (
    customer_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    created_date DATE
);

CREATE TABLE raw_orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(10,2),
    order_date DATE,
    status VARCHAR(20)
);

CREATE TABLE raw_products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    supplier_id INT,
    cost_price DECIMAL(10,2)
);

-- Intermediate staging tables
CREATE TABLE staging_customers AS
SELECT 
    customer_id,
    CONCAT(first_name, ' ', last_name) as full_name,
    LOWER(email) as email_normalized,
    phone,
    created_date
FROM raw_customers
WHERE email IS NOT NULL;

CREATE TABLE staging_orders AS
SELECT 
    o.order_id,
    o.customer_id,
    o.product_id,
    o.quantity,
    o.unit_price,
    o.quantity * o.unit_price as line_total,
    o.order_date,
    o.status
FROM raw_orders o
JOIN raw_customers c ON o.customer_id = c.customer_id
WHERE o.status != 'CANCELLED';

-- Business logic tables
CREATE TABLE customer_segments AS
SELECT 
    c.customer_id,
    c.full_name,
    c.email_normalized,
    COUNT(o.order_id) as total_orders,
    SUM(o.line_total) as total_spent,
    CASE 
        WHEN SUM(o.line_total) > 1000 THEN 'VIP'
        WHEN SUM(o.line_total) > 500 THEN 'Premium'
        ELSE 'Standard'
    END as customer_segment
FROM staging_customers c
LEFT JOIN staging_orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.full_name, c.email_normalized;

CREATE TABLE product_performance AS
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    COUNT(o.order_id) as total_orders,
    SUM(o.quantity) as total_quantity_sold,
    SUM(o.line_total) as total_revenue,
    AVG(o.line_total) as avg_order_value
FROM raw_products p
JOIN staging_orders o ON p.product_id = o.product_id
GROUP BY p.product_id, p.product_name, p.category;

-- Final reporting tables
CREATE TABLE monthly_sales_summary AS
SELECT 
    DATE_TRUNC('month', o.order_date) as sales_month,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    COUNT(o.order_id) as total_orders,
    SUM(o.line_total) as total_revenue,
    AVG(o.line_total) as avg_order_value
FROM staging_orders o
GROUP BY DATE_TRUNC('month', o.order_date);

CREATE TABLE customer_lifetime_value AS
SELECT 
    cs.customer_id,
    cs.full_name,
    cs.customer_segment,
    cs.total_orders,
    cs.total_spent,
    pp.category as favorite_category,
    mss.sales_month as last_purchase_month
FROM customer_segments cs
JOIN staging_orders so ON cs.customer_id = so.customer_id
JOIN product_performance pp ON so.product_id = pp.product_id
JOIN monthly_sales_summary mss ON DATE_TRUNC('month', so.order_date) = mss.sales_month
WHERE so.order_date = (
    SELECT MAX(order_date) 
    FROM staging_orders so2 
    WHERE so2.customer_id = cs.customer_id
);
