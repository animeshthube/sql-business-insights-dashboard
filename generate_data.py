"""
generate_data.py
Builds a realistic, normalized retail/e-commerce dataset for the SQL
Business Insights Dashboard project:
  customers(customer_id, customer_name, region, signup_date, segment)
  products(product_id, product_name, category, unit_price, unit_cost)
  orders(order_id, customer_id, order_date)
  order_items(item_id, order_id, product_id, quantity, unit_price, discount)

Spans 3 full years (2023-2025) so Year-over-Year growth analysis has
real data to work with. Includes intentional seasonality, region
variance, and a mix of high/low performing products for realistic
SQL analysis results.
"""
import csv
import random
from datetime import date, timedelta

random.seed(23)

OUT = "/home/claude/sql-business-insights-dashboard/data"

REGIONS = ["Northeast", "Midwest", "South", "West"]
REGION_MULT = {"West": 1.30, "Northeast": 1.20, "Midwest": 0.95, "South": 0.75}

CATEGORIES = {
    "Electronics": {"margin": (0.15, 0.28), "price": (25, 650)},
    "Home & Kitchen": {"margin": (0.20, 0.35), "price": (10, 300)},
    "Apparel": {"margin": (0.35, 0.55), "price": (12, 150)},
    "Beauty & Personal Care": {"margin": (0.30, 0.48), "price": (5, 90)},
    "Sports & Outdoors": {"margin": (0.18, 0.32), "price": (8, 400)},
}

PRODUCT_NAMES = {
    "Electronics": ["Wireless Earbuds", "4K Streaming Stick", "Portable SSD 1TB", "Smart Plug (4-Pack)",
                    "Bluetooth Speaker", "Phone Charger Cable", "Gaming Mouse", "Mechanical Keyboard",
                    "Tablet Stand", "Robot Vacuum", "Smart Doorbell", "Noise-Cancelling Headphones"],
    "Home & Kitchen": ["Air Fryer", "Coffee Maker", "Knife Set", "Non-Stick Pan Set", "Blender",
                       "Storage Bins (Set of 6)", "Bedding Set", "Throw Pillows (Pair)", "Table Lamp"],
    "Apparel": ["Men's Hoodie", "Women's Leggings", "Running Shoes", "Denim Jacket", "Graphic T-Shirt",
                "Wool Beanie", "Rain Jacket", "Athletic Socks (6-Pack)"],
    "Beauty & Personal Care": ["Face Moisturizer", "Shampoo & Conditioner Set", "Electric Toothbrush",
                               "Vitamin C Serum", "Hair Dryer", "Body Wash", "Sunscreen SPF50"],
    "Sports & Outdoors": ["Yoga Mat", "Adjustable Dumbbells", "Camping Chair", "Insulated Water Bottle",
                          "Bike Helmet", "Resistance Band Set", "Hiking Backpack", "Tennis Racket"],
}

FIRST_NAMES = ["Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Cameron", "Jamie", "Drew",
               "Skyler", "Reese", "Quinn", "Rowan", "Hayden", "Emerson", "Dakota", "Sage", "Finley",
               "Kendall", "Marlowe", "Sam", "Alex", "Priya", "Wei", "Fatima", "Diego", "Amara"]
LAST_NAMES = ["Bennett", "Ortiz", "Larsen", "Nakamura", "Fischer", "Adeyemi", "Kowalski", "Morales",
              "Whitfield", "Petrov", "Reyes", "Novak", "Hughes", "Delgado", "Berg", "Osei"]

SEGMENTS = ["New", "Returning", "VIP"]

START_DATE = date(2023, 1, 1)
END_DATE = date(2025, 12, 31)
N_DAYS = (END_DATE - START_DATE).days


def seasonality_factor(d):
    m = d.month
    if m in (11, 12):
        return 1.9
    if m == 1:
        return 1.2
    if m in (7, 8):
        return 0.80
    if m == 2:
        return 0.78
    return 1.0


def yearly_growth_factor(year):
    return {2023: 0.85, 2024: 1.0, 2025: 1.22}[year]


products = []
pid = 1
for cat, info in CATEGORIES.items():
    for name in PRODUCT_NAMES[cat]:
        price = round(random.uniform(*info["price"]), 2)
        margin = round(random.uniform(*info["margin"]), 3)
        cost = round(price * (1 - margin), 2)
        products.append({"product_id": f"PRD{pid:04d}", "product_name": name, "category": cat,
                          "unit_price": price, "unit_cost": cost})
        pid += 1

customers = []
for i in range(1, 261):
    # Most customers sign up early (business already has a base by 2023);
    # a smaller trickle of new signups continues through 2025.
    signup_offset = int(random.triangular(0, N_DAYS - 30, 0))
    signup = START_DATE + timedelta(days=signup_offset)
    region = random.choices(REGIONS, weights=[REGION_MULT[r] for r in REGIONS])[0]
    customers.append({
        "customer_id": f"CUST{i:04d}",
        "customer_name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        "region": region,
        "signup_date": signup.isoformat(),
        "segment": random.choices(SEGMENTS, weights=[30, 55, 15])[0],
    })

product_weight = {p["product_id"]: random.choice([0.3, 0.4, 0.6, 1.0, 1.2, 1.6, 2.2, 2.8]) for p in products}

orders = []
order_items = []
order_id_counter = 500000
item_id_counter = 1

n_target = 9000
for _ in range(n_target):
    offset = int(random.triangular(0, N_DAYS, N_DAYS * 0.7))
    d = START_DATE + timedelta(days=offset)
    season = seasonality_factor(d)
    growth = yearly_growth_factor(d.year)

    if random.random() > (season * growth) / 1.6:
        continue

    customer = random.choice(customers)
    if date.fromisoformat(customer["signup_date"]) > d:
        continue

    order_id_counter += 1
    order_id = f"ORD{order_id_counter}"
    orders.append({"order_id": order_id, "customer_id": customer["customer_id"], "order_date": d.isoformat()})

    n_items = random.choices([1, 2, 3, 4], weights=[50, 30, 15, 5])[0]
    weights = [product_weight[p["product_id"]] * REGION_MULT[customer["region"]] for p in products]
    chosen = random.choices(products, weights=weights, k=n_items)
    for product in chosen:
        qty = random.choices([1, 2, 3], weights=[70, 22, 8])[0]
        discount = random.choices([0, 0.10, 0.15, 0.20, 0.25], weights=[60, 18, 12, 6, 4])[0]
        order_items.append({
            "item_id": item_id_counter, "order_id": order_id, "product_id": product["product_id"],
            "quantity": qty, "unit_price": product["unit_price"], "discount": discount,
        })
        item_id_counter += 1

orders.sort(key=lambda o: o["order_date"])


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


write_csv(f"{OUT}/customers.csv", customers, ["customer_id", "customer_name", "region", "signup_date", "segment"])
write_csv(f"{OUT}/products.csv", products, ["product_id", "product_name", "category", "unit_price", "unit_cost"])
write_csv(f"{OUT}/orders.csv", orders, ["order_id", "customer_id", "order_date"])
write_csv(f"{OUT}/order_items.csv", order_items,
          ["item_id", "order_id", "product_id", "quantity", "unit_price", "discount"])

print(f"Wrote {len(orders)} orders, {len(order_items)} line items, "
      f"{len(customers)} customers, {len(products)} products -> data/")
