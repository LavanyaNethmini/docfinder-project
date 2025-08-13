#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# notifications.py (or inside your main Flask file)

import os
from flask import Blueprint, request, jsonify
from datetime import datetime

notifications_bp = Blueprint('notifications_bp', __name__)

@notifications_bp.route('/api/notification-requests', methods=['POST'])
def create_notification_request():
    data = request.get_json(silent=True) or request.form

    required = ['first_name','last_name','email','doc_type','doc_name']
    missing = [k for k in required if not data.get(k)]
    if missing:
        return jsonify({"ok": False, "message": f"Missing fields: {', '.join(missing)}"}), 400

    # Extract fields
    first_name     = data.get('first_name').strip()
    last_name      = data.get('last_name').strip()
    email          = data.get('email').strip().lower()
    phone          = (data.get('phone') or '').strip()
    doc_type       = data.get('doc_type').strip()
    doc_number     = (data.get('doc_number') or '').strip()
    doc_name       = data.get('doc_name').strip()
    lost_location  = (data.get('lost_location') or '').strip()
    lost_date      = data.get('lost_date') or None
    additional     = (data.get('additional_info') or '').strip()

    # Validate date if provided
    if lost_date:
        try:
            datetime.strptime(lost_date, "%Y-%m-%d")
        except ValueError:
            return jsonify({"ok": False, "message": "Invalid date format for lost_date (use YYYY-MM-DD)"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO notification_requests
        (first_name, last_name, email, phone, doc_type, doc_number, doc_name, lost_location, lost_date, additional_info)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (first_name, last_name, email, phone, doc_type, doc_number, doc_name, lost_location, lost_date, additional))
    conn.commit()

    return jsonify({"ok": True, "message": "Notification saved."}), 201


# In[ ]:




