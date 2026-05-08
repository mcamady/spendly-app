import random
import string
from datetime import datetime
from database.db import get_user_by_email, create_user

first_names = [
    "Aarav", "Vihaan", "Aryan", "Aditya", "Rohan", "Karan", "Siddharth",
    "Ananya", "Aisha", "Priya", "Kavya", "Sneha", "Maya", "Ishita",
    "Ravi", "Vijay", "Mahesh", "Sanjay",
]

last_names = [
    "Sharma", "Patel", "Kumar", "Singh", "Gupta", "Reddy", "Nair", "Chopra",
    "Mehta", "Verma", "Joshi", "Desai", "Bhatia", "Ghosh",
]

def generate_email(name):
    # name format: First Last
    first, last = name.lower().split()
    suffix = "".join(random.choices(string.digits, k=random.choice([2,3])))
    return f"{first}.{last}{suffix}@gmail.com"

def generate_user():
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    email = generate_email(name)
    password = "password123"
    return name, email, password

while True:
    name, email, password = generate_user()
    if not get_user_by_email(email):
        break

user_id = create_user(name, email, password)
print(f"User created: id={user_id}, name={name}, email={email}")
