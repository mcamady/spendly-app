import sys
import random
from datetime import datetime, timedelta
from database.db import get_db

def usage():
    print("Usage: /seed-expenses <user_id> <count> <months>")
    print("Example: /seed-expenses 1 50 6")

# Parse arguments
if len(sys.argv) != 4:
    usage()
    sys.exit(1)

try:
    user_id = int(sys.argv[1])
    count = int(sys.argv[2])
    months = int(sys.argv[3])
except ValueError:
    usage()
    sys.exit(1)

# Verify user exists
conn = get_db()
user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
if not user:
    print(f"No user found with id {user_id}.")
    conn.close()
    sys.exit(1)

categories = [
    ("Food", 50, 800),
    ("Transport", 20, 500),
    ("Bills", 200, 3000),
    ("Health", 100, 2000),
    ("Entertainment", 100, 1500),
    ("Shopping", 200, 5000),
    ("Other", 50, 1000),
]

# Weight categories: Food most common, Health/Entertainment least
weights = [0.30, 0.15, 0.20, 0.05, 0.05, 0.15, 0.10]

now = datetime.now()
start_date = now - timedelta(days=months * 30)

exp_records = []
for _ in range(count):
    cat, lo, hi = random.choices(categories, weights=weights, k=1)[0]
    amount = round(random.uniform(lo, hi), 2)
    # Random date between start_date and now
    rand_days = random.randint(0, (now - start_date).days)
    expense_date = (start_date + timedelta(days=rand_days)).date().isoformat()
    description = f"Random {cat.lower()} expense"
    exp_records.append((user_id, amount, cat, expense_date, description))

# Insert in a transaction
try:
    with conn:
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            exp_records,
        )
except Exception as e:
    print(f"Failed to insert expenses: {e}")
    conn.close()
    sys.exit(1)

# Fetch inserted rows to confirm
cursor = conn.execute(
    "SELECT id, amount, category, date, description FROM expenses WHERE user_id = ? ORDER BY id DESC LIMIT 5",
    (user_id,)
)
sample = cursor.fetchall()

# Determine date range
dates = [rec[3] for rec in exp_records]
min_date = min(dates)
max_date = max(dates)

print(f"Inserted {count} expenses for user {user_id}.")
print(f"Date range: {min_date} to {max_date}")
print("Sample inserted records (most recent 5):")
for row in sample:
    print(dict(row))

conn.close()
