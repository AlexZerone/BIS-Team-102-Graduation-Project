"""
Script to initialize application status values in the database
"""
from extensions import mysql
from models import execute_query, get_records

def initialize_application_statuses():
    """Initialize the application_statuses table with standard status values"""
    try:
        # Check if table exists first
        try:
            existing_statuses = get_records("SELECT * FROM application_statuses LIMIT 1")
            
            if existing_statuses is None or len(existing_statuses) == 0:
                print("Initializing application statuses...")
                # Insert standard application status values
                status_values = [
                    (1, 'Pending'),
                    (2, 'Under Review'),
                    (3, 'Accepted'),
                    (4, 'Rejected')
                ]
                
                for status_id, name in status_values:
                    execute_query(
                        "INSERT INTO application_statuses (StatusID, Name) VALUES (%s, %s)",
                        (status_id, name)
                    )
                print("Application statuses initialized successfully.")
            else:
                print(f"Application statuses already exist in database.")
                
        except Exception as e:
            if "Table 'flask0.application_statuses' doesn't exist" in str(e):
                print("Application statuses table does not exist yet. Will be created when database is initialized.")
            else:
                raise
    
    except Exception as e:
        print(f"Error initializing application statuses: {str(e)}")

if __name__ == "__main__":
    # This can be run as a standalone script
    from flask import Flask
    from config import Config
    
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)
    mysql.init_app(app)
    
    with app.app_context():
        initialize_application_statuses()
