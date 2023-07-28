from flask import Flask, request
from flask_restful import Api, Resource
import jwt
import datetime

app = Flask(__name__)
api = Api(app)

# This should be kept secret in a real application.
SECRET_KEY = 'your_secret_key'

# Simulated user data for authentication
users = {
    "admin": "admin"
}

# Custom function to generate JWT token
def generate_jwt_token(username):
    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token will be valid for 1 hour
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

# Custom decorator to authenticate endpoints using JWT
def jwt_required(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return {'message': 'Missing JWT token'}, 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user = payload['username']
        except jwt.ExpiredSignatureError:
            return {'message': 'JWT token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Invalid JWT token'}, 401

        return func(*args, **kwargs)

    return wrapper

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {'message': 'Missing username or password'}, 400

        if username not in users or users[username] != password:
            return {'message': 'Invalid credentials'}, 401

        token = generate_jwt_token(username)
        return {'token': token}, 200

class Trigger(Resource):
    @jwt_required
    def get(self, jobstatus):
        # In a real application, you would perform the appropriate actions based on jobstatus
        # For now, let's just return a log message.
        return {'message': f"Job status '{jobstatus}' triggered by user '{request.user}'"}

api.add_resource(Login, '/login')
api.add_resource(Trigger, '/trigger/<string:jobstatus>')

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=8080)
