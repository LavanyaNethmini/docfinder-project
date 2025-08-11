#!/usr/bin/env python
# coding: utf-8

from flask import Blueprint, request, jsonify, render_template
import mysql.connector

claim_bp = Blueprint('claims', __name__)

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="docfinder-docfinder.d.aivencloud.com",
        port=24448,
        user="avnadmin",
        password="AVNS_RQUukVzxF3liehSwMQS",
        database="defaultdb",  # or your Aiven DB name
        ssl_ca="./api/ca.pem",  # path to Aiven's CA
        ssl_verify_cert=True
    )

# ------------------------------
# POST: Submit a claim request
# ------------------------------
@claim_bp.route('/api/submit-claim', methods=['POST'])
def submit_claim():
    doc_id = request.form.get('doc_id')
    claimer_name = request.form.get('claimant_name')
    contact_info = request.form.get('claimant_email')
    claimant_nic = request.form.get('claimant_nic')

    if not (doc_id and claimer_name and contact_info and claimant_nic):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO claim_requests (document_id, claimant_name, claimant_nic, claimant_email, requested_at, status)
        VALUES (%s, %s, %s, %s, NOW(), 'Pending')
    """, (doc_id, claimer_name, claimant_nic, contact_info))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Claim submitted successfully!"})

# ------------------------------
# GET: View claim form for a document
# ------------------------------
@claim_bp.route('/api/claim/<int:doc_id>', methods=['GET'])
def claim(doc_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM found_documents  WHERE id = %s", (doc_id,))
    document = cursor.fetchone()

    cursor.close()
    conn.close()

    if not document:
        return "Document not found", 404

    return render_template("Claim.html", document=document)
