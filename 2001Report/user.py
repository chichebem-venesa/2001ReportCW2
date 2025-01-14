from flask import abort, make_response, request, jsonify
from sqlalchemy.sql.functions import user

from config import db
from models import User, user_schema

def read_all_user():
    """Retrieve all users."""
    try:
        users = User.query.all()
        if not users:
            print("No users found")
            return jsonify([]), 200

        user_list = [
            {
                "EmailAddress": user.EmailAddress,
                "Role": user.Role
            }
            for user in users
        ]
        print(user_list)
        return jsonify(user_list), 200
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}, 500

def read_one_user(email):
    """Retrieve a single user by email."""
    user = User.query.get(email)
    if user is not None:
        return user_schema.dump(user)
    else:
        abort(404, f"User with email '{email}' not found.")

def create_user():
    try:
        # Extract data from request
        data = request.get_json()
        email = data.get("EmailAddress")
        role = data.get("Role")

        # Validate required fields
        if not email or not role:
            return jsonify({"error": "EmailAddress and Role are required fields"}), 400

        # Check if user already exists
        existing_user = User.query.filter_by(EmailAddress=email).first()
        if existing_user:
            return jsonify({"error": "User with this email already exists"}), 400

        # Create and add new user
        new_user = User(EmailAddress=email, Role=role)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User created successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def update_user(EmailAddress):
    """Update an existing user by email."""
    try:
        # Fetch the user by email
        user = User.query.filter_by(EmailAddress=EmailAddress).first()
        if not user:
            return {"message": "User not found"}, 404

        # Extract data from request
        data = request.get_json()
        email = data.get("EmailAddress")
        role = data.get("Role")

        # Update user details
        user.Role = role
        db.session.commit()

        return {"message": "User updated successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def delete_user(EmailAddress):
 print(f"EmailAddress received: {EmailAddress}")
 try:
    """Delete an existing trail."""
    existing_user = User.query.filter_by(EmailAddress=EmailAddress).first()

    if existing_user:
        db.session.delete(existing_user)
        db.session.commit()
        return {"message": f"User '{EmailAddress}' successfully deleted."}, 200
    else:
        abort(404, f"User with email '{EmailAddress}' not found.")
 except Exception as e:
     print(f"Error: {e}")
     return {"error": str(e)}, 500