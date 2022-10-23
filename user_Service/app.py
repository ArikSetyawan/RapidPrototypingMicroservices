from flask import Flask, jsonify, abort, request, make_response, render_template
from flask_restful import Api, Resource, reqparse
from peewee import *

# Setup database
db = "user_service.db"
database = SqliteDatabase(db)

class BaseModel(Model):
    class Meta:
        database=database

class User(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField()
    email = CharField(unique=True)
    password = CharField()
    team_id = CharField()

    class Meta:
        table_name= 'users'

class create_tables():
    with database:
        database.create_tables([User])

# Initialize Flask app
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = "this is secret"

class ResourceUsers(Resource):
    def get(self):
            # Setup Params
            parser = reqparse.RequestParser(bundle_errors=True)
            parser.add_argument('id_user', type=int)
            parser.add_argument('email', type=str)
            args = parser.parse_args()

            # Check if params filled
            if args['id_user']  and args['email']:
                # Return if all params filled. Fail because all parameters included
                data_return = {
                    "data":None,
                    "message":"Query User Failed. Too Many Parameter",
                    "code":"400",
                    "error":None
                }
                return jsonify(data_return)
            
            # Return if params id_user selected
            elif args['id_user']:
                user = User.select().where(User.id == args['id_user'])
                if user.exists():
                    user = user.dicts().get()
                    data_return = {
                        "data":{"user":user},
                        "message":"Get User Success",
                        "code":"200",
                        "error":None
                    }
                    return data_return
                else:
                    data_return = {
                        "data":None,
                        "message":"Get User Failed. User not found",
                        "code":"404",
                        "error":None
                    }
                    return make_response(data_return,404)
            
            # Return if params email selected
            elif args['email']:
                user = User.select().where(User.email == args['email'])
                if user.exists():
                    user = user.dicts().get()
                    data_return = {
                        "data":{"user":user},
                        "message":"Get User Success",
                        "code":"200",
                        "error":None
                    }
                    return data_return
                else:
                    data_return = {
                        "data":None,
                        "message":"Get User Failed. User not found",
                        "code":"404",
                        "error":None
                    }
                    return make_response(data_return,404)

            # Return if params not used
            else:
                users = list(User.select().dicts())
                data_return = {
                    "data":{"users":users},
                    "message":"Get All User Success.",
                    "code":"200",
                    "error":None
                }
                return data_return

api.add_resource(ResourceUsers, '/api/users')

if __name__ == "__main__":
    create_tables()
    app.run(debug=True, port=5002)