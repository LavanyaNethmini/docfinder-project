#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Blueprint, Flask, request, jsonify
from flask import current_app
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import mysql.connector
from .notifications import notify_seekers_for_found_doc  # adjust import to match your structure

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/api/report_found', methods=['POST'])
def report_found():
    conn = None
    cursor = None

    try:
        # Validate required fields
        required_fields = ['doc_name', 'doc_type', 'location']
        for field in required_fields:
            if field not in request.form or not request.form[field].strip():
                return jsonify({"success": False, "message": f"Missing required field: {field}"}), 400

        # Get form data
        doc_name = request.form['doc_name'].strip()
        doc_type = request.form['doc_type'].strip()
        location = request.form['location'].strip()
        contact_name = request.form.get('contact_name', '').strip()
        contact_email = request.form.get('contact_email', '').strip()
        contact_phone = request.form.get('contact_phone', '').strip()
        doc_number = request.form.get('doc_number', '').strip() or None
        found_date = request.form.get('found_date', '').strip() or None
        preferred_method = request.form.get('preferred_method', 'email').strip()
        anonymous = request.form.get('anonymous', 'false').lower() == 'true'

        photo = request.files.get('photo')
        photo_filename = None
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, filename)
            photo.save(image_path)
            photo_filename = filename

        # Database operation
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO found_documents 
            (doc_name, doc_type, location, photo, contact_name, contact_email, contact_phone, preferred_method, anonymous, doc_number, found_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            doc_name, doc_type, location, photo_filename,
            contact_name or None,
            contact_email or None,
            contact_phone or None,
            preferred_method, anonymous,
            doc_number, found_date
        ))

        conn.commit()
        found_id = cursor.lastrowid

        # 🔔 Call notification logic here
        notify_seekers_for_found_doc(found_id)

        return jsonify({
            "success": True,
            "message": "Report saved successfully and seekers notified",
            "found_id": found_id,
            "photo_uploaded": photo_filename is not None
        })

    except mysql.connector.Error as db_err:
        print("Database error:", db_err)
        return jsonify({"success": False, "message": "Database error occurred"}), 500

    except Exception as e:
        print("Error:", e)
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()





# Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




# Database connection
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


# In[2]:


@documents_bp.route('/api/report_found', methods=['POST'])
def report_found():
    conn = None
    cursor = None

    try:
        # Validate required fields
        required_fields = ['doc_name', 'doc_type', 'location']
        for field in required_fields:
            if field not in request.form or not request.form[field].strip():
                return jsonify({"success": False, "message": f"Missing required field: {field}"}), 400

        # Get form data
        doc_name = request.form['doc_name'].strip()
        doc_type = request.form['doc_type'].strip()
        location = request.form['location'].strip()
        contact_name = request.form.get('contact_name', '').strip()
        contact_email = request.form.get('contact_email', '').strip()
        contact_phone = request.form.get('contact_phone', '').strip()
        doc_number = request.form.get('doc_number', '').strip()  # optional
        found_date = request.form.get('found_date', '').strip()
        
        preferred_method = request.form.get('preferred_method', 'email').strip()
        anonymous = request.form.get('anonymous', 'false').lower() == 'true'

        photo = request.files.get('photo')
        photo_uploaded = False
        photo_filename = None

        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            image_path = os.path.join(upload_folder, filename)
            photo.save(image_path)
            photo_filename = filename

        # Database operation
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO found_documents 
            (doc_name, doc_type, location, photo, contact_name, contact_email, contact_phone, preferred_method, anonymous)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            doc_name, doc_type, location, photo_filename,
            contact_name if contact_name else None,
            contact_email if contact_email else None,
            contact_phone if contact_phone else None,
            preferred_method, anonymous
        ))

        conn.commit()
        found_id = cursor.lastrowid

        return jsonify({
            "success": True,
            "message": "Report saved successfully",
            "found_id": found_id,
            "photo_uploaded": photo_filename is not None
        })

    except mysql.connector.Error as db_err:
        print("Database error:", db_err)
        return jsonify({"success": False, "message": "Database error occurred"}), 500

    except Exception as e:
        print("Error:", e)
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()





