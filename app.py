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
    return render_template('Home.html')

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
