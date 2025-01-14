from flask import abort, request, jsonify
from config import db
import pyodbc

from models import (
    Trail,
    trails_schema,
    trail_schema,
    Feature,
    Trail_feature,
    TrailLocation,
)

def read_all():
    """Retrieve all trails."""
    trails = Trail.query.all()
    return trails_schema.dump(trails)

def read_one(trail_name):
    """Retrieve a single trail by name."""
    trail = Trail.query.filter(Trail.trail_name == trail_name).first()
    if trail:
        return trail_schema.dump(trail)
    else:
        abort(404, f"Trail with trail name '{trail_name}' not found.")

def create():
    try:

        data = request.get_json()
        print(f"Received data: {data}")  # Debugging line


        if isinstance(data, list):
            for trail_data in data:
                process_trail_data(trail_data)
        elif isinstance(data, dict):
            process_trail_data(data)
        else:
            raise ValueError("Invalid data format. Expected a dictionary or list of dictionaries.")

        return {"message": "Trails created successfully"}, 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def process_trail_data(data):
  try:

        required_fields = ["TrailName", "OwnerID"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"'{field}' is required")

        # Create the trail
        new_trail = Trail(
            TrailName=data["TrailName"],
            TrailSummary=data.get("TrailSummary", ""),
            TrailDescription=data.get("TrailDescription", ""),
            Difficulty=data.get("Difficulty", "Unknown"),
            Location=data.get("Location", ""),
            Length=data.get("Length", 0.0),
            ElevationGain=data.get("ElevationGain", 0.0),
            RouteType=data.get("RouteType", ""),
            OwnerID=data["OwnerID"]
        )
        db.session.add(new_trail)
        db.session.commit()

        trail_id = new_trail.TrailID
        print(f"Trail ID: {trail_id}")


        existing_trail = Trail.query.get(trail_id)
        if not existing_trail:
            raise ValueError(f"Trail with ID {trail_id} does not exist in the database.")

        # Add features
        if "Feature" in data and isinstance(data["Feature"], list):
            for feature_data in data["Feature"]:
                feature_name = feature_data.get("Feature_name")
                if feature_name:
                    feature = Feature.query.filter_by(Feature_name=feature_name).first()
                    if not feature:
                        feature = Feature(Feature_name=feature_name)
                        db.session.add(feature)
                    trail_feature = Trail_feature(Trail_id=new_trail.TrailID, Feature_id=feature.Feature_id)
                    db.session.add(trail_feature)
            db.session.commit()

        # Add location points
        if "TrailLocation" in data and isinstance(data["TrailLocation"], list):
            location_points = []
            for location_data in data["TrailLocation"]:
                new_location = TrailLocation(
                    TrailID=trail_id,
                    Latitude=location_data["Latitude"],
                    Longitude=location_data["Longitude"],
                    Description=location_data.get("Description", ""),
                    PointOrder=location_data.get("PointOrder", 0)
                )
                location_points.append(new_location)


            db.session.add_all(location_points)
            db.session.commit()

        return {"message": "Trail and locations created successfully"}, 201

  except Exception as e:
      db.session.rollback()  # Rollback in case of error
      return jsonify({"error": str(e)}), 500

# Add features to a trail
def add_features_to_trail(trail_id, features):
    if not features or not isinstance(features, list):
        return
    feature_objects = []
    for feature_data in features:
        feature_name = feature_data.get("Feature_name")
        if feature_name:
            # Check if the feature  exists
            feature = Feature.query.filter_by(Feature_name=feature_name).first()
            if not feature:
                # Create a new feature
                feature = Feature(Feature_name=feature_name)
                db.session.add(feature)
                db.session.flush()
            # Link the feature to the trail
            feature_objects.append(Trail_feature(Trail_id=trail_id, Feature_id=feature.Feature_id))


    db.session.bulk_save_objects(feature_objects)
    db.session.commit()


# Add locations to a trail
def add_locations_to_trail(trail_id, locations):
    if not locations or not isinstance(locations, list):
        return
    # Create TrailLocation objects in bulk
    new_locations = [
        TrailLocation(
            TrailID=trail_id,
            Latitude=loc.get("Latitude"),
            Longitude=loc.get("Longitude"),
            Description=loc.get("Description", ""),
            PointOrder=loc.get("PointOrder", 0)
        )
        for loc in locations
    ]
    db.session.bulk_save_objects(new_locations)
    db.session.commit()


# Update a trail
def update(TrailID):
    existing_trail = Trail.query.get(TrailID)
    if not existing_trail:
        abort(404, f"Trail with ID '{TrailID}' not found.")

    try:
        data = request.get_json()
        # Update trail fields
        updated_fields = ["TrailName", "TrailSummary", "TrailDescription", "Difficulty",
                          "Location", "Length", "ElevationGain", "RouteType", "OwnerID"]
        for field in updated_fields:
            if field in data:
                setattr(existing_trail, field, data[field])

        db.session.commit()

        existing_trail = Trail.query.get(TrailID)

        # Update features
        if "Feature" in data:
            update_trail_features(TrailID, data["Feature"])

        # Update locations
        if "TrailLocation" in data:
            update_trail_locations(TrailID, data["TrailLocation"])

        return {"message": "Trail updated successfully", "trail": trail_schema.dump(existing_trail)}, 200
    except Exception as e:
        db.session.rollback()
        abort(400, f"Error updating trail: {str(e)}")


# Update features for a trail
def update_trail_features(trail_id, features):
    # Remove all existing features linked to the trail
    Trail_feature.query.filter_by(Trail_id=trail_id).delete()
    db.session.commit()

    # Add new features
    add_features_to_trail(trail_id, features)


# Update locations for a trail
def update_trail_locations(trail_id, locations):
    # Remove all existing locations linked to the trail
    TrailLocation.query.filter_by(TrailID=trail_id).delete()
    db.session.commit()

    # Add new locations
    add_locations_to_trail(trail_id, locations)


def delete(TrailID):
    """Delete an existing trail."""
    existing_trail = Trail.query.get(TrailID)

    if existing_trail:
        db.session.delete(existing_trail)
        db.session.commit()
        return {"message": f"Trail '{TrailID}' successfully deleted."}, 200
    else:
        abort(404, f"Trail with name '{TrailID}' not found.")
