from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource, reqparse
import requests

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = "this is secret"

# Service Endpoint
AUTH_SERVICE = "http://127.0.0.1:5001/"
USER_SERVICE = "http://127.0.0.1:5002/"
FNF_SERVICE = "http://127.0.0.1:5003/"
CES_SERVICE = "http://127.0.0.1:5004/"
PDC_SERVICE = "http://127.0.0.1:5005/"
BMC_SERVICE = "http://127.0.0.1:5006/"

def checktoken(Header):
    if "Token" not in Header:
        return False
    Token = Header['Token']
    accesstoken = requests.get(f"{AUTH_SERVICE}api/checkaccesstoken", headers={"Token":Token})
    if accesstoken.status_code == 200:
        return True
    else:
        return False

class AuthServiceLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', location='json')
        parser.add_argument('password', location='json')
        args = parser.parse_args()

        # Hit Auth API Login
        login = requests.post(f"{AUTH_SERVICE}api/login", json=args)
        return make_response(login.json(),login.status_code)

class AuthServiceRefreshToken(Resource):
    def get(self):
        # Get Parameters from headers
        header = dict(request.headers)
        # Hit Auth API RefreshToken
        refreshtoken = requests.get(f"{AUTH_SERVICE}api/refresh_token", headers=header)
        return make_response(refreshtoken.json(),refreshtoken.status_code)

class AuthServiceCheckAccessToken(Resource):
    def get(self):
        # Get Parameters from headers
        header = dict(request.headers)
        # Hit Auth API
        accesstoken = requests.get(f"{AUTH_SERVICE}api/checkaccesstoken", headers=header)
        return make_response(accesstoken.json(),accesstoken.status_code)

class AuthServiceCheckRefreshToken(Resource):
    def get(self):
        # Get Parameters from headers
        header = dict(request.headers)
        # Hit Auth API
        refreshtoken = requests.get(f"{AUTH_SERVICE}api/checkrefreshtoken", headers=header)
        return make_response(refreshtoken.json(),refreshtoken.status_code)

class UserService(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id_user', location='args')
        parser.add_argument('email', location='args')
        args = parser.parse_args()

        # Hit User Serive
        user = requests.get(f"{USER_SERVICE}/api/users", params=args)
        
        return make_response(user.json(), user.status_code)

class FnfService(Resource):
    def get(self):
        header = dict(request.headers)
        if not checktoken(header):
            data_return = {
                "data":None,
                "message":"Token Invalid/NotFound",
                "code":"401",
                "error":[{"params":"Token", "message":"Token Invalid/NotFound"}]
            }
            return make_response(data_return,401)
        
        parser = reqparse.RequestParser()
        parser.add_argument('kodekelompok', location='args')
        args = parser.parse_args()

        # Hit F/NF Service
        fnf = requests.get(f"{FNF_SERVICE}/api/fnf", params=args)
        return make_response(fnf.json(), fnf.status_code)

    def post(self):
        header = dict(request.headers)
        if not checktoken(header):
            data_return = {
                "data":None,
                "message":"Token Invalid/NotFound",
                "code":"401",
                "error":[{"params":"Token", "message":"Token Invalid/NotFound"}]
            }
            return make_response(data_return,401)

        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('kodekelompok', location='json')
        parser.add_argument('type', location='json', type=int)
        parser.add_argument('name', location='json')
        parser.add_argument('backlog', location='json')

        args = parser.parse_args()

        # Hit F/NF Service
        fnf = requests.post(f"{FNF_SERVICE}/api/fnf", json=args)
        return make_response(fnf.json(), fnf.status_code)

    def put(self):
        header = dict(request.headers)
        if not checktoken(header):
            data_return = {
                "data":None,
                "message":"Token Invalid/NotFound",
                "code":"401",
                "error":[{"params":"Token", "message":"Token Invalid/NotFound"}]
            }
            return make_response(data_return,401)
        
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('fnf_id', type=int, location='json', required=True)
        parser.add_argument('name', location='json')
        parser.add_argument('description', location='json')
        parser.add_argument('assign_to', location='json')
        parser.add_argument('target_finish', location='json')
        args = parser.parse_args()

        # Hit F/NF Service
        fnf = requests.put(f"{FNF_SERVICE}/api/fnf", json=args)
        return make_response(fnf.json(), fnf.status_code)

    def delete(self):
        header = dict(request.headers)
        if not checktoken(header):
            data_return = {
                "data":None,
                "message":"Token Invalid/NotFound",
                "code":"401",
                "error":[{"params":"Token", "message":"Token Invalid/NotFound"}]
            }
            return make_response(data_return,401)

        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('fnf_id', type=int, location='args', required=True)
        args = parser.parse_args()

        # Hit F/NF Service
        fnf = requests.delete(f"{FNF_SERVICE}/api/fnf", params=args)
        return make_response(fnf.json(), fnf.status_code)

class CesService(Resource):
    def get(self):
        header = dict(request.headers)
        if not checktoken(header):
            data_return = {
                "data":None,
                "message":"Token Invalid/NotFound",
                "code":"401",
                "error":[{"params":"Token", "message":"Token Invalid/NotFound"}]
            }
            return make_response(data_return,401)

        parser = reqparse.RequestParser()
        parser.add_argument('kodekelompok', location='args')
        args = parser.parse_args()

        # Hit Ces Serive
        ces = requests.get(f"{CES_SERVICE}/api/ces", params=args)
        
        return make_response(ces.json(), ces.status_code)

    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('kodekelompok', location='json')
        parser.add_argument('type', location='json', type=int)
        parser.add_argument('name', location='json')
        parser.add_argument('backlog', location='json')
        parser.add_argument('cause_id', location='json')
        parser.add_argument('effect_id', location='json')
        args = parser.parse_args()

        if args['type'] == 1: 
            #Create Cause
            data = args
            data.pop("type")
            data.pop("cause_id")
            data.pop("effect_id")

            # Hit Ces Service
            ces = requests.post(f"{CES_SERVICE}/api/cause", json=data)
            return make_response(ces.json(), ces.status_code)
        
        elif args['type'] == 2:
            # create Effect
            data = args
            data.pop("type")
            data.pop("effect_id")
            # Hit Ces Service
            ces = requests.post(f"{CES_SERVICE}/api/effect", json=data)
            return make_response(ces.json(), ces.status_code)

        elif args['type'] == 3:
            #Create Solution
            data = args
            data.pop("type")
            data.pop("cause_id")

            # Hit Ces Service
            ces = requests.post(f"{CES_SERVICE}/api/solution", json=data)
            return make_response(ces.json(), ces.status_code)
        else:
            data_return = {
                "data":None,
                "message":"Crete CES Failed. type must be in [1,2,3]",
                "code":"401",
                "error":[{"params":"type", "message":"type Incorrect"}]
            }
            return make_response(data_return,401)

    def put(self):
        header = dict(request.headers)
        if not checktoken(header):
            data_return = {
                "data":None,
                "message":"Token Invalid/NotFound",
                "code":"401",
                "error":[{"params":"Token", "message":"Token Invalid/NotFound"}]
            }
            return make_response(data_return,401)

        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('cause_id', location='json', type=int)
        parser.add_argument('effect_id', location='json', type=int)
        parser.add_argument('solution_id', location='json', type=int)
        parser.add_argument('name', location='json', required=True)
        args = parser.parse_args()

        if args['cause_id']:
            data = {
                "cause_id":args['cause_id'],
                "name":args['name']
            }

            # Hit Ces Serive
            update_cause = requests.put(f"{CES_SERVICE}/api/cause", json=data)
            return make_response(update_cause.json(), update_cause.status_code)
        elif args['effect_id']:
            data = {
                "effect_id":args['effect_id'],
                "name":args['name']
            }

            # Hit Ces Serive
            update_effect = requests.put(f"{CES_SERVICE}/api/effect", json=data)
            return make_response(update_effect.json(), update_effect.status_code)
        elif args['solution_id']:
            data = {
                "solution_id":args['solution_id'],
                "name":args['name']
            }

            # Hit Ces Serive
            update_solution = requests.put(f"{CES_SERVICE}/api/solution", json=data)
            return make_response(update_solution.json(), update_solution.status_code)
        else:
            data_return = {
                "data":None,
                "message":"Invalid Data. Must Contain cause_id or effect_id or solution_id",
                "code":"400",
                "error":None
            }
            return make_response(data_return,400)

    def delete(self):
        header = dict(request.headers)
        if not checktoken(header):
            data_return = {
                "data":None,
                "message":"Token Invalid/NotFound",
                "code":"401",
                "error":[{"params":"Token", "message":"Token Invalid/NotFound"}]
            }
            return make_response(data_return,401)

        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('cause_id', location='args', type=int)
        parser.add_argument('effect_id', location='args', type=int)
        parser.add_argument('solution_id', location='args', type=int)
        args = parser.parse_args()

        if args['cause_id']:
            # Hit Ces Serive
            ces = requests.delete(f"{CES_SERVICE}/api/cause", params={"cause_id":args["cause_id"]})
            return make_response(ces.json(), ces.status_code)
        elif args['effect_id']:
            # Hit Ces Serive
            ces = requests.delete(f"{CES_SERVICE}/api/effect", params={"effect_id":args["effect_id"]})
            return make_response(ces.json(), ces.status_code)
        elif args['solution_id']:
            # Hit Ces Serive
            ces = requests.delete(f"{CES_SERVICE}/api/solution", params={"solution_id":args["solution_id"]})
            return make_response(ces.json(), ces.status_code)
        else:
            data_return = {
                "data":None,
                "message":"Invalid Data. Must Contain cause_id or effect_id or solution_id",
                "code":"400",
                "error":None
            }
            return make_response(data_return,400)


class PdcService(Resource):
    def get(self):
        header = dict(request.headers)
        if not checktoken(header):
            data_return = {
                "data":None,
                "message":"Token Invalid/NotFound",
                "code":"401",
                "error":[{"params":"Token", "message":"Token Invalid/NotFound"}]
            }
            return make_response(data_return,401)

        parser = reqparse.RequestParser()
        parser.add_argument('kodekelompok', location='args')
        args = parser.parse_args()

        # Hit Pdc Serive
        pdc = requests.get(f"{PDC_SERVICE}/api/pdc", params=args)
        
        return make_response(pdc.json(), pdc.status_code)
    
    def post(self):
        header = dict(request.headers)
        if not checktoken(header):
            data_return = {
                "data":None,
                "message":"Token Invalid/NotFound",
                "code":"401",
                "error":[{"params":"Token", "message":"Token Invalid/NotFound"}]
            }
            return make_response(data_return,401)

        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('kodekelompok', location='json')
        parser.add_argument('name', location='json')
        parser.add_argument('backlog', location='json')
        parser.add_argument('type', location='json', type=int)
        args = parser.parse_args()

        # Hit PDC Service
        pdc = requests.post(f"{PDC_SERVICE}/api/pdc", json=args)
        return make_response(pdc.json(), pdc.status_code)

    def put(self):
        header = dict(request.headers)
        if not checktoken(header):
            data_return = {
                "data":None,
                "message":"Token Invalid/NotFound",
                "code":"401",
                "error":[{"params":"Token", "message":"Token Invalid/NotFound"}]
            }
            return make_response(data_return,401)

        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('pdc_id', location='json', type=int, required=True)
        parser.add_argument('name', location='json', required=True)
        args = parser.parse_args()

        # Hit PDC Service
        pdc = requests.put(f"{PDC_SERVICE}/api/pdc", json=args)
        return make_response(pdc.json(), pdc.status_code)

    def delete(self):
        header = dict(request.headers)
        if not checktoken(header):
            data_return = {
                "data":None,
                "message":"Token Invalid/NotFound",
                "code":"401",
                "error":[{"params":"Token", "message":"Token Invalid/NotFound"}]
            }
            return make_response(data_return,401)

        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('pdc_id', location='args', type=int, required=True)
        args = parser.parse_args()
        
        # Hit Pdc Serive
        pdc = requests.delete(f"{PDC_SERVICE}/api/pdc", params=args)
        return make_response(pdc.json(), pdc.status_code)

class BmcService(Resource):
    def get(self):
        header = dict(request.headers)
        if not checktoken(header):
            data_return = {
                "data":None,
                "message":"Token Invalid/NotFound",
                "code":"401",
                "error":[{"params":"Token", "message":"Token Invalid/NotFound"}]
            }
            return make_response(data_return,401)

        parser = reqparse.RequestParser()
        parser.add_argument('kodekelompok', location='args')
        args = parser.parse_args()

        # Hit Bmc Serive
        bmc = requests.get(f"{BMC_SERVICE}/api/bmc", params=args)
        
        return make_response(bmc.json(), bmc.status_code)
    
    def post(self):
        header = dict(request.headers)
        if not checktoken(header):
            data_return = {
                "data":None,
                "message":"Token Invalid/NotFound",
                "code":"401",
                "error":[{"params":"Token", "message":"Token Invalid/NotFound"}]
            }
            return make_response(data_return,401)

        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('kodekelompok', location='json')
        parser.add_argument('name', location='json')
        parser.add_argument('backlog', location='json')
        parser.add_argument('type', location='json', type=int)
        args = parser.parse_args()

        # Hit Bmc Service
        bmc = requests.post(f"{BMC_SERVICE}/api/bmc", json=args)
        return make_response(bmc.json(), bmc.status_code)

    def put(self):
        header = dict(request.headers)
        if not checktoken(header):
            data_return = {
                "data":None,
                "message":"Token Invalid/NotFound",
                "code":"401",
                "error":[{"params":"Token", "message":"Token Invalid/NotFound"}]
            }
            return make_response(data_return,401)

        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('bmc_id', location='json', type=int, required=True)
        parser.add_argument('name', location='json', required=True)
        args = parser.parse_args()

        # Hit BMC Service
        bmc = requests.put(f"{BMC_SERVICE}/api/bmc", json=args)
        return make_response(bmc.json(), bmc.status_code)

    def delete(self):
        header = dict(request.headers)
        if not checktoken(header):
            data_return = {
                "data":None,
                "message":"Token Invalid/NotFound",
                "code":"401",
                "error":[{"params":"Token", "message":"Token Invalid/NotFound"}]
            }
            return make_response(data_return,401)

        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('bmc_id', location='args', type=int, required=True)
        args = parser.parse_args()
        
        # Hit BMC Serive
        bmc = requests.delete(f"{BMC_SERVICE}/api/bmc", params=args)
        return make_response(bmc.json(), bmc.status_code)

api.add_resource(AuthServiceLogin, '/login')
api.add_resource(AuthServiceRefreshToken, '/refreshtoken')
api.add_resource(AuthServiceCheckAccessToken, '/checkaccesstoken')
api.add_resource(AuthServiceCheckRefreshToken, '/checkrefreshtoken')
api.add_resource(UserService, '/users')
api.add_resource(FnfService, '/fnf')
api.add_resource(CesService, '/ces')
api.add_resource(PdcService, '/pdc')
api.add_resource(BmcService, '/bmc')

if __name__ == '__main__':
    app.run(debug=True, port=5000)