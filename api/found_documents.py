#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import mysql.connector

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = r'C:\wamp64\www\lost-found\uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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


# In[2]:


@app.route('/api/report_found', methods=['POST'])
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
        preferred_method = request.form.get('preferred_method', 'email').strip()
        anonymous = request.form.get('anonymous', 'false').lower() == 'true'

        photo = request.files.get('photo')
        photo_uploaded = False
        photo_filename = None

        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            photo_filename = filename 
            photo_uploaded = True

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

        return jsonify({
            "success": True,
            "message": "Report saved successfully",
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



# In[ ]:


if __name__ == '__main__':
    app.run(port=5001)

