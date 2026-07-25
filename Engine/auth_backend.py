# Engine/auth_backend.py
import re
import bcrypt
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# The connection bridge configuration
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "StudyBuddyDB"


def get_db_collection():
    """Establishes connection to the MongoDB engine."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    db = client[DB_NAME]
    return db["users"]


def validate_registration_inputs(username, email, password):
    """Checks input constraints before sending data to the database."""
    username = username.strip()
    email = email.strip().lower()

    if not username or not email or not password:
        return False, "All fields are required!"
    if len(username) < 3:
        return False, "Username must be at least 3 characters long."

    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return False, "Invalid email address format."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    return True, "Valid"


def register_user(username, email, password):
    """Hashes the password and saves the account information directly into MongoDB."""
    is_valid, msg = validate_registration_inputs(username, email, password)
    if not is_valid:
        return False, msg

    try:
        users_collection = get_db_collection()

        # Check if user already exists
        if users_collection.find_one({"email": email.lower()}):
            return False, "An account with this email already exists."
        if users_collection.find_one({"username": username}):
            return False, "Username is already taken."

        # Securely hash password using bcrypt
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        # Insert new user document
        user_document = {
            "username": username,
            "email": email.lower(),
            "password": hashed_password
        }
        users_collection.insert_one(user_document)
        return True, "Registration successful! You can now login."

    except ConnectionFailure:
        return False, "Database connection failed. Ensure your custom MongoDB service is running."
    except Exception as e:
        return False, f"Error: {str(e)}"


def login_user(email, password):
    """Verifies user credentials against the database records."""
    email = email.strip().lower()
    password = password.strip()

    if not email or not password:
        return False, "Email and Password cannot be empty."

    try:
        users_collection = get_db_collection()

        user_record = users_collection.find_one({"email": email})
        if not user_record:
            return False, "Invalid email or password."

        stored_hash = user_record["password"]
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            return True, user_record["username"]
        else:
            return False, "Invalid email or password."

    except ConnectionFailure:
        return False, "Database offline. Check local MongoDB service."