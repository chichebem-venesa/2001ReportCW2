from config import app, db
from models import User as UserModel, Trail as TrailModel, TrailLocation
from sqlalchemy import text
import pyodbc




# Define user data
user_data = [
    {
        "EmailAddress": "tim@plymouth.ac.uk",
        "Role": "admin",
    },
]

# Define trail data
trail_data = [
    {
        "TrailName": "Plymouth City trail",
        "TrailSummary": "Trail around the town center of Plymouth",
        "TrailDescription": "This trail offers a challenging hike through a dense forest, leading to a viewpoint overlooking a beautiful valley.",
        "Difficulty": "Moderate",
        "Location": "Mountain Range, Valley Trail",
        "Length": 12.5,
        "ElevationGain": 850.0,
        "RouteType": "Loop",
        "OwnerID": 1,
        "locations": [
            {
                "latitude": 35.123456,
                "longitude": -118.123456,
                "description": "Start of the trail",
                "pointOrder": 1
            },
            {
                "latitude": 35.223456,
                "longitude": -118.223456,
                "description": "Scenic viewpoint",
                "pointOrder": 2
            },
            {
                "latitude": 35.323456,
                "longitude": -118.323456,
                "description": "Rest area",
                "pointOrder": 3
            }
        ]
    }
]

with app.app_context():

    conn = db.session.connection()


    print("Attempting to drop foreign key constraint...")
    try:
        conn.execute(text('ALTER TABLE CW2.Trail_Location DROP CONSTRAINT FK__Trail_Loc__Trail__160F4887'))
        print("Foreign key constraint dropped successfully.")
    except Exception as e:
        print(f"Error dropping constraint: {e}")


with app.app_context():
    # Add users to the database
    print("Adding users...")
    for data in user_data:
        new_user = UserModel(EmailAddress=data.get("EmailAddress"), Role=data.get("Role"))
        db.session.add(new_user)

    # Add trails and their corresponding location points to the database
    print("Adding trail data...")
    for data in trail_data:
        new_trail = TrailModel(
            TrailName=data.get("TrailName"),
            TrailSummary=data.get("TrailSummary"),
            TrailDescription=data.get("TrailDescription"),
            Difficulty=data.get("Difficulty"),
            Location=data.get("Location"),
            Length=data.get("Length"),
            ElevationGain=data.get("ElevationGain"),
            RouteType=data.get("RouteType"),
            OwnerID=data.get("OwnerID")
        )
        db.session.add(new_trail)


        db.session.commit()

        # Add associated location points for the trail
        print("Adding location data...")
        for location in data.get("locations"):
            new_location = TrailLocation(
                TrailID=new_trail.TrailID,
                Latitude=location.get("latitude"),
                Longitude=location.get("longitude"),
                Description=location.get("description"),
                PointOrder=location.get("pointOrder")
            )
            db.session.add(new_location)

    # Commit all changes to the database
    print("Committing changes to the database...")
    db.session.commit()
    print("Data committed successfully.")
