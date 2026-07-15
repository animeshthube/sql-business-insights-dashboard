# SQL Business Insights Report

**Data source:** `data/sales.db` (SQLite) — 260 customers, 44 products,
3,833 orders, 6,765 order line items
**Period covered:** March 2023 – December 2025 (2023 is a partial year;
the business's first orders begin in March 2023)

---

## 1. Headline Numbers

| Metric | Value |
|---|---|
| Total Revenue | $1,720,686.08 |
| Total Orders | 3,833 |
| Average Order Value | $448.91 |
| Total Profit | $344,396.86 |
| Overall Profit Margin | 20.0% |

## 2. Monthly Revenue & Growth

Monthly revenue (Query 1) shows strong, consistent seasonality: **November
and December are the strongest months every year**, and **July/August
are consistent troughs**. This is a reliable pattern worth planning
inventory and staffing around.

**Year-over-year growth** (Query 8, using a `LAG()` window function):

| Year | Revenue | YoY Growth |
|---|---|---|
| 2023 (partial, Mar–Dec) | $105,318 | — |
| 2024 | $738,509 | +601% *(vs. a partial prior year — not a fair comparison)* |
| 2025 | $876,859 | **+18.7%** |

The 2023→2024 jump is inflated because 2023 only has ~9.5 months of
data and represents the business's earliest, smallest period. The
**2024→2025 growth of +18.7% is the meaningful, comparable figure** —
a healthy, sustainable growth rate for a maturing retail operation.

## 3. Top Customers

Query 3 (JOIN across `customers` → `orders` → `order_items`, filtered
with `HAVING order_count >= 2` to exclude one-off outliers) identifies
the top 10 customers by revenue — led by **Rowan Ortiz** ($19,381
across 34 orders) and **Sam Ortiz** ($19,371 across 39 orders). These
customers are placing far more orders than average and represent
concentrated revenue risk if lost.

## 4. Customer Purchase Frequency

Segmenting all 260 customers by order count (Query 7, using `CASE`
inside a subquery) reveals a striking pattern:

| Tier | Customers | Avg Revenue/Customer |
|---|---|---|
| Frequent (5+ orders) | 199 (77%) | $8,429.93 |
| Occasional (2–4 orders) | 32 (12%) | $1,164.86 |
| One-Time (1 order) | 14 (5%) | $418.12 |

**Frequent customers generate ~20x the revenue of one-time buyers.**
The business's customer base skews heavily toward repeat purchasers,
which is a strong sign of product-market fit — but also means retention
of the "Frequent" tier is disproportionately critical to revenue.

## 5. Product Performance

Query 4 (JOIN + `CASE`) tiers all 44 products into Top Performer
(≥$15,000 revenue), Solid ($6,000–$15,000), and Slow-Moving (<$6,000).
**Smart Doorbell** leads all products at $220,000 in revenue (457
units), followed by **Insulated Water Bottle** ($157,602) and
**Portable SSD 1TB** ($139,837).

## 6. Slow-Moving Inventory

Query 5 isolates underperformers with `HAVING revenue < 6000` — **7 of
44 products** fall into this category, concentrated in **Apparel** and
**Beauty & Personal Care**. The lowest performer, **Hair Dryer**, has
generated only $602 across the full period.

## 7. Sales by Region

| Region | Orders | Revenue |
|---|---|---|
| Northeast | 1,173 | $558,619.30 |
| West | 1,210 | $534,437.37 |
| Midwest | 834 | $351,451.04 |
| South | 616 | $276,178.37 |

**South generates roughly half the revenue of Northeast**, despite
having a full customer base in the dataset — the clearest regional
underperformance signal in the data.

## 8. Discount Impact

Query 12 shows discount usage is fairly consistent across categories
(5.6%–6.1% average discount), with **Electronics giving up the most
absolute revenue to discounting** ($43,669) simply due to its higher
price points — not because it's discounted more aggressively than
other categories.

---

## Business Recommendations

1. **Increase inventory / marketing for top-selling products** —
   Smart Doorbell, Insulated Water Bottle, and Portable SSD 1TB
   collectively drive a disproportionate share of revenue; ensure
   stock levels and ad spend reflect this concentration.
2. **Investigate the South region's underperformance** — at roughly
   half the revenue of the top region despite a comparable customer
   base, this points to a coverage, pricing, or awareness gap worth a
   dedicated review.
3. **Build a retention program for "Frequent" tier customers** — this
   group is 77% of customers but drives the overwhelming majority of
   revenue; even a small increase in churn here would materially hurt
   revenue. Consider a loyalty program or account-manager touch for
   top spenders like Rowan Ortiz and Sam Ortiz.
4. **Reduce or reposition slow-moving inventory** — the 7 identified
   underperformers (led by Hair Dryer, Women's Leggings, and Men's
   Hoodie) are strong candidates for clearance pricing, bundling, or
   discontinuation to free up working capital.
5. **Plan around confirmed seasonality** — Nov/Dec demand spikes and
   Jul/Aug troughs are consistent year over year; align inventory
   ordering and staffing schedules accordingly rather than reacting
   to each cycle after the fact.

## Methodology Note

All figures are computed directly from `sql/queries.sql` run against
`data/sales.db`. Revenue is calculated line-by-line as
`quantity × unit_price × (1 - discount)` throughout, rather than
stored as a precomputed column, since it depends on discount at time
of sale.
