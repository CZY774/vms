from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from connection import (
    db, users_collection, vendors_collection, 
    banks_collection, branches_collection,
    hash_password, verify_password
)
from bson import ObjectId
import redis
import datetime
import html
import re
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)
# Konfigurasi CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5000", "https://your-production-domain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Redis setup
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0)),
    password=os.getenv('REDIS_PASSWORD', None)
)

# Security Functions
def sanitize_input(data):
    """Sanitize input data untuk mencegah XSS dan injection"""
    if isinstance(data, str):
        # Remove any script tags
        data = re.sub(r'<script[\s\S]*?/script>', '', data)
        # Escape HTML
        return html.escape(data.strip())
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    return data

def validate_mongodb_id(id_string):
    """Validasi MongoDB ObjectID"""
    try:
        ObjectId(id_string)
        return True
    except:
        return False

# Authentication & Authorization
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = session.get('session_id')
        if not session_id or not redis_client.get(session_id):
            return jsonify({"error": "Unauthorized", "redirect": "/login"}), 401
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user_role = session.get('role')
            if user_role not in allowed_roles and 'DBA' not in allowed_roles:
                return jsonify({"error": "Forbidden"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def home():
    return render_template('index.html')

# Route Login dan Authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json() if request.is_json else request.form
    username = sanitize_input(data.get('username'))
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400

    user = users_collection.find_one({"username": username})
    if user and verify_password(password, user['password']):
        if not user.get('active', True):  # Cek apakah akun aktif
            return jsonify({"success": False, "message": "Account is not active"}), 403
        session_id = os.urandom(24).hex()
        session['session_id'] = session_id
        session['user_id'] = str(user['_id'])
        session['username'] = username
        session['role'] = user['role']

        # Set session in Redis with 24 hour expiry
        redis_client.setex(
            session_id,
            datetime.timedelta(hours=24),
            username
        )

        return jsonify({
            "success": True,
            "redirect": f"/dashboard/{user['role'].lower()}"
        })

    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    
    data = request.get_json() if request.is_json else request.form
    username = sanitize_input(data.get('username'))
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    email = sanitize_input(data.get('email'))

    if not all([username, password, confirm_password, email]):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    if password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match"}), 400

    if users_collection.find_one({"username": username}):
        return jsonify({"success": False, "message": "Username already exists"}), 400

    if users_collection.find_one({"email": email}):
        return jsonify({"success": False, "message": "Email already registered"}), 400

    hashed_password = hash_password(password)
    user_doc = {
        "username": username,
        "password": hashed_password,
        "email": email,
        "role": "Vendor",  # Default role for new signups
        "active": True,
        "created_at": datetime.datetime.utcnow()
    }

    users_collection.insert_one(user_doc)
    return jsonify({"success": True, "message": "Account created successfully"})

@app.route('/logout')
def logout():
    session_id = session.get('session_id')
    if session_id:
        redis_client.delete(session_id)
    session.clear()
    return redirect(url_for('login'))

# Dashboard Routes
@app.route('/dashboard/dba')
@role_required(['DBA'])
def dba_dashboard():
    return render_template('dashboard_dba.html')

@app.route('/dashboard/admin')
@role_required(['DBA', 'Admin'])
def admin_dashboard():
    return render_template('dashboard_admin.html')

@app.route('/dashboard/vendor')
@role_required(['DBA', 'Admin', 'Vendor'])
def vendor_dashboard():
    return render_template('dashboard_vendor.html')

@app.route('/dashboard/finance')
@role_required(['DBA', 'Admin', 'Finance'])
def finance_dashboard():
    return render_template('dashboard_finance.html')

# API Routes for User Management
@app.route('/api/users', methods=['GET'])
@role_required(['DBA', 'Admin'])
def get_users():
    try:
        users = list(users_collection.find({}, {'password': 0}))
        return jsonify([{**user, '_id': str(user['_id'])} for user in users])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users', methods=['POST'])
@role_required(['DBA', 'Admin'])
def create_user():
    try:
        data = sanitize_input(request.get_json())
        required_fields = ['username', 'password', 'email', 'role']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        if users_collection.find_one({"username": data['username']}):
            return jsonify({"error": "Username already exists"}), 400
        
        # Hash password
        hashed_password = hash_password(data['password'])
        if not hashed_password:
            return jsonify({"error": "Failed to hash password"}), 500

        user_doc = {
            "username": data['username'],
            "password": hash_password(data['password']),
            "email": data['email'],
            "role": data['role'],
            "active": True,
            "created_at": datetime.datetime.utcnow()
        }

        result = users_collection.insert_one(user_doc)
        return jsonify({"success": True, "id": str(result.inserted_id)})
    except Exception as e:
        print(f"Error while creating user: {e}")  # Log error untuk debugging
        return jsonify({"error": str(e)}), 500

# Vendor Management API Routes
@app.route('/api/vendors', methods=['GET'])
@role_required(['DBA', 'Admin', 'Vendor'])
def get_vendors():
    try:
        user_role = session.get('role')
        user_id = session.get('user_id')

        if user_role == 'Vendor':
            # Vendors can only see their own profile
            vendors = list(vendors_collection.find({"user_id": user_id}))
        else:
            # Admin and DBA can see all vendors
            vendors = list(vendors_collection.find())

        return jsonify([{**vendor, '_id': str(vendor['_id'])} for vendor in vendors])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vendors', methods=['POST'])
@role_required(['DBA', 'Admin'])
def create_vendor():
    try:
        data = sanitize_input(request.get_json())
        required_fields = ['name', 'email', 'address']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        vendor_doc = {
            **data,
            "created_at": datetime.datetime.utcnow(),
            "created_by": session.get('username'),
            "active": True
        }

        result = vendors_collection.insert_one(vendor_doc)
        return jsonify({"success": True, "id": str(result.inserted_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Bank Management API Routes
@app.route('/api/banks', methods=['GET'])
@role_required(['DBA', 'Admin', 'Finance'])
def get_banks():
    try:
        banks = list(banks_collection.find())
        return jsonify([{**bank, '_id': str(bank['_id'])} for bank in banks])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/banks', methods=['POST'])
@role_required(['DBA', 'Admin', 'Finance'])
def create_bank():
    try:
        data = sanitize_input(request.get_json())
        required_fields = ['name', 'code']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        bank_doc = {
            **data,
            "created_at": datetime.datetime.utcnow(),
            "created_by": session.get('username'),
            "active": True
        }

        result = banks_collection.insert_one(bank_doc)
        return jsonify({"success": True, "id": str(result.inserted_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))