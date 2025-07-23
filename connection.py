from pymongo import MongoClient
import os
from datetime import timedelta, datetime

# Koneksi ke MongoDB dengan environment variable
MONGO_URI = os.getenv('MONGO_URI', '')

client = MongoClient(MONGO_URI)
db = client['ProyekAkhir']

# Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

# Session configuration
SESSION_LIFETIME = timedelta(hours=24)

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

except Exception as e:
    print(f"Error during initialization: {e}")
