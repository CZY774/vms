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
from datetime import datetime, timedelta
import html
import re
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)
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
            if user_role not in allowed_roles:
                return jsonify({"error": "Forbidden"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Basic Routes
@app.route('/')
def home():
    return render_template('index.html')

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
        if not user.get('active', True):
            return jsonify({"success": False, "message": "Account is not active"}), 403
        
        session_id = os.urandom(24).hex()
        session['session_id'] = session_id
        session['user_id'] = str(user['_id'])
        session['username'] = username
        session['role'] = user['role']

        redis_client.setex(
            session_id,
            int(timedelta(hours=24).total_seconds()),
            username
        )

        users_collection.update_one(
            {"_id": user['_id']},
            {"$set": {"last_login": datetime.utcnow()}}
        )

        return redirect(url_for(f"{user['role'].lower()}_dashboard"))


    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/logout')
@login_required
def logout():
    session_id = session.get('session_id')
    if session_id:
        redis_client.delete(session_id)
    session.clear()
    return redirect(url_for('login'))

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
    
    hashed_password = hash_password(new_password)
    users_collection.update_one(
        {"_id": user['_id']},
        {"$set": {"password": hashed_password}}
    )

    return jsonify({"success": True, "message": "Password reset successful. Please log in."})


# Dashboard Routes
@app.route('/dashboard/dba')
@role_required(['DBA'])
def dba_dashboard():
    return render_template('dashboard-dba.html')

@app.route('/dashboard/admin')
@role_required(['Admin'])
def admin_dashboard():
    return render_template('dashboard-admin.html')

@app.route('/dashboard/finance')
@role_required(['Finance'])
def finance_dashboard():
    return render_template('dashboard-finance.html')

@app.route('/dashboard/vendor')
@role_required(['Vendor'])
def vendor_dashboard():
    return render_template('dashboard-vendor.html')

@app.route('/dashboard/dba/dba-manage-users')
@login_required
@role_required(['DBA'])
def manage_users():
    return render_template('dba-manage-users.html')

@app.route('/dashboard/dba/manage-banks')
@login_required
@role_required(['DBA', 'Admin', 'Finance'])
def manage_banks():
    return render_template('manage-banks.html')

@app.route('/dashboard/dba/manage-branches')
@login_required
@role_required(['DBA', 'Admin', 'Finance'])
def manage_branches():
    return render_template('manage-branches.html')

@app.route('/dashboard/dba/manage-vendors')
@login_required
@role_required(['DBA', 'Admin', 'Vendor'])
def manage_vendors():
    return render_template('manage-vendors.html')

# User Management API Routes (DBA Only)
@app.route('/api/users', methods=['GET'])
@role_required(['DBA'])
def get_users():
    try:
        users = list(users_collection.find({}, {'password': 0}))
        return jsonify([{**user, '_id': str(user['_id'])} for user in users])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users', methods=['POST'])
@role_required(['DBA'])
def create_user():
    try:
        data = sanitize_input(request.get_json())
        required_fields = ['username', 'email', 'role']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        if users_collection.find_one({"username": data['username']}):
            return jsonify({"error": "Username already exists"}), 400

        user_doc = {
            "username": data['username'],
            "email": data['email'],
            "password": hash_password(data['password']),
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
@role_required(['DBA'])
def get_user(username):
    try:
        # Mendapatkan username dari session
        current_user = session.get('username')
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        # Cari user di database, kecualikan field password
        user = users_collection.find_one({"username": username}, {'password': 0})
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Convert _id menjadi string
        user['_id'] = str(user['_id'])
        return jsonify(user)
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/users/<username>', methods=['PUT'])
@role_required(['DBA'])
def update_user(username):
    try:
        current_user = session.get('username')
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json()
        update_data = {key: value for key, value in data.items() if value is not None}

        if not update_data:
            return jsonify({"error": "No fields to update"}), 400

        # Validasi perubahan untuk role dan active
        if username == current_user:
            if 'role' in update_data or 'active' in update_data:
                current_role = users_collection.find_one({"username": current_user}, {"role": 1}).get('role')

                if current_role == 'DBA':
                    dba_count = users_collection.count_documents({"role": "DBA"})

                    # Validasi perubahan role
                    if 'role' in update_data and update_data['role'] != 'DBA' and dba_count <= 1:
                        return jsonify({"error": "Cannot remove the only DBA role"}), 403

                    # Validasi perubahan active
                    if 'active' in update_data and not update_data['active'] and dba_count <= 1:
                        return jsonify({"error": "Cannot deactivate the only DBA account"}), 403

        # Update data user
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
@role_required(['DBA'])
def delete_user(username):
    try:
        current_user = session.get('username')
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        if username == current_user:
            return jsonify({"error": "Cannot delete own account"}), 403

        user = users_collection.find_one({"username": username})
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Validasi jika role adalah DBA
        if user.get('role') == 'DBA':
            dba_count = users_collection.count_documents({"role": "DBA"})
            if dba_count <= 1:
                return jsonify({"error": "Cannot delete the only DBA account"}), 403

        # Hapus user
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
        banks = list(banks_collection.find())
        return jsonify([{**bank, '_id': str(bank['_id'])} for bank in banks])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        user_id = session.get('user_id')

        if user_role == 'Vendor':
            vendors = list(vendors_collection.find({"pic.username": session.get('username')}))
        else:
            vendors = list(vendors_collection.find())

        return jsonify([{**vendor, '_id': str(vendor['_id'])} for vendor in vendors])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vendors', methods=['POST'])
@role_required(['DBA', 'Admin', 'Vendor'])
def create_vendor():
    try:
        data = sanitize_input(request.get_json())
        vendor_doc = {
            "_id": data.get('_id', str(ObjectId())),  # Generate ID
            "vendorName": data.get('vendorName', ''),  # Required vendor name
            "unitUsaha": data.get('unitUsaha', 'IT'),  # Default: IT
            "address": data.get('address', ''),       # Required address
            "country": data.get('country', ''),       # Optional
            "province": data.get('province', ''),     # Optional
            "noTelp": data.get('noTelp', ''),         # Optional phone number
            "emailCompany": data.get('emailCompany', ''),  # Optional email
            "activeStatus": "Y",  # Default: Active
            "change": {
                "createDate": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "createUser": session.get('username'),
                "updateUser": "",
                "updateDate": ""
            }
        }

        result = vendors_collection.insert_one(vendor_doc)
        return jsonify({"success": True, "id": str(result.inserted_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/vendors/<vendor_id>', methods=['GET'])
@role_required(['DBA', 'Admin', 'Vendor'])
def get_vendor(vendor_id):
    try:
        user_role = session.get('role')
        username = session.get('username')

        query = {"_id": vendor_id}
        if user_role == 'Vendor':
            query["pic.username"] = username

        vendor = vendors_collection.find_one(query)
        if not vendor:
            return jsonify({"error": "Vendor not found"}), 404

        vendor['_id'] = str(vendor['_id'])
        return jsonify(vendor)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vendors/<vendor_id>', methods=['PUT'])
@role_required(['DBA', 'Admin', 'Vendor'])
def update_vendor(vendor_id):
    try:
        user_role = session.get('role')
        username = session.get('username')

        # Verify vendor exists and user has permission
        query = {"_id": vendor_id}
        if user_role == 'Vendor':
            query["pic.username"] = username

        vendor = vendors_collection.find_one(query)
        if not vendor:
            return jsonify({"error": "Vendor not found or access denied"}), 404

        data = sanitize_input(request.get_json())
        
        # Prepare update document
        update_doc = {
            "partnerType": data.get('partnerType', vendor.get('partnerType', '')),
            "vendorName": data.get('vendorName', vendor.get('vendorName', '')),
            "unitUsaha": data.get('unitUsaha', vendor.get('unitUsaha', 'IT')),
            "address": data.get('address', vendor.get('address', '')),
            "country": data.get('country', vendor.get('country', '')),
            "province": data.get('province', vendor.get('province', '')),
            "noTelp": data.get('noTelp', vendor.get('noTelp', '')),
            "emailCompany": data.get('emailCompany', vendor.get('emailCompany', '')),
            "website": data.get('website', vendor.get('website', '')),
            "namePIC": data.get('namePIC', vendor.get('namePIC', '')),
            "noTelpPIC": data.get('noTelpPIC', vendor.get('noTelpPIC', '')),
            "emailPIC": data.get('emailPIC', vendor.get('emailPIC', '')),
            "positionPIC": data.get('positionPIC', vendor.get('positionPIC', '')),
            "noNPWP": data.get('noNPWP', vendor.get('noNPWP', '')),
            "activeStatus": data.get('activeStatus', vendor.get('activeStatus', 'Y')),
            "supportingEquipment": data.get('supportingEquipment', vendor.get('supportingEquipment', [])),
            "branchOffice": data.get('branchOffice', vendor.get('branchOffice', [])),
            "accountBank": data.get('accountBank', vendor.get('accountBank', []))
        }

        # Keep original PIC if vendor role
        if user_role == 'Vendor':
            update_doc["pic"] = vendor.get('pic', [])
        else:
            update_doc["pic"] = data.get('pic', vendor.get('pic', []))

        result = vendors_collection.update_one(
            {"_id": vendor_id},
            {"$set": update_doc}
        )
        
        if result.modified_count:
            return jsonify({"success": True})
        return jsonify({"error": "No changes made"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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