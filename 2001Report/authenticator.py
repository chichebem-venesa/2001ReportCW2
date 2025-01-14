import requests
from config import app, db
from models import User  # Import the User model from your ORM

# Authentication URL
auth_url = 'https://web.socem.plymouth.ac.uk/COMP2001/auth/api/users'

# User credentials
email = 'tim@plymouth.ac.uk'
password = 'COMP2001!'

credentials = {
    'email': email,
    'password': password
}


# Fetch role based on email
def fetch_role(user_email):
    try:
        with app.app_context():

            user = db.session.query(User).filter(User.EmailAddress == user_email).first()

            if user:
                return user.Role
            else:
                return None
    except Exception as e:
        print("Error fetching role:", e)
        return None


# Making the POST request for authentication
response = requests.post(auth_url, json=credentials)

if response.status_code == 200:
    try:

        json_response = response.json()
        print("Authenticated successfully:", json_response)


        if isinstance(json_response, list):
            verification_status = json_response[0]
            print(f"Verification status: {verification_status}")


            verified = json_response[1]
            print(f"Verified: {verified}")


            user_email = credentials['email']
            user_role = fetch_role(user_email)

            if user_role:
                print(f"User role is: {user_role}")

                # Role-based access control
                if user_role == "admin":
                    print("Access granted to admin functionalities.")
                    # Admin-specific actions
                elif user_role == "user":
                    print("Access granted to user functionalities.")
                    # User-specific actions
                else:
                    print(f"Access restricted for role: {user_role}")
            else:
                print("User role not found. Access denied.")

        else:
            print("Unexpected response format:", json_response)

    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
else:
    print(f"Authentication failed with status code {response.status_code}")
    print("Response content:", response.text)
