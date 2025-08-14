#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Blueprint, request, jsonify
import mysql.connector
from datetime import datetime

contact_bp = Blueprint('contact_bp', __name__)

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your-secret-key'

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3308,
        user="root",
        password="",
        database="lost_found_db"
    )

# Test connection
try:
    conn = get_connection()
    print("Connected to lost_found_db successfully!")
    conn.close()
except Exception as e:
    print("Connection failed:", e)

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

