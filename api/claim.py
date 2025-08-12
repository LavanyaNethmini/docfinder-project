#!/usr/bin/env python
# coding: utf-8

import os
import smtplib
import ssl
from email.message import EmailMessage
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import Blueprint, request, jsonify, render_template
import mysql.connector
from datetime import datetime

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM = os.getenv("SMTP_FROM", "docfinder.notify@gmail.com")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "True").lower() in ("1", "true", "yes")

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


@claim_bp.route("/api/send-request", methods=["POST"])
def send_request_email():
    data = request.get_json() or {}
    claim_id = data.get("claim_id")
    document_id = data.get("document_id")

    if not claim_id or not document_id:
        return jsonify({"error": "Missing claim_id or document_id"}), 400

    conn = get_connection()
    cur = conn.cursor()
    try:
        print(f"Received claim_id={claim_id}, document_id={document_id}")
        # Fetch founder details
        cur.execute("""
            SELECT  contact_name, contact_email, anonymous
            FROM found_documents
            WHERE id = %s
        """, (document_id,))
        founder = cur.fetchone()
        if not founder:
            print("Founder not found")
            return jsonify({"error": "Founder not found"}), 404

        contact_name, contact_email, anonymous = founder
        print(f"Founder: {contactr_name}, {contact_email}, anonymous={anonymous}")
        if anonymous:
            print("Founder is anonymous - aborting")
            return jsonify({"error": "Founder is anonymous"}), 403

        # Fetch claimant details
        cur.execute("""
            SELECT claimant_name, claimant_email
            FROM claim_requests
            WHERE id = %s
        """, (claim_id,))
        claim_row = cur.fetchone()
        if not claim_row:
            print("Claim request not found")
            return jsonify({"error": "Claim request not found"}), 404

        claimant_name, claimant_email = claim_row

        # Compose email
        msg = EmailMessage()
        msg["Subject"] = f"DocFinder: Claim request for document #{document_id}"
        msg["From"] = SMTP_FROM
        msg["To"] = contact_email

        text_body = f"""Hello {contact_name},

A user has requested to claim a document you found (Document ID: {document_id}).

Claimant:
    Name: {claimant_name}
    Email: {claimant_email}

Please reply to this email or contact the claimant directly.

Thanks,
DocFinder Team
"""
        html_body = f"""
        <p>Hello {contact_name},</p>
        <p>A user has requested to claim a document you found (Document ID: <strong>{document_id}</strong>).</p>
        <p><strong>Claimant</strong><br/>
            Name: {claimant_name}<br/>
            Email: {claimant_email}
        </p>
        <p>Please reply to this email or contact the claimant directly.</p>
        <p>— DocFinder</p>
        """

        msg.set_content(text_body)
        msg.add_alternative(html_body, subtype="html")

        # Send email via SMTP
        context = ssl.create_default_context()
        if SMTP_USE_TLS and SMTP_PORT == 587:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
        else:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)

        # Optional: update claim status
        cur.execute("""
            UPDATE claim_requests SET status = 'requested'
            WHERE id = %s
        """, (claim_id,))
        conn.commit()

        return jsonify({"status": "ok", "message": "Request email sent"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()


