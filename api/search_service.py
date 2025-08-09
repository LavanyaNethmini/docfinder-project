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


@app.route('/api/search', methods=['GET'])
def search_documents():
    query = request.args.get('query')
    if not query:
        return jsonify({'success': False, 'message': 'Query parameter is required'}), 400

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM found_documents WHERE doc_name LIKE %s", ('%' + query + '%',))
        results = cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify({'success': True, 'data': results})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# In[ ]:


if __name__ == '__main__':
    app.run(port=5003)

