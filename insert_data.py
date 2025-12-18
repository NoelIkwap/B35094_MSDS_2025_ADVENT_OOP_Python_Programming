import sqlite3
import random
from faker import Faker
from datetime import date

fake = Faker()

DB_FILE = "refugees.db"
NUM_RECORDS = 10000  # for purposes of exam i only created 10,000 but can adjust

# Connect to SQLite
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# table should exists with only these required columns
cursor.execute("""
CREATE TABLE IF NOT EXISTS refugees (
    individual_number TEXT PRIMARY KEY,
    process_status TEXT,
    family_group_number TEXT,
    full_name TEXT,
    family_size INTEGER,
    age INTEGER,
    gender TEXT,
    country_of_origin TEXT,
    legal_status TEXT,
    location_address TEXT,
    date_of_birth TEXT,
    registration_date TEXT
)
""")
conn.commit()


def generate_refugee(seq_num):
    registration_year = random.randint(2020, 2025)
    process_status = random.choice(["Active", "Closed"])

    # Registration date as a date object
    start = date(registration_year, 1, 1)
    end = date(registration_year, 12, 31)
    registration_date = fake.date_between(start_date=start, end_date=end).strftime("%Y-%m-%d")

    # Family group number format: UGA-YY-XXXXXXX
    family_group_number = f"UGA-{str(registration_year)[-2:]}-{seq_num:07d}"

    individual_number = f"UGA-{random.randint(10000000, 99999999)}"
    full_name = fake.name()
    family_size = random.randint(1, 10)
    age = random.randint(1, 80)
    gender = random.choice(["Male", "Female"])
    country_of_origin = random.choice(["Pakistan", "DR Congo", "South Sudan", "Rwanda", "Burundi"])
    legal_status = random.choice(["Refugee", "Asylum Seeker"])
    location_address = fake.city()
    date_of_birth = fake.date_of_birth(minimum_age=1, maximum_age=80).strftime("%Y-%m-%d")

    return (
        individual_number, process_status, family_group_number, full_name,
        family_size, age, gender, country_of_origin, legal_status,
        location_address, date_of_birth, registration_date
    )


# Insert records
batch_size = 500  # Insert in batches for efficiency
records = []

for i in range(1, NUM_RECORDS + 1):
    records.append(generate_refugee(i))
    if i % batch_size == 0:
        cursor.executemany("""
            INSERT INTO refugees (
                individual_number, process_status, family_group_number, full_name,
                family_size, age, gender, country_of_origin, legal_status,
                location_address, date_of_birth, registration_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, records)
        conn.commit()
        print(f"{i} records inserted...")
        records = []

# Insert remaining records
if records:
    cursor.executemany("""
        INSERT INTO refugees (
            individual_number, process_status, family_group_number, full_name,
            family_size, age, gender, country_of_origin, legal_status,
            location_address, date_of_birth, registration_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, records)
    conn.commit()
    print(f"{NUM_RECORDS} records inserted successfully!")

conn.close()
print("Done!")
