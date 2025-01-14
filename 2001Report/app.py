from flask import Flask, jsonify, render_template, request, abort
import config
from models import Trail, User, Feature, Trail_feature, TrailSchema
from authenticator import fetch_role
import pyodbc


app = config.connex_app
app.add_api(config.basedir / "swagger.yml")


@app.route("/")
def home():
    trail = Trail.query.all()
    return render_template("home.html", trail=trail)


@app.route("/trail/<trail_id>", methods=["GET", "PUT", "DELETE"])
def handle_trail(trail_name):
    if request.method == "GET":
        return get_trail_by_name(trail_name)
    elif request.method == "PUT":
        return update_trail(trail_name)
    elif request.method == "DELETE":
        return delete_trail(trail_name)
    else:
        abort(405, "Method not allowed")


def get_trail_by_name(trail_id):
    trail_instance = Trail.query.filter_by(trail_id=trail_id).first()
    if trail_instance:
        return jsonify(TrailSchema().dump(trail_instance))
    else:
        return {"message": "Trail not found"}, 404


def update_trail(trail_id):
    if not request.is_json:
        return {"message": "Request must be JSON"}, 400

    trail_data = request.get_json()
    trail = Trail.query.filter_by(trail_name=trail_id).first()

    if not trail:
        return {"message": f"Trail with name {trail_id} not found"}, 404

    updated_trail = TrailSchema().load(trail_data, instance=trail, session=config.db.session)
    config.db.session.commit()
    return jsonify(TrailSchema().dump(updated_trail))


def delete_trail(trail_id):
    trail = Trail.query.filter_by(trail_name=trail_id).first()
    if not trail:
        return {"message": f"Trail with name {trail_id} not found"}, 404

    config.db.session.delete(trail)
    config.db.session.commit()
    return '', 204


@app.route('/user', methods=['POST'])
def create_user():
    try:
        # Log incoming request payload
        data = request.get_json()
        return jsonify({"received_data": data})
        print("Received payload:", data)

        # Validate payload
        email = data.get("EmailAddress")
        role = data.get("Role")

        if not email or not role:
            return jsonify({"error": "EmailAddress and Role are required"}), 400

        # Further processing...
        return jsonify({"message": "Payload received successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/update_user', methods=['POST'])
def update_user():
    try:
        # Log incoming request payload
        data = request.get_json()
        return jsonify({"received_data": data})
        print("Received payload:", data)

        # Validate payload
        email = data.get("EmailAddress")
        role = data.get("Role")
        print(requestBody)
        return 'User updated'
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
