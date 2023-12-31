from flask import Flask, request
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from flask_restplus import Api, Resource
import jwt
import datetime
import logging
import os

app = Flask(__name__)
api = Api(app)

ns = api.namespace('todos', description='TODO operations')

SECRET_KEY = '}FR!iP>Ik`kZJi+_iaaacx34F>ZX-u@vF1O%mYlZB2RmMq,Bv+5r\WF5OKT~L::*QwXdC'

user_env = os.environ.get('USER_LIST')

users = {}

if user_env:
    user_pairs = user_env.split(';')
    for pair in user_pairs:
        username, password = pair.split(':')
        users[username] = password
else:
    users = {
        "admin": "admin",
        "vuonghuynh": "admin"
    }

# Middleware for JWT authentication
def generate_jwt_token(username):
    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours = 1) 
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


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


# Endpoint definitions
class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        logging.info('Login attempt for %s', username);

        if not username or not password:
            logging.error('Invalid username or password')
            return {'message': 'Missing username or password'}, 400

        if username not in users or users[username] != password:
            logging.error('Invalid credentials')
            return {'message': 'Invalid credentials'}, 401

        token = generate_jwt_token(username)

        logging.info('Authentication successful for %s', username)
        logging.info('Token: %s', token)

        return {'token': token}, 200

class Trigger(Resource):
    @jwt_required
    def get(self, jobstatus):
        return {'message': f"Job status '{jobstatus}' triggered by user '{request.user}'"}
    

class HealthCheck(Resource):
    def get(self):
        return {'status': 'healthy'}, 200
    

api.add_resource(Login, '/login')
api.add_resource(Trigger, '/trigger/<string:jobstatus>')
api.add_resource(HealthCheck, '/health')

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=8080)
