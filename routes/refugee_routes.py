# refugee routes

from flask import request, jsonify, session
from models import db, Refugee
import random
from datetime import datetime

def generate_nssf_number():

    # Generate a unique NSSF number
    existing = [r.nssf_number for r in Refugee.query.filter(Refugee.nssf_number.isnot(None)).all()]
    while True:
        nssf = f"NSSF{random.randint(100000, 999999)}"
        if nssf not in existing:
            return nssf

@app.route('/verify-case', methods=['POST'])
def verify_case_route():

    # Verify case and optionally issue NSSF
    individual_number = request.form.get('individual_id', '').strip()
    action = request.form.get('action', 'verify')

    if not individual_number:
        return jsonify({'success': False, 'message': 'Individual ID is required'})

    refugee = Refugee.query.filter_by(individual_number=individual_number).first()
    if not refugee:
        return jsonify({'success': False, 'message': f'No case found with ID: {individual_number}'})

    process_status = refugee.process_status
    legal_status = refugee.legal_status

    # Eligible for NSSF: Active + Refugee
    if process_status == 'Active' and legal_status == 'Refugee':
        if action == 'issue_nssf':
            nssf_number = generate_nssf_number()
            refugee.nssf_number = nssf_number
            refugee.process_status = 'Closed'
            refugee.last_updated = datetime.now()
            db.session.commit()
            return jsonify({
                'success': True,
                'message': f'NSSF Number {nssf_number} issued successfully!',
                'nssf_number': nssf_number,
                'redirect': '/'
            })
        else:
            refugee.last_updated = datetime.now()
            db.session.commit()
            return jsonify({'success': True, 'message': 'Case verified successfully!', 'prompt_issue': True})

    # Eligible for benefits: Closed + Refugee
    elif process_status == 'Closed' and legal_status == 'Refugee':
        if action == 'benefits':
            refugee.process_status = 'Benefits Processed'
            refugee.last_updated = datetime.now()
            db.session.commit()
            return jsonify({'success': True, 'message': 'Benefits processed successfully!', 'redirect': '/'})
        else:
            return jsonify({'success': False, 'message': 'Case is eligible for benefits processing only.'})

    # Case not eligible
    else:
        refugee.process_status = 'Rejected'
        refugee.last_updated = datetime.now()
        db.session.commit()
        reason = f"Process status: {process_status}, Legal status: {legal_status}"
        return jsonify({'success': False, 'message': f'Case rejected: {reason}', 'reason': reason})

@app.route('/issue-nssf', methods=['POST'])
def issue_nssf():
    """Directly issue NSSF for a verified case."""
    individual_number = request.form.get('individual_id', '').strip()
    refugee = Refugee.query.filter_by(individual_number=individual_number).first()
    if not refugee:
        return jsonify({'success': False, 'message': f'Case not found: {individual_number}'})

    if refugee.nssf_number:
        return jsonify({'success': True, 'message': f'NSSF already exists: {refugee.nssf_number}', 'nssf_number': refugee.nssf_number})

    nssf_number = generate_nssf_number()
    refugee.nssf_number = nssf_number
    refugee.process_status = 'Closed'
    refugee.last_updated = datetime.now()
    db.session.commit()

    return jsonify({'success': True, 'message': f'NSSF Number {nssf_number} issued successfully!', 'nssf_number': nssf_number, 'redirect': '/'})
