from backend.config import settings
from pymongo import MongoClient

def get_mongodb_client():
    """Get MongoDB client connection."""
    mongo_uri = settings.MONGODB_URI if hasattr(settings, 'MONGODB_URI') else "mongodb://localhost:27017"
    return MongoClient(mongo_uri)

mongodb_client = get_mongodb_client()
mongodb_db = mongodb_client["hospital_management"]
medical_records_collection = mongodb_db["medical_records"]

medical_records_collection.find({})