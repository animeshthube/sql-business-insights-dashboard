import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

BASE = "/home/claude/sql-business-insights-dashboard"
OUT = f"{BASE}/screenshots"
conn = sqlite3.connect(f"{BASE}/data/sales.db")
cur = conn.cursor()

TEAL = "#0F766E"; CORAL = "#C2410C"; INDIGO = "#4338CA"; SLATE = "#475569"; AMBER = "#B45309"
PALETTE = [TEAL, INDIGO, AMBER, CORAL, SLATE, "#7C3AED"]

plt.rcParams.update({
    "font.size": 11, "axes.edgecolor": "#444444", "axes.labelcolor": "#1F2937",
    "text.color": "#1F2937", "xtick.color": "#444444", "ytick.color": "#444444",
})

# ---------- Monthly revenue with running total ----------
rows = cur.execute("""
    SELECT strftime('%Y-%m', o.order_date) AS month,
           ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2)
    FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY month ORDER BY month
""").fetchall()
months = [r[0] for r in rows]
revenue = [r[1] for r in rows]
dates = [datetime.strptime(m, "%Y-%m") for m in months]

fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(dates, revenue, color=TEAL, linewidth=2.2)
ax.fill_between(dates, revenue, alpha=0.1, color=TEAL)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
fig.autofmt_xdate(rotation=45)
ax.set_title("Monthly Revenue", fontsize=14, fontweight="bold")
ax.set_ylabel("Revenue ($)")
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
plt.tight_layout(); plt.savefig(f"{OUT}/monthly_revenue.png", dpi=150); plt.close()

# ---------- Sales by region ----------
rows = cur.execute("""
    SELECT c.region, ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2)
    FROM customers c JOIN orders o ON o.customer_id=c.customer_id
    JOIN order_items oi ON oi.order_id=o.order_id
    GROUP BY c.region ORDER BY 2 DESC
""").fetchall()
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.bar([r[0] for r in rows], [r[1] for r in rows], color=PALETTE[:len(rows)])
ax.set_title("Sales by Region", fontsize=13, fontweight="bold")
ax.set_ylabel("Revenue ($)")
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
plt.tight_layout(); plt.savefig(f"{OUT}/sales_by_region.png", dpi=150); plt.close()

# ---------- Top 10 customers ----------
rows = cur.execute("""
    SELECT c.customer_name, ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) rev
    FROM customers c JOIN orders o ON o.customer_id=c.customer_id
    JOIN order_items oi ON oi.order_id=o.order_id
    GROUP BY c.customer_id HAVING COUNT(DISTINCT o.order_id) >= 2
    ORDER BY rev DESC LIMIT 10
""").fetchall()
fig, ax = plt.subplots(figsize=(8, 5.5))
names = [r[0] for r in rows][::-1]; vals = [r[1] for r in rows][::-1]
bars = ax.barh(names, vals, color=INDIGO)
ax.set_title("Top 10 Customers by Revenue", fontsize=13, fontweight="bold")
ax.set_xlabel("Revenue ($)")
for bar, v in zip(bars, vals):
    ax.text(bar.get_width() + max(vals)*0.01, bar.get_y()+bar.get_height()/2, f"${v:,.0f}", va='center', fontsize=9)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
plt.tight_layout(); plt.savefig(f"{OUT}/top_customers.png", dpi=150); plt.close()

# ---------- Product performance tiers ----------
rows = cur.execute("""
    SELECT p.product_name, ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) rev
    FROM products p JOIN order_items oi ON oi.product_id=p.product_id
    GROUP BY p.product_id ORDER BY rev DESC LIMIT 10
""").fetchall()
fig, ax = plt.subplots(figsize=(8, 5.5))
names = [r[0] for r in rows][::-1]; vals = [r[1] for r in rows][::-1]
bars = ax.barh(names, vals, color=TEAL)
ax.set_title("Top 10 Products by Revenue", fontsize=13, fontweight="bold")
ax.set_xlabel("Revenue ($)")
for bar, v in zip(bars, vals):
    ax.text(bar.get_width() + max(vals)*0.01, bar.get_y()+bar.get_height()/2, f"${v:,.0f}", va='center', fontsize=9)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
plt.tight_layout(); plt.savefig(f"{OUT}/top_products.png", dpi=150); plt.close()

# ---------- Customer purchase frequency segmentation ----------
rows = cur.execute("""
    SELECT frequency_tier, COUNT(*), ROUND(AVG(total_revenue),2) FROM (
      SELECT c.customer_id,
             COUNT(DISTINCT o.order_id) oc,
             SUM(oi.quantity*oi.unit_price*(1-oi.discount)) total_revenue,
             CASE WHEN COUNT(DISTINCT o.order_id)=1 THEN 'One-Time'
                  WHEN COUNT(DISTINCT o.order_id) BETWEEN 2 AND 4 THEN 'Occasional'
                  ELSE 'Frequent' END AS frequency_tier
      FROM customers c JOIN orders o ON o.customer_id=c.customer_id
      JOIN order_items oi ON oi.order_id=o.order_id
      GROUP BY c.customer_id
    ) t GROUP BY frequency_tier
""").fetchall()
fig, ax = plt.subplots(1, 2, figsize=(10, 4.5))
labels = [r[0] for r in rows]; counts = [r[1] for r in rows]; avgrev = [r[2] for r in rows]
ax[0].pie(counts, labels=labels, autopct='%1.0f%%', colors=PALETTE[:len(rows)],
          wedgeprops={'width':0.42,'edgecolor':'white','linewidth':2})
ax[0].set_title("Customers by Frequency Tier", fontsize=12, fontweight="bold")
ax[1].bar(labels, avgrev, color=PALETTE[:len(rows)])
ax[1].set_title("Avg Revenue per Customer", fontsize=12, fontweight="bold")
ax[1].spines['top'].set_visible(False); ax[1].spines['right'].set_visible(False)
plt.tight_layout(); plt.savefig(f"{OUT}/customer_frequency.png", dpi=150); plt.close()

# ---------- YoY growth ----------
rows = cur.execute("""
    WITH yearly AS (
      SELECT strftime('%Y', o.order_date) yr, SUM(oi.quantity*oi.unit_price*(1-oi.discount)) rev
      FROM orders o JOIN order_items oi ON oi.order_id=o.order_id GROUP BY yr
    )
    SELECT yr, ROUND(rev,2) FROM yearly ORDER BY yr
""").fetchall()
fig, ax = plt.subplots(figsize=(6.5, 4.5))
colors_yoy = [SLATE, TEAL, TEAL]
bars = ax.bar([r[0] for r in rows], [r[1] for r in rows], color=colors_yoy[:len(rows)])
ax.set_title("Annual Revenue", fontsize=13, fontweight="bold")
ax.set_ylabel("Revenue ($)")
for bar, r in zip(bars, rows):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()*1.01, f"${r[1]:,.0f}", ha='center', fontsize=9)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
plt.tight_layout(); plt.savefig(f"{OUT}/annual_revenue.png", dpi=150); plt.close()

print("All charts saved to screenshots/")
