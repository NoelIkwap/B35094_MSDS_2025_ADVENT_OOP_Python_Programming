from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Refugee(db.Model):
    __tablename__ = "refugees"

    individual_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    process_status = db.Column(db.String(20), nullable=False)  # Active / Closed
    individual_number = db.Column(db.String(20), nullable=False, unique=True)  # UGA-00000001
    family_group_number = db.Column(db.String(20), nullable=False)  # UGA-25-0000001

    full_name = db.Column(db.String(200), nullable=False)
    family_size = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)

    country_of_origin = db.Column(db.String(100), nullable=False)
    legal_status = db.Column(db.String(50), nullable=False)
    location_address = db.Column(db.String(100), nullable=False)

    date_of_birth = db.Column(db.String(20), nullable=False)
    registration_date = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<Refugee {self.individual_number}>"
