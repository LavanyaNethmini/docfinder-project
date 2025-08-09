#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask
from flask_cors import CORS
from flask import render_template
import os

from api.lost_auth import users_bp
from api.search_service import search_bp
from api.found_documents import documents_bp

app = Flask(__name__)
CORS(app)
# Uploads folder config (centralized)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['SECRET_KEY'] = 'your-secret-key'


app.register_blueprint(users_bp)
app.register_blueprint(search_bp)
app.register_blueprint(documents_bp)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/search')
def search():
    return render_template('Search.html')

@app.route('/search_details')
def search_details():
    return render_template('search-details.html')

@app.route('/about')
def about():
    return render_template('About.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('Registration.html')

@app.route('/report_details')
def report_details():
    return render_template('report-details.html')

@app.route('/claim_details')
def claim_details():
    return render_template(' claim-details.html')

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
