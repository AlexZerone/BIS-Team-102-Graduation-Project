from app import create_app
from models import get_records

app = create_app()

with app.app_context():
    try:
        users = get_records("SELECT UserID, Email, UserType, Status FROM users LIMIT 5")
        for u in users:
            print(f"- ID: {u['UserID']}, Email: {u['Email']}, Type: {u['UserType']}, Status: {u['Status']}")
    except Exception as e:
        print(f"Database connection error: {e}")
