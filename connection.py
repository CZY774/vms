from pymongo import MongoClient
from bcrypt import hashpw, gensalt
import os
from datetime import timedelta, datetime

# Koneksi ke MongoDB dengan environment variable
MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://yogaliuze:cGCSaK31stTMt0R9@clusterkapita.hkeyv.mongodb.net/')

client = MongoClient(MONGO_URI)
db = client['ProyekAkhir']

# Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

# Session configuration
SESSION_LIFETIME = timedelta(hours=24)

def hash_password(password):
    """Hash password menggunakan bcrypt"""
    try:
        return hashpw(password.encode('utf-8'), gensalt())
    except Exception as e:
        print(f"Error while hashing password: {e}")
        return None


# Inisialisasi Koleksi
try:
    collections = ['users', 'vendors', 'banks', 'branches', 'sessions']
    for collection in collections:
        if collection not in db.list_collection_names():
            db.create_collection(collection)
    
    users_collection = db['users']
    vendors_collection = db['vendors']
    banks_collection = db['banks']
    branches_collection = db['branches']
    sessions_collection = db['sessions']

    # Create indexes for better security and performance
    users_collection.create_index("username", unique=True)
    vendors_collection.create_index("email", unique=True)
    sessions_collection.create_index("expireAt", expireAfterSeconds=0)

    print("Koneksi berhasil dan koleksi sudah diinisialisasi.")

    # Tambahkan pengguna DBA default jika belum ada data di koleksi `users`
    if users_collection.count_documents({}) == 0:  # Jika kosong
        dba_password = hash_password("dba123!@#")
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
        print("Default DBA user created with username 'dba' and password 'dba123!@#'")
except Exception as e:
    print(f"Error during initialization: {e}")


def verify_password(password, hashed):
    """Verifikasi password dengan hash"""
    return hashpw(password.encode('utf-8'), hashed) == hashed

def create_user(username, password, role, email=None):
    """Buat user baru"""
    try:
        if users_collection.find_one({"username": username}):
            return False, "Username sudah digunakan"
        
        hashed_pw = hash_password(password)
        user_doc = {
            "username": username,
            "email": email,
            "password": hashed_pw,
            "role": role,
            "active": True,
            "created_at": datetime.utcnow(),
            "last_login": None
        }
        
        users_collection.insert_one(user_doc)
        return True, "User berhasil dibuat"
    except Exception as e:
        return False, f"Error creating user: {e}"

def validate_login(username, password):
    """Validasi login user"""
    try:
        user = users_collection.find_one({"username": username, "active": True})
        if not user:
            return False, None, "Username tidak ditemukan atau akun tidak aktif"
        
        if verify_password(password, user['password']):
            users_collection.update_one(
                {"_id": user['_id']},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            return True, user, "Login berhasil"
        return False, None, "Password salah"
    except Exception as e:
        return False, None, f"Error during login: {e}"