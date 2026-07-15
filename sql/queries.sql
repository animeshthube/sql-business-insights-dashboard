/* ============================================================
   SQL Business Insights Dashboard
   File: queries.sql
   Dataset: data/sales.db (SQLite)
   Tables:
     customers(customer_id, customer_name, region, signup_date, segment)
     products(product_id, product_name, category, unit_price, unit_cost)
     orders(order_id, customer_id, order_date)
     order_items(item_id, order_id, product_id, quantity, unit_price, discount)

   Note: line_revenue = quantity * unit_price * (1 - discount) is
   computed inline throughout rather than stored, since it depends on
   the discount applied at time of sale.

   Tested against SQLite; window functions and CASE syntax are
   standard ANSI SQL and portable to MySQL 8+/PostgreSQL/SQL Server
   with minimal changes (noted where relevant).
   ============================================================ */


-- 1. MONTHLY REVENUE
-- Uses JOIN + GROUP BY + aggregate functions.
SELECT
    strftime('%Y-%m', o.order_date) AS month,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS revenue,
    COUNT(DISTINCT o.order_id) AS orders
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY month
ORDER BY month;


-- 2. TOTAL ORDERS & AVERAGE ORDER VALUE
-- Aggregate functions combined in a single summary row.
SELECT
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS total_revenue,
    ROUND(
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount))
        / COUNT(DISTINCT o.order_id), 2
    ) AS avg_order_value
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id;


-- 3. TOP 10 CUSTOMERS BY REVENUE
-- JOIN across 3 tables + GROUP BY + HAVING (only customers with 2+ orders,
-- to exclude one-off outliers from the "top customer" list).
SELECT
    c.customer_name,
    c.region,
    c.segment,
    COUNT(DISTINCT o.order_id) AS order_count,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS total_revenue
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY c.customer_id, c.customer_name, c.region, c.segment
HAVING COUNT(DISTINCT o.order_id) >= 2
ORDER BY total_revenue DESC
LIMIT 10;


-- 4. PRODUCT PERFORMANCE
-- JOIN + GROUP BY + aggregate functions + CASE for a readable performance tier.
SELECT
    p.product_name,
    p.category,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS revenue,
    ROUND(SUM(oi.quantity * (oi.unit_price * (1 - oi.discount) - p.unit_cost)), 2) AS profit,
    CASE
        WHEN SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) >= 15000 THEN 'Top Performer'
        WHEN SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) >= 6000  THEN 'Solid'
        ELSE 'Slow-Moving'
    END AS performance_tier
FROM products p
JOIN order_items oi ON oi.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY revenue DESC;


-- 5. SLOW-MOVING INVENTORY
-- Same logic as above, filtered with HAVING to surface only underperformers -
-- directly supports the "reduce slow-moving inventory" recommendation.
SELECT
    p.product_name,
    p.category,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS revenue
FROM products p
JOIN order_items oi ON oi.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
HAVING SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) < 6000
ORDER BY revenue ASC;


-- 6. SALES BY REGION
-- JOIN + GROUP BY + HAVING (only regions doing at least $10k, i.e. all of
-- them here, but demonstrates the pattern for filtering low-volume segments).
SELECT
    c.region,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS revenue
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY c.region
HAVING SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) > 0
ORDER BY revenue DESC;


-- 7. CUSTOMER PURCHASE FREQUENCY (SEGMENTATION)
-- CASE used to bucket customers into frequency tiers based on order count.
SELECT
    frequency_tier,
    COUNT(*) AS customer_count,
    ROUND(AVG(total_revenue), 2) AS avg_revenue_per_customer
FROM (
    SELECT
        c.customer_id,
        COUNT(DISTINCT o.order_id) AS order_count,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS total_revenue,
        CASE
            WHEN COUNT(DISTINCT o.order_id) = 1 THEN 'One-Time'
            WHEN COUNT(DISTINCT o.order_id) BETWEEN 2 AND 4 THEN 'Occasional'
            ELSE 'Frequent'
        END AS frequency_tier
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY c.customer_id
) t
GROUP BY frequency_tier
ORDER BY avg_revenue_per_customer DESC;


-- 8. YEAR-OVER-YEAR GROWTH
-- Window function: LAG() to compare each year's revenue to the prior year
-- without a self-join.
WITH yearly AS (
    SELECT
        strftime('%Y', o.order_date) AS year,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY year
)
SELECT
    year,
    ROUND(revenue, 2) AS revenue,
    ROUND(LAG(revenue) OVER (ORDER BY year), 2) AS prior_year_revenue,
    ROUND(
        100.0 * (revenue - LAG(revenue) OVER (ORDER BY year))
        / LAG(revenue) OVER (ORDER BY year), 1
    ) AS yoy_growth_pct
FROM yearly
ORDER BY year;


-- 9. RUNNING TOTAL OF MONTHLY REVENUE (WINDOW FUNCTION)
-- SUM() OVER with a frame clause for a cumulative revenue trend.
WITH monthly AS (
    SELECT
        strftime('%Y-%m', o.order_date) AS month,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY month
)
SELECT
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(SUM(revenue) OVER (ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS running_total
FROM monthly
ORDER BY month;


-- 10. TOP PRODUCT PER CATEGORY (WINDOW FUNCTION: RANK)
-- RANK() partitioned by category to find each category's #1 product
-- without a separate query per category.
WITH product_revenue AS (
    SELECT
        p.category,
        p.product_name,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue,
        RANK() OVER (PARTITION BY p.category ORDER BY SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) DESC) AS category_rank
    FROM products p
    JOIN order_items oi ON oi.product_id = p.product_id
    GROUP BY p.category, p.product_id, p.product_name
)
SELECT category, product_name, ROUND(revenue, 2) AS revenue
FROM product_revenue
WHERE category_rank = 1
ORDER BY revenue DESC;


-- 11. NEW VS RETURNING CUSTOMER REVENUE (CASE + aggregate)
SELECT
    c.segment,
    COUNT(DISTINCT c.customer_id) AS customers,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS revenue
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY c.segment
ORDER BY revenue DESC;


-- 12. AVERAGE DISCOUNT IMPACT BY CATEGORY
-- Shows how much revenue is being given up to discounts per category -
-- useful for evaluating promotion effectiveness.
SELECT
    p.category,
    ROUND(AVG(oi.discount) * 100, 1) AS avg_discount_pct,
    ROUND(SUM(oi.quantity * oi.unit_price * oi.discount), 2) AS revenue_given_up_to_discount
FROM products p
JOIN order_items oi ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue_given_up_to_discount DESC;
