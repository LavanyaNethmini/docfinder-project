#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask
from flask_cors import CORS
import os

from lost_auth_api import users_bp
from search_service_api import search_bp
from found_documents_api import documents_bp

app = Flask(__name__)
CORS(app)
# Uploads folder config (centralized)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')


app.register_blueprint(users_bp)
app.register_blueprint(search_bp)
app.register_blueprint(documents_bp)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

