from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from connection import db, users_collection, vendors_collection, banks_collection, branches_collection
from bson import ObjectId
import redis
import datetime
from datetime import datetime, timedelta
import html
import re
import os
from functools import wraps
from bcrypt import gensalt, hashpw

app = Flask(__name__)
app.secret_key = "ProyekAkhirKapitaSelektaSoftwareEngineeringAlfamart"
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5000", "https://your-production-domain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

connRedis = redis.StrictRedis(host="10.85.49.147", port=6379, db=0, password="b56e784c-49a7-4adf-be06-7192ca6ea73e")

# Redis setup
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0)),
    password=os.getenv('REDIS_PASSWORD', None)
)

@app.route("/insertRedis", methods=['POST'])
def insertRedis():
    data = request.get_json()
    key = data.get('key')
    value = data.get('value')
    resultInsert = connRedis.set(name=key, value=value)
    if resultInsert:
        return jsonify({'status': True, 'data': {key: value}})
    return jsonify({'status': False, 'data': None})

@app.route("/getRedisData")
def getRedis():
    param = request.args.get('param')
    resultGetRedis = connRedis.get(param)
    if resultGetRedis:
        return jsonify({'status': True, 'data': resultGetRedis.decode('utf-8')})
    return jsonify({'status': False, 'data': None}) 

# Security Functions
def sanitize_input(data):
    if isinstance(data, str):
        data = re.sub(r'<script[\s\S]*?/script>', '', data)
        return html.escape(data.strip())
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    return data

def validate_mongodb_id(id_string):
    try:
        ObjectId(id_string)
        return True
    except:
        return False

def hash_password(password):
    """Hash password menggunakan bcrypt dan kembalikan dalam format binary sesuai MongoDB."""
    try:
        hashed = hashpw(password.encode('utf-8'), gensalt())
        return hashed
    except Exception as e:
        print(f"Error while hashing password: {e}")
        return None
    
def verify_password(password, hashed):
    """Verifikasi password dengan hash"""
    return hashpw(password.encode('utf-8'), hashed) == hashed
   
# Authentication & Authorization
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = session.get('session_id')
        if not session_id or not redis_client.get(session_id):
            return jsonify({"error": "Unauthorized", "redirect": "/login"}), 401
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_role = session.get('role')
            if not user_role:
                return jsonify({"error": "Unauthorized: Role not found"}), 401
            if user_role not in roles:
                return jsonify({"error": "Forbidden: Insufficient permissions"}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Basic Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'GET':
            return render_template('login.html')
        
        data = request.get_json() if request.is_json else request.form
        username = sanitize_input(data.get('username'))
        password = data.get('password')

        if not username or not password:
            return jsonify({"success": False, "message": "Username and password required"}), 400

        user = users_collection.find_one({"username": username})
        if user and verify_password(password, user['password']):
            if not user.get('active', True):
                return jsonify({"success": False, "message": "Account is not active"}), 403
            
            session_id = os.urandom(24).hex()
            session['session_id'] = session_id
            session['user_id'] = str(user['_id'])
            session['username'] = username
            session['role'] = user['role']
            session['email'] = user['email']

            redis_client.setex(
                session_id,
                int(timedelta(hours=24).total_seconds()),
                username
            )

            users_collection.update_one(
                {"_id": user['_id']},
                {"$set": {"last_login": datetime.utcnow()}}
            )

            # Kirim URL dashboard sesuai role dalam JSON
            redirect_url = url_for(f"{user['role'].lower()}_dashboard")
            return jsonify({"success": True, "redirectUrl": redirect_url}), 200
        
        return jsonify({"success": False, "message": "Invalid credentials"}), 401
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/logout')
@login_required
def logout():
    session_id = session.get('session_id')
    if session_id:
        redis_client.delete(session_id)
    session.clear()
    return redirect(url_for('home'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('forgot_password.html')
    
    data = request.get_json() if request.is_json else request.form
    username = sanitize_input(data.get('username'))
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not username or not new_password or not confirm_password:
        return jsonify({"success": False, "message": "All fields are required"}), 400
    
    if new_password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match"}), 400
    
    user = users_collection.find_one({"username": username})
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    if user.get('role') == 'DBA':
        return jsonify({"success": False, "message": "DBA cannot reset their own password"}), 403

    hashed_password = hash_password(new_password)
    users_collection.update_one(
        {"_id": user['_id']},
        {"$set": {"password": hashed_password}}
    )

    return jsonify({"success": True, "message": "Password reset successful. Please log in."})

@app.route('/api/session-role', methods=['GET'])
def get_session_role():
    try:
        role = session.get('role', None)
        if not role:
            return jsonify({"error": "Unauthorized"}), 401
        return jsonify({"role": role}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Dashboard Routes
# DBA Dashboard
@app.route('/dashboard/dba')
@role_required(['DBA'])
def dba_dashboard():
    return render_template('dashboard-dba.html')

@app.route('/dashboard/dba/manage-users')
@login_required
@role_required(['DBA'])
def manage_users():
    return render_template('dba-manage-users.html')

@app.route('/dashboard/dba/manage-banks')
@login_required
@role_required(['DBA', 'Admin', 'Finance'])
def manage_banks():
    return render_template('dba-manage-banks.html')

@app.route('/dashboard/dba/manage-branches')
@login_required
@role_required(['DBA', 'Admin', 'Finance'])
def manage_branches():
    return render_template('dba-manage-branches.html')

@app.route('/dashboard/dba/manage-vendors')
@login_required
@role_required(['DBA', 'Admin', 'Vendor'])
def manage_vendors():
    return render_template('dba-manage-vendors.html')

# Admin Dashboard
@app.route('/dashboard/admin')
@role_required(['Admin'])
def admin_dashboard():
    return render_template('dashboard-admin.html')

@app.route('/dashboard/admin/manage-users')
@login_required
@role_required(['Admin'])
def manage_users_admin():
    return render_template('admin-manage-users.html')

@app.route('/dashboard/admin/manage-banks')
@login_required
@role_required(['Admin', 'Finance'])
def manage_banks_admin():
    return render_template('admin-manage-banks.html')

@app.route('/dashboard/admin/manage-branches')
@login_required
@role_required(['Admin', 'Finance'])
def manage_branches_admin():
    return render_template('admin-manage-branches.html')

@app.route('/dashboard/admin/manage-vendors')
@login_required
@role_required(['Admin', 'Vendor'])
def manage_vendors_admin():
    return render_template('admin-manage-vendors.html')

# Finance Dashboard
@app.route('/dashboard/finance')
@role_required(['Finance'])
def finance_dashboard():
    return render_template('dashboard-finance.html')

@app.route('/dashboard/finance/manage-banks')
@login_required
@role_required(['Finance', 'Admin'])
def manage_banks_finance():
    return render_template('finance-manage-banks.html')

@app.route('/dashboard/finance/manage-branches')
@login_required
@role_required(['Finance', 'Admin'])
def manage_branches_finance():
    return render_template('finance-manage-branches.html')

# Vendor Dashboard
@app.route('/dashboard/vendor')
@role_required(['Vendor'])
def vendor_dashboard():
    return render_template('dashboard-vendor.html')

@app.route('/dashboard/vendor/manage-vendors')
@login_required
@role_required(['Vendor', 'Admin'])
def manage_vendors_vendor():
    return render_template('vendor-manage-vendors.html')

# User Management API Routes (DBA Only)
@app.route('/api/users', methods=['GET'])
@role_required(['DBA', 'Admin'])
def get_users():
    try:
        current_role = session.get('role')

        # Jika role Admin, filter untuk tidak menampilkan pengguna dengan role DBA
        query = {} if current_role == 'DBA' else {"role": {"$ne": "DBA"}}

        users = list(users_collection.find(query, {'password': 0}))
        return jsonify([{**user, '_id': str(user['_id'])} for user in users])
    except Exception as e:
        print("Error fetching users:", str(e))  # Log error di backend
        return jsonify({"error": str(e)}), 500

@app.route('/api/users', methods=['POST'])
@role_required(['DBA', 'Admin'])
def create_user():
    try:
        if users_collection.count_documents({}) == 0:  # Jika kosong
            dba_password = hash_password("dba123!@#")
            if not dba_password:
                return jsonify({"error": "Failed to hash DBA password"}), 500
            dba_user = {
                "username": "dba",
                "email": "dba@example.com",
                "password": dba_password,
                "role": "DBA",
                "active": True,
                "created_at": datetime.utcnow(),
                "last_login": None
            }
            users_collection.insert_one(dba_user)
        else:
            return jsonify({"error": "Users collection is not empty"}), 400

        current_role = session.get('role')
        data = sanitize_input(request.get_json())
        required_fields = ['username', 'email', 'role']

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        if current_role == 'Admin' and data['role'] == 'DBA':
            return jsonify({"error": "Admin cannot create DBA account"}), 400

        if users_collection.find_one({"username": data['username']}):
            return jsonify({"error": "Username already exists"}), 400

        hashed_password = hash_password(data['password'])
        if not hashed_password:
            return jsonify({"error": "Failed to hash password"}), 500

        user_doc = {
            "username": data['username'],
            "email": data['email'],
            "password": hashed_password,  # Simpan langsung dalam bentuk hashed binary
            "role": data['role'],
            "active": True,
            "created_at": datetime.utcnow(),
            "last_login": None
        }

        result = users_collection.insert_one(user_doc)
        return jsonify({"success": True, "id": str(result.inserted_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<username>', methods=['GET'])
@role_required(['DBA', 'Admin'])
def get_user(username):
    try:
        current_role = session.get('role')

        # Cari user di database, kecualikan field password
        user = users_collection.find_one({"username": username}, {'password': 0})
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Cegah Admin melihat detail DBA
        if current_role == 'Admin' and user['role'] == 'DBA':
            return jsonify({"error": "Access denied"}), 403

        # Convert _id menjadi string
        user['_id'] = str(user['_id'])
        return jsonify(user)
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/users/<username>', methods=['PUT'])
@role_required(['DBA', 'Admin'])
def update_user(username):
    try:
        current_user = session.get('username')
        current_role = session.get('role')

        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json()
        password = data.get('password')
        user_to_update = users_collection.find_one({"username": username})

        if not user_to_update:
            return jsonify({"error": "User not found"}), 404

        if current_role == 'Admin' and user_to_update.get('role') == 'DBA':
            return jsonify({"error": "Admins cannot modify users with the DBA role"}), 403

        update_data = {key: value for key, value in data.items() if value is not None}
        if password:
            hashed_password = hash_password(password)
            if not hashed_password:
                return jsonify({"error": "Failed to hash password"}), 500
            update_data['password'] = hashed_password

        if not update_data:
            return jsonify({"error": "No fields to update"}), 400

        result = users_collection.update_one({"username": username}, {"$set": update_data})
        if result.matched_count == 0:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"message": "User updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/role/dba-count', methods=['GET'])
@role_required(['DBA'])
def get_dba_count():
    try:
        dba_count = users_collection.count_documents({"role": "DBA"})
        return jsonify({"count": dba_count}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<username>', methods=['DELETE'])
@role_required(['DBA', 'Admin'])
def delete_user(username):
    try:
        current_user = session.get('username')
        current_role = session.get('role')

        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        if username == current_user:
            return jsonify({"error": "Cannot delete own account"}), 403

        user_to_delete = users_collection.find_one({"username": username})
        if not user_to_delete:
            return jsonify({"error": "User not found"}), 404

        if current_role == 'Admin' and user_to_delete.get('role') == 'DBA':
            return jsonify({"error": "Admins cannot delete users with the DBA role"}), 403

        result = users_collection.delete_one({"username": username})
        if result.deleted_count == 0:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Master Data API Routes
# Bank Management
@app.route('/api/banks', methods=['GET'])
@role_required(['DBA', 'Admin', 'Finance'])
def get_banks():
    try:
        # Ambil parameter query dari URL
        status = request.args.get('status', '').upper()

        # Query ke database berdasarkan status
        query = {}
        if status == 'ACTIVE':
            query = {"activeStatus": "Y"}

        # Pastikan koleksi bank tersedia
        banks = list(banks_collection.find(query, {"_id": 1, "bankDesc": 1}))
        return jsonify([{**bank, '_id': str(bank['_id'])} for bank in banks])
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/api/banks', methods=['POST'])
@role_required(['DBA', 'Admin', 'Finance'])
def create_bank():
    try:
        data = sanitize_input(request.get_json())
        bank_doc = {
            "_id": data.get('_id'),  # Bank code as ID
            "activeStatus": "Y",
            "bankDesc": data.get('bankDesc'),
            "setup": {
                "createDate": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "createUser": session.get('username'),
                "updateUser": "",
                "updateDate": ""
            }
        }

        result = banks_collection.insert_one(bank_doc)
        return jsonify({"success": True, "id": str(result.inserted_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/banks/<bank_id>', methods=['GET'])
@role_required(['DBA', 'Admin', 'Finance'])
def get_bank_by_id(bank_id):
    try:
        bank = banks_collection.find_one({"_id": bank_id})
        if not bank:
            return jsonify({"error": "Bank not found"}), 404

        # Konversi ObjectId ke string
        return jsonify({**bank, '_id': str(bank['_id'])})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/banks/<bank_id>', methods=['PUT'])
@role_required(['DBA', 'Admin', 'Finance'])
def update_bank(bank_id):
    try:
        data = sanitize_input(request.get_json())
        
        # Dokumen pembaruan
        update_doc = {
            "bankDesc": data.get('bankDesc'),
            "activeStatus": data.get('activeStatus', 'Y'),  # Default aktif
            "setup.updateUser": session.get('username'),  # User yang mengupdate
            "setup.updateDate": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")  # Tanggal update
        }

        # Update dokumen di MongoDB
        result = banks_collection.update_one(
            {"_id": bank_id},
            {"$set": update_doc}
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "Bank not found"}), 404

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
@app.route('/api/banks/<bank_id>', methods=['DELETE'])
@role_required(['DBA', 'Admin', 'Finance'])
def delete_bank(bank_id):
    try:
        result = banks_collection.delete_one({"_id": bank_id})
        if result.deleted_count:
            return jsonify({"success": True})
        return jsonify({"error": "Bank not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Branch Management
@app.route('/api/branches/<branch_id>', methods=['GET'])
@role_required(['DBA', 'Admin', 'Finance'])
def get_branch(branch_id):
    try:
        branch = branches_collection.find_one({"_id": branch_id})
        if not branch:
            return jsonify({"error": "Branch not found"}), 404
        # Konversi ObjectId ke string untuk JSON
        branch['_id'] = str(branch['_id'])
        return jsonify(branch)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/branches', methods=['GET'])
@role_required(['DBA', 'Admin', 'Finance'])
def get_branches():
    try:
        branches = list(branches_collection.find())
        return jsonify([{**branch, '_id': str(branch['_id'])} for branch in branches])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/branches', methods=['POST'])
@role_required(['DBA', 'Admin', 'Finance'])
def create_branch():
    try:
        data = sanitize_input(request.get_json())
        branch_doc = {
            "_id": data.get('_id'),  # Branch code as ID
            "activeStatus": "Y",
            "BranchName": data.get('BranchName'),
            "setup": {
                "createDate": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "createUser": session.get('username'),
                "updateUser": "",
                "updateDate": ""
            }
        }

        result = branches_collection.insert_one(branch_doc)
        return jsonify({"success": True, "id": str(result.inserted_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/branches/<branch_id>', methods=['PUT'])
@role_required(['DBA', 'Admin', 'Finance'])
def update_branch(branch_id):
    try:
        data = sanitize_input(request.get_json())
        update_doc = {
            "BranchName": data.get('BranchName'),
            "activeStatus": data.get('activeStatus', 'Y'),
            "setup.updateUser": session.get('username'),
            "setup.updateDate": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

        result = branches_collection.update_one(
            {"_id": branch_id},
            {"$set": update_doc}
        )
        
        if result.modified_count:
            return jsonify({"success": True})
        return jsonify({"error": "Branch not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/branches/<branch_id>', methods=['DELETE'])
@role_required(['DBA', 'Admin', 'Finance'])
def delete_branch(branch_id):
    try:
        # Cek apakah cabang ada
        branch = branches_collection.find_one({"_id": branch_id})
        if not branch:
            return jsonify({"error": "Branch not found"}), 404
        
        # Menghapus cabang
        result = branches_collection.delete_one({"_id": branch_id})
        if result.deleted_count:
            return jsonify({"success": True})
        return jsonify({"error": "Failed to delete branch"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Transaction Data API Routes (Vendor Management)
@app.route('/api/vendors', methods=['GET'])
@role_required(['DBA', 'Admin', 'Vendor'])
def get_vendors():
    try:
        user_role = session.get('role')
        user_email = session.get('email')
        
        if user_role == 'Vendor':
            vendor = vendors_collection.find_one({"emailCompany": user_email})
            if not vendor:
                return jsonify({"error": "Vendor not found"}), 404
            vendor['_id'] = str(vendor['_id'])
            return jsonify([vendor])  # Return as a list to match frontend expectations
        
        vendors = list(vendors_collection.find())
        return jsonify([{**vendor, '_id': str(vendor['_id'])} for vendor in vendors])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vendors', methods=['POST'])
@role_required(['DBA', 'Admin', 'Vendor'])
def create_vendor():
    try:
        # Log input data
        data = sanitize_input(request.get_json())
        print("Received data:", data)  # Tambahkan log
        
        required_fields = [
            "partnerType", "vendorName", "unitUsaha", "address","emailCompany", "country", "noTelp"
        ]
        
        # Validasi field wajib
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            error_message = f"Missing required fields: {', '.join(missing_fields)}"
            print(error_message)  # Log error
            return jsonify({"error": error_message}), 400
        
        # Validasi bank - use string comparison instead of ObjectId
        for account in data.get("accountBank", []):
            bank_id = account.get("bankId")
            if not bank_id:
                continue
            bank_exists = banks_collection.find_one({"_id": bank_id, "activeStatus": "Y"})
            if not bank_exists:
                error_message = f"Invalid bank selected: {bank_id}"
                print(error_message)  # Log error
                return jsonify({"error": error_message}), 400
        
        # Insert vendor
        vendor = {
            "_id": data.get("_id"),  # optional field
            "partnerType": data.get("partnerType", ""),  # optional field
            "vendorName": data.get("vendorName", ""),  # sesuaikan dengan nama field di backend
            "unitUsaha": data.get("unitUsaha", ""),  # sesuaikan dengan nama field di backend
            "address": data.get("address", ""),
            "country": data.get("country", ""),
            "province": data.get("province", ""),
            "noTelp": data.get("noTelp", ""),
            "emailCompany": data.get("emailCompany", ""),  # sesuaikan dengan nama field di backend
            "website": data.get("website", ""),
            "namePIC": data.get("namePic", ""),
            "noTelpPIC": data.get("noTelpPIC", ""),
            "emailPIC": data.get("emailPIC", ""),
            "positionPIC": data.get("positionPIC", ""),
            "NPWP": data.get("NPWP", ""),
            "activeStatus":  "Y",
            "PIC": data.get("PIC", []),
            "supportingEquipment": data.get("supportingEquipment", []),
            "branchOffice": data.get("branchOffice", []),
            "accountBank": data.get("accountBank", []),
            "change": {
                "createUser": session.get('username'),
                "createDate": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "updateUser": "",
                "updateDate": ""
            }
        }
        result = vendors_collection.insert_one(vendor)
        return jsonify({"message": "Vendor created successfully", "_id": str(result.inserted_id)}), 201
    except Exception as e:
        print("Server error:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/api/vendors/<vendor_id>', methods=['GET'])
@role_required(['DBA', 'Admin', 'Vendor'])
def get_vendor(vendor_id):
    try:
        vendor = vendors_collection.find_one({"_id": vendor_id})
        
        if not vendor:
            return jsonify({"error": "Vendor not found"}), 404
        
        return jsonify(vendor), 200
    
    except Exception as e:
        app.logger.error(f"Error fetching vendor: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/api/vendors/<vendor_id>', methods=['PUT'])
@role_required(['DBA', 'Admin', 'Vendor'])
def update_vendor(vendor_id):
    try:
        user_role = session.get('role')
        user_email = session.get('email')
        
        # Find vendor by _id string
        vendor = vendors_collection.find_one({"_id": vendor_id})
        if not vendor:
            return jsonify({"error": "Vendor not found"}), 404
        
        if user_role == 'Vendor' and vendor.get('emailCompany') != user_email:
            return jsonify({"error": "Access denied"}), 403
        
        data = sanitize_input(request.get_json())
        print("Received data:", data)
        
        # Validate mandatory fields
        mandatory_fields = ["partnerType", "vendorName", "unitUsaha", "country", "noTelp", "emailCompany"]
        for field in mandatory_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Mandatory field {field} is missing"}), 400
        
        # Process arrays from nested form data
        PICs = []
        for i in range(len(vendor.get('PIC', []))):
            PIC = {
                'username': data.get(f'PIC_username[{i}]'),
                'name': data.get(f'PIC_name[{i}]'),
                'email': data.get(f'PIC_email[{i}]'),
                'noTelp': data.get(f'PIC_noTelp[{i}]')
            }
            # Only add if all fields are not None
            if all(PIC.values()):
                PICs.append(PIC)
        
        supporting_equipment = []
        for i in range(len(vendor.get('supportingEquipment', []))):
            equipment = {
                'toolType': data.get(f'supportingEquipment_toolType[{i}]'),
                'count': data.get(f'supportingEquipment_count[{i}]'),
                'merk': data.get(f'supportingEquipment_merk[{i}]'),
                'condition': data.get(f'supportingEquipment_condition[{i}]')
            }
            # Only add if all fields are not None
            if all(equipment.values()):
                supporting_equipment.append(equipment)
        
        branch_offices = []
        for i in range(len(vendor.get('branchOffice', []))):
            branch = {
                'branchName': data.get(f'branchOffice_branchName[{i}]'),
                'location': data.get(f'branchOffice_location[{i}]'),
                'address': data.get(f'branchOffice_address[{i}]'),
                'country': data.get(f'branchOffice_country[{i}]'),
                'noTelp': data.get(f'branchOffice_noTelp[{i}]'),
                'website': data.get(f'branchOffice_website[{i}]'),
                'email': data.get(f'branchOffice_email[{i}]')
            }
            # Only add if all fields are not None
            if all(branch.values()):
                branch_offices.append(branch)
        
        account_banks = []
        for i in range(len(vendor.get('accountBank', []))):
            bank = {
                'accountNumber': data.get(f'accountBank_accountNumber[{i}]'),
                'accountName': data.get(f'accountBank_accountName[{i}]')
            }
            # Only add if all fields are not None
            if all(bank.values()):
                account_banks.append(bank)
        
        # Validasi bank - use string comparison instead of ObjectId
        for account in account_banks:
            bank_id = account.get("bankId")
            if not bank_id:
                continue
            bank_exists = banks_collection.find_one({"_id": bank_id, "activeStatus": "Y"})
            if not bank_exists:
                error_message = f"Invalid bank selected: {bank_id}"
                print(error_message)  # Log error
                return jsonify({"error": error_message}), 400
        
        # Prepare update document
        update_fields = {
            "partnerType": data.get("partnerType", vendor.get("partnerType")),
            "vendorName": data.get("vendorName", vendor.get("vendorName")),
            "unitUsaha": data.get("unitUsaha", vendor.get("unitUsaha")),
            "address": data.get("address", vendor.get("address")),
            "country": data.get("country", vendor.get("country")),
            "province": data.get("province", vendor.get("province")),
            "noTelp": data.get("noTelp", vendor.get("noTelp")),
            "emailCompany": data.get("emailCompany", vendor.get("emailCompany")),
            "website": data.get("website", vendor.get("website")),
            "namePIC": data.get("namePIC", vendor.get("namePIC")),
            "noTelpPIC": data.get("noTelpPIC", vendor.get("noTelpPIC")),
            "emailPIC": data.get("emailPIC", vendor.get("emailPIC")),
            "positionPIC": data.get("positionPIC", vendor.get("positionPIC")),
            "NPWP": data.get("NPWP", vendor.get("NPWP")),
            "activeStatus": data.get("activeStatus", vendor.get("activeStatus")),
            
            # Preserve existing arrays if no new data is provided
            "PIC": PICs if PICs else vendor.get("PIC", []),
            "supportingEquipment": supporting_equipment if supporting_equipment else vendor.get("supportingEquipment", []),
            "branchOffice": branch_offices if branch_offices else vendor.get("branchOffice", []),
            "accountBank": account_banks if account_banks else vendor.get("accountBank", []),
            
            "create": vendor.get("create", {}),
            "change": {
                "updateDate": datetime.now(),
                "updateUser": session.get('username')
            }
        }
        
        result = vendors_collection.update_one(
            {"_id": vendor_id},
            {"$set": update_fields}
        )
        
        if result.modified_count == 0:
            return jsonify({"error": "No changes were made"}), 400
        
        return jsonify({"message": "Vendor updated successfully"}), 200
    
    except Exception as e:
        app.logger.error(f"Error updating vendor: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/api/vendors/<vendor_id>', methods=['DELETE'])
@role_required(['DBA', 'Admin'])
def delete_vendor(vendor_id):
    try:
        result = vendors_collection.delete_one({"_id": vendor_id})
        if result.deleted_count:
            return jsonify({"success": True})
        return jsonify({"error": "Vendor not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Error Handlers
@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({"error": f"Bad request: {error}"}), 400

@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({"error": f"Unauthorized: {error}"}), 401

@app.errorhandler(403)
def forbidden_error(error):
    return jsonify({"error": f"Forbidden: {error}"}), 403

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": f"Not found: {error}"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": f"Internal server error: {error}"}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))