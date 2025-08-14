#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Blueprint, request, jsonify
import mysql.connector
from datetime import datetime

contact_bp = Blueprint('contact_bp', __name__)

def get_connection():
    return mysql.connector.connect(
        host="localhost",  # or your Railway DB host
        user="root",
        password="yourpassword",
        database="docfinder"
    )

@contact_bp.route('/api/contact', methods=['POST'])
def save_contact_message():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    if not name or not email or not message:
        return jsonify({"error": "All fields are required"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO contact_messages (name, email, message)
        VALUES (%s, %s, %s)
    """, (name, email, message))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Message saved successfully!"}), 201

