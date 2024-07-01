from datetime import timedelta
from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, unset_jwt_cookies
from helper.db_helper import get_connection

bcrypt = Bcrypt()
auth_endpoints = Blueprint('auth', __name__)

@auth_endpoints.route('/login', methods=['POST'])
def login():
    """Routes for authentication"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Username and password are required"}), 400
    
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM user WHERE username = %s"
    request_query = (username,)
    cursor.execute(query, request_query)
    user = cursor.fetchone()
    
    if not user or not bcrypt.check_password_hash(user['password'], password):
        cursor.close()
        return jsonify({"msg": "Bad username or password"}), 401

    role = user.get('role', '')  # Get the role as a string
    user_id = user.get('id_user')  # Get the user id
    
    # Create access token with username, role, and user_id, valid for 1 day
    expires = timedelta(days=1)
    access_token = create_access_token(identity={'username': username, 'role': role, 'user_id': user_id}, expires_delta=expires)
    
    cursor.close()
    return jsonify({"access_token": access_token, "type": "Bearer", "role": role, "user_id": user_id}), 200

@auth_endpoints.route('/register', methods=['POST'])
def register():
    """Routes for register"""
    data = request.get_json()

    # Validate incoming data
    if not data or 'username' not in data or 'password' not in data or 'email' not in data:
        return jsonify({"msg": "Username, password, and email are required"}), 400

    username = data['username']
    password = data['password']
    email = data['email']
    role = data.get('role', 'umum')  # Get role from JSON data, default to 'umum' if not provided

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Establish database connection
    connection = get_connection()
    cursor = connection.cursor()

    # Prepare and execute SQL query to insert user data
    insert_query = "INSERT INTO user (username, password, email, role) VALUES (%s, %s, %s, %s)"
    request_insert = (username, hashed_password, email, role)

    try:
        cursor.execute(insert_query, request_insert)
        connection.commit()
        new_id = cursor.lastrowid
        cursor.close()

        if new_id:
            return jsonify({"message": "User created successfully", "username": username, "role": role}), 201
        else:
            return jsonify({"message": "Failed to register user"}), 500
    except Exception as e:
        return jsonify({"message": f"Failed to register user: {str(e)}"}), 500


@auth_endpoints.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    username = current_user['username']

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT username, email, no_hp, role FROM user WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()

    cursor.close()
    return jsonify(user), 200

@auth_endpoints.route('/profile/update', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user = get_jwt_identity()
    username = current_user['username']

    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided"}), 400

    # Extract fields to update
    email = data.get('email')
    no_hp = data.get('no_hp')

    if not email and not no_hp:
        return jsonify({"msg": "Email or phone number ('no_hp') must be provided for update"}), 400

    # Update profile in the database
    connection = get_connection()
    cursor = connection.cursor()

    update_query = "UPDATE user SET"
    update_values = []
    if email:
        update_query += " email = %s,"
        update_values.append(email)
    if no_hp:
        update_query += " no_hp = %s,"
        update_values.append(no_hp)

    # Remove trailing comma and add WHERE clause
    update_query = update_query.rstrip(',') + " WHERE username = %s"
    update_values.append(username)

    try:
        cursor.execute(update_query, tuple(update_values))
        connection.commit()
        cursor.close()
        return jsonify({"msg": "Profile updated successfully"}), 200
    except Exception as e:
        return jsonify({"msg": f"Failed to update profile: {str(e)}"}), 500


@auth_endpoints.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({"msg": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200
