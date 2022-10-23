from flask import Flask, jsonify, abort, request, make_response, render_template
from flask_restful import Api, Resource, reqparse
import jwt, datetime, requests

# Initialize Flask app
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = "this is secret"

# User Service Endpoint
userServiceEndpoint = 'http://127.0.0.1:5002/api/users'

class AuthHandler():
    secret = app.config['SECRET_KEY']
    # GenerateEncodeToken
    def encode_token(self, content, type):
        payload = {
            "iss":content,
            "type":type
        }
        if type == "access_token":
            payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(hours=720)
        else:
            payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(hours=720)

        jwt_token = jwt.encode(payload, self.secret, algorithm="HS256")
        
        # If using #Python 3.8.10^
        # return jwt_token.decode('UTF-8')
        # Else
        return jwt_token

    # Create Token
    def encode_login_token(self, content):
        access_token = self.encode_token(content, "access_token")
        refresh_token = self.encode_token(content, "refresh_token")

        login_token = {
            "access_token":access_token,
            "refresh_token":refresh_token
        }
        return login_token

    def encode_update_token(self, content):
        access_token = self.encode_token(content, "access_token")

        update_token = dict(
            access_token=f"{access_token}"
        ) 
        return update_token

    # Decode Token
    def decode_access_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            if payload['type'] != "access_token":
                data_return = {
                    "data":None,
                    "message":"Token Invalid",
                    "code":"401",
                    "error":[{"params":"Token", "message":"Token Invalid"}]
                }
                response = make_response(data_return,401)
                return abort(response)
            return payload['iss']
        except jwt.ExpiredSignatureError:
            data_return = {
                "data":None,
                "message":"Token Expired",
                "code":"401",
                "error":[{"params":"Token", "message":"Token Expired"}]
                
            }
            response = make_response(data_return,401)
            return abort(response)
        except jwt.InvalidTokenError as e:
            data_return = {
                "data":None,
                "message":"Token Invalid",
                "code":"401",
                "error":[{"params":"Token", "message":"Token Invalid"}]
                
            }
            response = make_response(data_return,401)
            return abort(response)

    # Decode Token
    def decode_refresh_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            if payload['type'] != "refresh_token":
                data_return = {
                    "data":None,
                    "message":"Token Invalid",
                    "code":"401",
                    "error":[{"params":"Token", "message":"Token Invalid"}]
                }
                response = make_response(data_return,401)
                return abort(response)
            return payload['iss']
        except jwt.ExpiredSignatureError:
            data_return = {
                "data":None,
                "message":"Token Expired",
                "code":"401",
                "error":[{"params":"Token", "message":"Token Expired"}]
            }
            response = make_response(data_return,401)
            return abort(response)
        except jwt.InvalidTokenError as e:
            data_return = {
                "data":None,
                "message":"Token Invalid",
                "code":"401",
                "error":[{"params":"Token", "message":"Token Invalid"}]
            }
            response = make_response(data_return,401)
            return abort(response)

    # Check access Token
    def auth_access_wrapper(self, token):
        return self.decode_access_token(token)

    # Check refresh Token
    def auth_refresh_wrapper(self, token):
        return self.decode_refresh_token(token)

# initiate JWT AuthHandler
auth_handler=AuthHandler()

class AuthentificationUser(Resource):
    def post(self):
        # Setup parameters
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('email', location='json')
        parser.add_argument('password', location='json')
        args = parser.parse_args()

        # List for error message
        error_message = []
        # Check if required argument is not null
        if args['email'] == None or args['password'] == None:
            if args['email'] == None:
                error = {"params":"email","message":"Email Missing"}
                error_message.append(error)
            if args['password'] == None:
                error = {"params":"password","message":"Password Missing"}
                error_message.append(error)
            data_return = {
                "data":None,
                "message":"Login Failed",
                "code":"400",
                "error":error_message
            }
            return make_response(data_return,400)

        # get user
        get_user = requests.get(userServiceEndpoint, params={'email':args['email']})
        # Check if user found
        if get_user.status_code == 200:
            # Get user data
            user = get_user.json()['data']['user']
            # Check if password is correct
            if user['password'] != args['password']:
                # Return if password is not correct
                data_return = {
                    "data":None,
                    "message":"Login Failed. Email or Password Wrong",
                    "code":"401",
                    "error":None
                }
                return make_response(data_return,401)
            
            # Return if password is correct
            payload_content = {"user_id":user['id'],"team_id":user['team_id']}
            # Generate Token
            token = auth_handler.encode_login_token(payload_content)
            data_return = {
                "data":{"Token":token,"User":user},
                "message":"Login Success",
                "code":"200",
                "error":None
            }
            return jsonify(data_return)
        
        # Return if user with that email is not found
        elif get_user.status_code == 404:
            data_return = {
                "data":None,
                "message":"Login Failed. Email or Password Wrong",
                "code":"401",
                "error":None
            }
            return make_response(data_return,401)
        
        # User Service ERROR
        else:
            data_return = {
                "data":None,
                "message":"Login Failed. User Service Error",
                "code":"500",
                "error":None
            }
            return make_response(data_return,500)

class Resource_Refresh_Token(Resource):
    def get(self):
        # Get Parameters from headers
        header = dict(request.headers)
        # Check if "Token" in headers
        if "Token" not in header:
            data_return = {
                "data":None,
                "message":"Token Not Found",
                "code":"400",
                "error":[{"params":"Token", "message":"Token Missing"}]
            }
            return make_response(data_return,400)
        # Get Token from headers
        token = header['Token']
        # Validate Token
        auth = auth_handler.auth_refresh_wrapper(token)
        # Generate new_token
        New_Token = auth_handler.encode_login_token(auth)
        data_return = {
            "data":{"Token":New_Token},
            "message":"Refresh Token Success",
            "code":"200",
            "error":None
        }
        return jsonify(data_return)

class Resource_CheckAccessToken(Resource):
    def get(self):
        # Get Parameters from headers
        header = dict(request.headers)
        # Check if "Token" in headers
        if "Token" not in header:
            data_return = {
                "data":None,
                "message":"Token Not Found",
                "code":"400",
                "error":[{"params":"Token", "message":"Token Missing"}]
            }
            return make_response(data_return,400)
        # Get Token from headers
        token = header['Token']
        # Validate Token
        auth = auth_handler.auth_access_wrapper(token)
        data_return = {
            "data":{"access_token":token,"data":auth},
            "message":"Access Token Valid",
            "code":"200",
            "error":None
        }
        return jsonify(data_return)

class Resource_CheckRefreshToken(Resource):
    def get(self):
        # Get Parameters from headers
        header = dict(request.headers)
        # Check if "Token" in headers
        if "Token" not in header:
            data_return = {
                "data":None,
                "message":"Token Not Found",
                "code":"400",
                "error":[{"params":"Token", "message":"Token Missing"}]
            }
            return make_response(data_return,400)
        # Get Token from headers
        token = header['Token']
        # Validate Token
        auth = auth_handler.auth_refresh_wrapper(token)
        data_return = {
            "data":{"refresh_token":token, "data":auth},
            "message":"Refresh Token Valid",
            "code":"200",
            "error":None
        }
        return jsonify(data_return)

api.add_resource(AuthentificationUser, '/api/login')
api.add_resource(Resource_Refresh_Token, "/api/refresh_token")
api.add_resource(Resource_CheckAccessToken, '/api/checkaccesstoken')
api.add_resource(Resource_CheckRefreshToken, '/api/checkrefreshtoken')

if __name__ == "__main__":
    app.run(debug=True, port=5001)