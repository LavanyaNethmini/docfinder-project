#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Blueprint, Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import jwt, datetime
from werkzeug.security import generate_password_hash, check_password_hash

claim_bp = Blueprint('claims', __name__)

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="docfinder-docfinder.d.aivencloud.com",
        port=24448,
        user="avnadmin",
        password="AVNS_RQUukVzxF3liehSwMQS",
        database="defaultdb",  # or lost_found_db if that’s your DB name on Aiven
        ssl_ca="C:/wamp64/www/lost-found/api/ca.pem",  # path to Aiven's CA certificate (for SSL)
        ssl_verify_cert=True
    )


# Test connection
try:
    conn = get_connection()
    print("Connected to lost_found_db successfully!")
    conn.close()
except Exception as e:
    print("Connection failed:", e)


# In[2]:


@claim_bp.route('/api/submit-claim', methods=['POST'])
def submit_claim():
    doc_id = request.form.get('doc_id')
    claimer_name = request.form.get('claimant_name')
    contact_info = request.form.get('claimant_email')
    claimant_nic = request.form.get('claimant_nic')

    conn = get_connection()
    cursor = conn.cursor()

    # Insert into claims table
    cursor.execute("""
        INSERT INTO claim_requests (document_id, claimant_name, claimant_nic, claimant_email, requested_at, status)
        VALUES (%s, %s, %s, NOW(), 'Pending')
    """, (doc_id, claimer_name, contact_info)) document_id 

    conn.commit()
    cursor.close()
    conn.close()

    return "Claim submitted successfully!"


# In[ ]:


@claim_bp.rout('/api/claim/<int_id>', mrthods=['GET'])
def claim(doc_id):
    conn = get_connection()
    cursor = conn.cursor() 

    cursor.execute("SELECT * FROM documnets WHERE Did =%s" , (doc_id))
    document = cursor.fetchone()

    cursor.close()
    conn.close()

if not document:
    return "Document not found", 404

return render_template(claim.html, document==document)




