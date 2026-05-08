import os
import random
from werkzeug.security import generate_password_hash

# Add parent directory to path to import database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_db, get_user_by_email


def generate_name():
    first_names = ["Rahul", "Amit", "Sanjay", "Vikram", "Manish", "Rohan", "Arjun", "Deepak", "Karan", "Ramesh", "Ankit", "Prakash", "Sanjay", "Vijay", "Nilesh", "Siddharth"]
    last_names = ["Sharma", "Patel", "Singh", "Kumar", "Reddy", "Nair", "Gupta", "Chaudhary", "Joshi", "Verma", "Desai", "Mehta", "Bhatia", "Iyer", "Ghosh"]
    return random.choice(first_names), random.choice(last_names)


def generate_email(first, last):
    num = random.randint(10, 999)
    return f"{first.lower()}.{last.lower()}{num}@gmail.com"


def main():
    # generate a unique email
    while True:
        first, last = generate_name()
        name = f"{first} {last}"
        email = generate_email(first, last)
        if not get_user_by_email(email):
            break
    password_hash = generate_password_hash("password123")
    # Insert using same pattern as db.py
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, password_hash),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    print(f"User created: id={user_id}, name={name}, email={email}")

if __name__ == "__main__":
    main()
