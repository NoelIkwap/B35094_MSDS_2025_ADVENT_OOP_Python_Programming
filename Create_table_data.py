import random
from datetime import datetime, timedelta
from faker import Faker
from flask import Flask
from models import db, Refugee

fake = Faker()

# Allowed values
PROCESS_STATUS = ["Active", "Closed"]
GENDERS = ["Male", "Female"]
LEGAL_STATUS = ["Refugee", "Asylum Seeker"]

COUNTRIES = [
    "South Sudan", "Democratic Republic of Congo", "Eritrea", "Ethiopia",
    "Rwanda", "Burundi", "Kenya", "Malawi", "Egypt", "Sudan", "Somalia",
    "Tanzania", "Uganda", "Chad"
]

DISTRICTS = [
    "Kampala", "Mbale", "Lira", "Soroti", "Arua",
    "Mbarara", "Gulu", "Fort Portal", "Masaka", "Jinja"
]


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///refugee.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app


def generate_individual_number(n):
    return f"UGA-{str(n).zfill(8)}"


def generate_family_group_number(year, n):
    return f"UGA-{str(year)[2:]}-{str(n).zfill(7)}"


def calculate_dob(age):
    today = datetime.today()
    birth_date = today - timedelta(days=age * 365)
    return birth_date.strftime("%Y-%m-%d")


def random_registration_date():
    start = datetime(2005, 1, 1)
    end = datetime(2024, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    date = start + timedelta(days=random_days)
    return date.strftime("%Y-%m-%d")


app = create_app()

def insert_random_data(records=50):
    with app.app_context():

        for n in range(1, records + 1):
            # Random values
            age = random.randint(12, 90)
            family_size = random.randint(1, 12)
            registration_year = random.randint(2005, 2024)

            refugee = Refugee(
                process_status=random.choice(PROCESS_STATUS),
                individual_number=generate_individual_number(n),
                family_group_number=generate_family_group_number(registration_year, n),

                full_name=fake.name(),
                family_size=family_size,
                age=age,
                gender=random.choice(GENDERS),

                country_of_origin=random.choice(COUNTRIES),
                legal_status=random.choice(LEGAL_STATUS),
                location_address=random.choice(DISTRICTS),

                date_of_birth=calculate_dob(age),
                registration_date=random_registration_date()
            )

            db.session.add(refugee)

        db.session.commit()
        print(f"✅ Successfully inserted {records} refugee records into refugee.db!")

if __name__ == "__main__":
    insert_random_data(200)  # insert 200 records (change number as needed)
