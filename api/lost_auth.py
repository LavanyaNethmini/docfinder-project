#!/usr/bin/env python
# coding: utf-8

# In[1]:





# In[2]:


from flask import Blueprint, Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import jwt, datetime
from werkzeug.security import generate_password_hash, check_password_hash

users_bp = Blueprint('users', __name__)
CORS(app)
app.config['SECRET_KEY'] = 'your-secret-key'

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


# In[3]:


# Register Route
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    role = 'seeker'  

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, phone_number, password, role) VALUES (%s, %s, %s, %s, %s)",
            (name, email, phone, password, role)
        )
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400
    finally:
        cursor.close()
        conn.close()


# In[4]:


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()

        if user:
            
            token = jwt.encode({
                'user_id': user['id'],
                'role': user['role'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }, 'your_secret_key', algorithm='HS256')

        
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'role': user['role'],
                    'name': user['name']
                },
                'token': token
            })
        else:
            return jsonify({'message': 'Invalid email or password'}), 401
    finally:
        cursor.close()
        conn.close()


# In[ ]:


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

