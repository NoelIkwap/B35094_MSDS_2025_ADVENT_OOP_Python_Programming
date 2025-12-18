from flask import Blueprint, request, jsonify
from models import Refugee, db
from datetime import datetime

verification_bp = Blueprint('verification', __name__)


# Verify Individual Case

@verification_bp.route('/verify-case', methods=['POST'])
def verify_case():
    individual_number = request.form.get('INDIVIDUAL_ID', '').upper()

    refugee = Refugee.query.filter_by(individual_number=individual_number).first()
    if not refugee:
        return jsonify({'success': False, 'message': 'Individual not found'})

    if refugee.process_status == 'Active' and refugee.legal_status in ['Refugee', 'Asylum seeker']:
        # Return success with personal info
        return jsonify({
            'success': True,
            'message': 'Individual is a Recognized Active Refugee in Uganda',
            'show_info': True,
            'individual': {
                'individual_number': refugee.individual_number,
                'full_name': refugee.full_name,
                'family_group_number': refugee.family_group_number,
                'family_size': refugee.family_size,
                'age': refugee.age,
                'gender': refugee.gender,
                'country_of_origin': refugee.country_of_origin,
                'legal_status': refugee.legal_status,
                'location_address': refugee.location_address,
                'date_of_birth': refugee.date_of_birth,
                'registration_date': refugee.registration_date,
                'nssf_number': refugee.nssf_number
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Individual found but not an Active Refugee'})



# Generate NSSF Number

def generate_nssf_number(individual_number):
    """
    Generates a unique NSSF number based on individual_number and timestamp.
    Format: NSSF-YYYYMMDD-HHMMSS-XXXX
    """
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_suffix = individual_number[-4:]  # last 4 digits
    return f"NSSF-{now}-{unique_suffix}"



# Process NSSF issuance

@verification_bp.route('/process-nssf', methods=['POST'])
def process_nssf():
    individual_number = request.form.get('INDIVIDUAL_ID', '').upper()
    refugee = Refugee.query.filter_by(individual_number=individual_number).first()

    if not refugee:
        return jsonify({'success': False, 'message': 'Individual not found'})

    if refugee.nssf_number:
        return jsonify({
            'success': False,
            'message': 'NSSF number already issued',
            'nssf_number': refugee.nssf_number
        })

    if refugee.process_status != 'Active':
        return jsonify({'success': False, 'message': 'Cannot issue NSSF: Individual is not Active'})

    # Generate and assign NSSF
    nssf_number = generate_nssf_number(individual_number)
    refugee.nssf_number = nssf_number
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'NSSF number successfully issued',
        'nssf_number': nssf_number
    })
