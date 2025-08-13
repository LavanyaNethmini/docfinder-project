#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# notifications.py (or inside your main Flask file)

import os
from flask import Blueprint, request, jsonify
from datetime import datetime
import mysql.connector
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def get_connection():
    return mysql.connector.connect(
        host="docfinder-docfinder.d.aivencloud.com",
        port=24448,
        user="avnadmin",
        password="AVNS_RQUukVzxF3liehSwMQS",
        database="defaultdb",  # or lost_found_db if that’s your DB name on Aiven
        ssl_ca="./api/ca.pem",  # path to Aiven's CA certificate (for SSL)
        ssl_verify_cert=True
    )

# Test connection
try:
    conn = get_connection()
    print("Connected to lost_found_db successfully!")
    conn.close()
except Exception as e:
    print("Connection failed:", e)


notifications_bp = Blueprint('notifications_bp', __name__)

@notifications_bp.route('/api/notification-requests', methods=['POST'])
def create_notification_request():
    data = request.get_json(silent=True) or request.form

    required = ['first_name','last_name','email','doc_type','doc_name']
    missing = [k for k in required if not data.get(k)]
    if missing:
        return jsonify({"ok": False, "message": f"Missing fields: {', '.join(missing)}"}), 400

    # Extract fields
    first_name     = data.get('first_name').strip()
    last_name      = data.get('last_name').strip()
    email          = data.get('email').strip().lower()
    phone          = (data.get('phone') or '').strip()
    doc_type       = data.get('doc_type').strip()
    doc_number     = (data.get('doc_number') or '').strip()
    doc_name       = data.get('doc_name').strip()
    lost_location  = (data.get('lost_location') or '').strip()
    lost_date      = data.get('lost_date') or None
    additional     = (data.get('additional_info') or '').strip()

    # Validate date if provided
    if lost_date:
        try:
            datetime.strptime(lost_date, "%Y-%m-%d")
        except ValueError:
            return jsonify({"ok": False, "message": "Invalid date format for lost_date (use YYYY-MM-DD)"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO notification_requests
        (first_name, last_name, email, phone, doc_type, doc_number, doc_name, lost_location, lost_date, additional_info)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (first_name, last_name, email, phone, doc_type, doc_number, doc_name, lost_location, lost_date, additional))
    conn.commit()

    return jsonify({"ok": True, "message": "Notification saved."}), 201


FROM_EMAIL = os.getenv("SMTP_FROM", "docfinder.notify@gmail.com")  # your verified sender
FRONTEND_CLAIM_URL = os.getenv("FRONTEND_CLAIM_URL", "https://yourdomain/claim.html")  # adjust

def send_email(to_email, subject, html_content):
    sg = SendGridAPIClient(api_key=os.environ["SENDGRID_API_KEY"])
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    sg.send(message)

def make_claim_email_html(seeker_name, doc_type_label, doc_name, doc_id):
    claim_url = f"{FRONTEND_CLAIM_URL}?doc_id={doc_id}"

    return f"""
    <div style="font-family:Segoe UI,Arial,sans-serif;max-width:600px;margin:auto;border:1px solid #eee;border-radius:12px;padding:24px;">
      <h2 style="color:#4361ee;margin-top:0;">Good news, {seeker_name}!</h2>
      <p>We’ve found a document in our database that matches your notification request.</p>
      <table style="width:100%;margin-top:12px;">
        <tr><td style="padding:4px 0;"><strong>Type:</strong> {doc_type_label}</td></tr>
        <tr><td style="padding:4px 0;"><strong>Name on Document:</strong> {doc_name}</td></tr>
      </table>
      <div style="margin:20px 0;">
        <a href="{claim_url}"
           style="background:#4361ee;color:#fff;text-decoration:none;padding:12px 18px;border-radius:8px;display:inline-block;">
           Make a Claim
        </a>
      </div>
      <p style="color:#555;">If the button doesn’t work, copy & paste this link into your browser:<br>
        <span style="color:#3f37c9;">{claim_url}</span>
      </p>
      <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
      <p style="font-size:12px;color:#888;">You received this because you asked DocFinder to notify you when a matching document is found.</p>
    </div>
    """

def label_for_doc_type(value):
    return {
        "id_card": "National ID Card",
        "passport": "Passport",
        "drivers_license": "Driver's License",
        "credit_card": "Credit/Debit Card",
        "certificate": "Certificate",
        "other": "Other"
    }.get(value, value)

def notify_seekers_for_found_doc(found_doc_id):
    """
    Call this AFTER you insert a new found document.
    Matching rules:
      - match seekers by document name (case-insensitive)
    """
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)

    # 1) Load the newly inserted found doc
    cur.execute("""
        SELECT id, doc_type, doc_name, location, reported_at
        FROM found_documents
        WHERE id = %s
    """, (found_doc_id,))
    found = cur.fetchone()
    if not found:
        print(f"No document found with id {found_doc_id}")
        return

    # 2) Match notification requests by doc_name (case-insensitive)
    cur.execute("""
        SELECT * FROM notification_requests
        WHERE status='active'
          AND LOWER(doc_name) LIKE CONCAT('%', LOWER(%s), '%')
    """, (found['doc_name'],))
    matches = cur.fetchall()

    if not matches:
        print(f"No active seekers matched for document: {found['doc_name']}")
    else:
        print(f"Found {len(matches)} seekers for document: {found['doc_name']}")

    # 3) Send emails & optionally mark as 'notified'
    for seeker in matches:
        print(f"Sending email to {seeker['email']} for document {found['doc_name']}")
        subject = "Your document may have been found — DocFinder"
        html = make_claim_email_html(
            seeker_name=f"{seeker['first_name']} {seeker['last_name']}",
            doc_type_label=label_for_doc_type(found['doc_type']),
            doc_name=found['doc_name'],
            doc_id=found['id']
        )
        try:
            send_email(seeker['email'], subject, html)
             print(f"Email sent to {seeker['email']}")
            cur.execute("UPDATE notification_requests SET status='notified' WHERE id=%s", (seeker['id'],))
            conn.commit()
        except Exception as e:
            print("Email error:", e)

    cur.close()
    conn.close()




