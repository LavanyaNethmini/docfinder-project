#!/usr/bin/env python
# coding: utf-8

from flask import Blueprint, request, jsonify, render_template
import mysql.connector
from datetime import datetime

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
@claim_bp.route("/api/submit-claim", methods=["POST"])
def submit_claim():
    conn = get_connection()
    cur = conn.cursor()
    try:
        document_id = request.form.get("document_id")
        name = request.form.get("claimant_name")
        nic = request.form.get("claimant_nic")
        email = request.form.get("claimant_email")

        cur.execute("""
            INSERT INTO claim_requests (document_id, claimant_name, claimant_nic, claimant_email, status, requested_at)
            VALUES (%s, %s, %s, %s, 'pending', %s)
        """, (document_id, name, nic, email, datetime.now()))
        
        claim_id = cur.lastrowid 

        cur.execute("""
            SELECT contact_name, contact_email, contact_phone, anonymous
            FROM found_documents
            WHERE id = %s
        """, (document_id,))
        founder = cur.fetchone()
        conn.commit()

    finally:
        cur.close()
        conn.close()

    if founder:
        founder_data = {
            "name": founder[0],
            "email": founder[1],
            "phone": founder[2],
            "anonymous": founder[3]
        }
    else:
        founder_data = None

    return jsonify({
        "claim_id": claim_id,
        "founder": founder_data
    })

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
