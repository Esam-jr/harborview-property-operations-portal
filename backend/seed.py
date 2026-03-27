#!/usr/bin/env python3

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import engine
from app.db.base import Base
from app.services.user_service import UserService
from sqlalchemy.orm import sessionmaker

# Create tables if not exist
Base.metadata.create_all(bind=engine)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Add sample users
    sample_users = [
        {"username": "admin", "password": "admin123", "role": "admin"},
        {"username": "manager1", "password": "manager123", "role": "manager"},
        {"username": "clerk1", "password": "clerk123", "role": "clerk"},
        {"username": "dispatcher1", "password": "dispatcher123", "role": "dispatcher"},
        {"username": "resident1", "password": "resident123", "role": "resident"},
    ]

    for user_data in sample_users:
        try:
            user = UserService.create_user(
                db=db,
                username=user_data["username"],
                password=user_data["password"],
                role=user_data["role"]
            )
            print(f"Created user: {user.username} with role {user.role}")
        except Exception as e:
            print(f"Failed to create user {user_data['username']}: {e}")

    db.commit()
    print("Sample users added successfully!")

except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()