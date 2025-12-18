# app.py - Refugee Verification System (SQLite + SQLAlchemy)

from flask import Flask, render_template, request, jsonify, session, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pathlib import Path
import csv
import random
import logging


# Logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Flask App + DB

app = Flask(__name__)
app.secret_key = "super-secret-key"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "refugees.db"

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Refugee Model class

class Refugee(db.Model):
    __tablename__ = "refugees"

    individual_number = db.Column(db.String(20), primary_key=True)  # this is my PK
    process_status = db.Column(db.String(20))
    family_group_number = db.Column(db.String(20))
    full_name = db.Column(db.String(100))
    family_size = db.Column(db.Integer)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    country_of_origin = db.Column(db.String(50))
    legal_status = db.Column(db.String(20))
    location_address = db.Column(db.String(50))
    date_of_birth = db.Column(db.String(20))
    registration_date = db.Column(db.String(20))
    nssf_number = db.Column(db.String(20), nullable=True)


# Helpers

def get_case(individual_number):
    return Refugee.query.filter_by(individual_number=individual_number).first()

def generate_nssf():
    while True:
        n = f"NSSF{random.randint(100000, 999999)}"
        if not Refugee.query.filter_by(nssf_number=n).first():
            return n

def log_to_csv(refugee, nssf_number, action="ISSUED"):

    # Log NSSF issuance to CSV with timestamp

    data_dir = BASE_DIR / "data"
    data_dir.mkdir(exist_ok=True)
    csv_path = data_dir / "nssf_issuance_log.csv"
    
    headers = [
        "NSSF_Number", "Individual_Number", "Full_Name", "Age",
        "Legal_Status", "Country_Of_Origin", "Process_Status",
        "Action", "Timestamp"
    ]
    
    file_exists = csv_path.exists()
    
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        
        writer.writerow([
            nssf_number,
            refugee.individual_number,
            refugee.full_name,
            refugee.age,
            refugee.legal_status,
            refugee.country_of_origin,
            refugee.process_status,
            action,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])


# Vverification routes for ajax calls

@app.route("/verify-case", methods=["POST"])
def verify_case():
    """Endpoint for AJAX verification from JavaScript"""
    individual_number = request.form.get("INDIVIDUAL_ID", "").upper().strip()
    logger.info(f"verify-case called with: {individual_number}")
    
    # Search for the individual
    case = get_case(individual_number)
    
    if not case:
        logger.warning(f"Individual not found: {individual_number}")
        return jsonify({
            "success": False, 
            "message": f"Individual '{individual_number}' not found in database"
        })
    
    logger.info(f"Found: {case.individual_number}, Status: {case.process_status}, Legal: {case.legal_status}")
    
    # logic to ensure the app works as inteded
    # scenario 1: Active Refugee - Eligible for NSSF
    if case.process_status == "Active" and case.legal_status.lower() == "refugee":
        return jsonify({
            "success": True,
            "eligible": True,
            "message": "Individual is a Recognized Active Refugee in Uganda",
            "individual": {
                "individual_number": case.individual_number,
                "full_name": case.full_name,
                "family_group_number": case.family_group_number,
                "family_size": case.family_size,
                "age": case.age,
                "gender": case.gender,
                "country_of_origin": case.country_of_origin,
                "legal_status": case.legal_status,
                "location_address": case.location_address,
                "date_of_birth": case.date_of_birth,
                "registration_date": case.registration_date,
                "nssf_number": case.nssf_number
            }
        })
    
    # scenario 2: Process Status is Closed
    elif case.process_status == "Closed":
        return jsonify({
            "success": False,
            "eligible": False,
            "inactive": True,  # Flag to identify closed cases
            "message": "Individual is no longer a refugee in Uganda",
            "details": "Process Status is closed meaning they nolonger enjoy protection of the Ugandan governement."
        })
    
    # scenario 3: Active Asylum Seeker
    elif case.process_status == "Active" and "asylum" in case.legal_status.lower():
        return jsonify({
            "success": False,
            "eligible": False,
            "asylum_seeker": True,  # Flag to identify asylum seekers
            "message": "Case found",
            "details": "Individual is not yet eligible for NSSF Number because he is still an Asylum Seeker"
        })
    
    # scenario 4: Other cases
    else:
        status_message = f"Status: {case.process_status}, Legal: {case.legal_status}"
        return jsonify({
            "success": False,
            "eligible": False,
            "message": f"Case found but not eligible for NSSF",
            "details": status_message
        })
    
@app.route("/process-nssf", methods=["POST"])
def process_nssf():

    #Endpoint for issuing NSSF numbers from JavaScript

    individual_number = request.form.get("INDIVIDUAL_ID", "").upper().strip()
    logger.info(f"process-nssf called with: {individual_number}")
    
    case = get_case(individual_number)
    
    if not case:
        return jsonify({
            "success": False, 
            "message": "Individual not found"
        })
    
    # Check if already has NSSF
    if case.nssf_number:
        return jsonify({
            "success": False,
            "message": "NSSF number already issued",
            "nssf_number": case.nssf_number
        })
    
    # Check if individual is Active
    if case.process_status != "Active":
        return jsonify({
            "success": False, 
            "message": "Cannot issue NSSF: Individual is not Active"
        })
    
    # Check if individual is a Refugee (not Asylum Seeker)
    if case.legal_status.lower() != "refugee":
        return jsonify({
            "success": False, 
            "message": f"Cannot issue NSSF: Individual is {case.legal_status}, not a Refugee"
        })
    
    # Check if individual is a minor (below 18 years)
    if case.age < 18:
        return jsonify({
            "success": False,
            "minor": True,  # Flag to identify minor cases
            "message": "Individual is a Minor",
            "details": f"Age: {case.age} years. Cannot issue NSSF to individuals below 18 years."
        })
    
    # All checks passed -  assign NSSF number
    nssf_number = generate_nssf()
    case.nssf_number = nssf_number
    db.session.commit()
    
    # Log to CSV
    log_to_csv(case, nssf_number, "ISSUED")
    
    return jsonify({
        "success": True,
        "message": "NSSF number successfully issued",
        "nssf_number": nssf_number
    })


# more routes

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/verify", methods=["POST"])
def verify():
    individual_number = request.form.get("individual_number")
    case = get_case(individual_number)

    if not case:
        return jsonify({"success": False, "message": "No record found."})

    session["current_case"] = case.individual_number

    eligible_nssf = case.process_status == "Active" and case.legal_status == "Refugee"
    eligible_benefits = case.process_status == "Closed" and case.legal_status == "Refugee"

    return jsonify({
        "success": True,
        "redirect": f"/case/{individual_number}",
        "eligible_nssf": eligible_nssf,
        "eligible_benefits": eligible_benefits
    })

@app.route("/case/<individual_number>")
def case_details(individual_number):
    case = get_case(individual_number)
    if not case:
        flash("Case not found.", "error")
        return redirect("/")

    eligible_nssf = case.process_status == "Active" and case.legal_status == "Refugee"
    eligible_benefits = case.process_status == "Closed" and case.legal_status == "Refugee"

    return render_template(
        "case_details.html",
        case=case,
        eligible_nssf=eligible_nssf,
        eligible_benefits=eligible_benefits
    )

@app.route("/issue-nssf", methods=["POST"])
def issue_nssf():
    individual_number = session.get("current_case")
    case = get_case(individual_number)

    if not case:
        return jsonify({"success": False, "message": "No case loaded."})

    if case.nssf_number:
        return jsonify({"success": True, "message": f"Already issued: {case.nssf_number}"})

    nssf = generate_nssf()
    case.nssf_number = nssf
    case.process_status = "Closed"
    db.session.commit()

    log_to_csv([
        nssf, case.process_status, case.individual_number, case.legal_status,
        case.country_of_origin, "Verified", "Pending Benefits",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])

    return jsonify({"success": True, "message": f"NSSF issued: {nssf}", "nssf_number": nssf})

@app.route("/process-benefits", methods=["POST"])
def process_benefits():
    individual_number = session.get("current_case")
    case = get_case(individual_number)

    if not case:
        return jsonify({"success": False, "message": "Case not found."})

    case.process_status = "Benefits Processed"
    db.session.commit()

    log_to_csv([
        case.nssf_number, "Benefits Processed", case.individual_number,
        case.legal_status, case.country_of_origin,
        "Verified", "Cleared",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])

    return jsonify({"success": True, "message": "Benefits processed."})

# debug routes when they fail

@app.route("/debug/individuals")
def debug_individuals():

# Debug: List first 10 individuals

    individuals = Refugee.query.limit(10).all()
    result = []
    for ind in individuals:
        result.append({
            "individual_number": ind.individual_number,
            "full_name": ind.full_name,
            "process_status": ind.process_status,
            "legal_status": ind.legal_status,
            "nssf_number": ind.nssf_number
        })
    return jsonify(result)

@app.route("/debug/routes")
def debug_routes():

    # Debug: List all routes

    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": list(rule.methods),
            "path": rule.rule
        })
    return jsonify(routes)

# generate records

@app.route("/nssf-records", methods=["GET"])
def nssf_records():

    # Endpoint to get all NSSF issuance records

    try:
        # Get all refugees with issued NSSF numbers
        refugees_with_nssf = Refugee.query.filter(
            Refugee.nssf_number.isnot(None)
        ).all()
        
        records = []
        for refugee in refugees_with_nssf:

            # Try to get issue date from CSV log
            issue_date = None
            try:
                csv_path = BASE_DIR / "data" / "verification_status.csv"
                if csv_path.exists():
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row.get('NSSF_Number') == refugee.nssf_number:
                                issue_date = row.get('Date_Updated')
                                break
            except:
                pass
            
            records.append({
                'nssf_number': refugee.nssf_number,
                'individual_number': refugee.individual_number,
                'full_name': refugee.full_name,
                'age': refugee.age,
                'process_status': refugee.process_status,
                'legal_status': refugee.legal_status,
                'issue_date': issue_date,
                'country_of_origin': refugee.country_of_origin
            })
        
        return jsonify({
            'success': True,
            'count': len(records),
            'records': records
        })
        
    except Exception as e:
        logger.error(f"Error fetching NSSF records: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error fetching records: {str(e)}'
        })
    
@app.route("/health")
def health():
    """Health check"""
    return jsonify({"status": "ok", "message": "Flask is running"})


# Initialization

if __name__ == "__main__":
    
    # Create DB if missing
    if not DB_PATH.exists():
        with app.app_context():
            db.create_all()
            logger.info("Database created.")
    
    # Print routes on startup
    with app.app_context():
        print("\n" + "="*50)
        print("AVAILABLE ROUTES:")
        print("="*50)
        for rule in app.url_map.iter_rules():
            print(f"{rule.rule} -> {rule.endpoint}")
        print("="*50 + "\n")

    app.run(debug=True, host="0.0.0.0", port=5000)