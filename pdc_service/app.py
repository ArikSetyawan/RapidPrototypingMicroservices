from unicodedata import name
from flask import Flask, jsonify, abort, request, make_response, render_template
from flask_restful import Api, Resource, reqparse
from peewee import *
import time, datetime

# Setup database
db = "pdc_service.db"
database = SqliteDatabase(db)

class BaseModel(Model):
    class Meta:
        database=database

class Pdc(BaseModel):
    id = AutoField(primary_key=True)
    kodekelompok = TextField()
    type = IntegerField() # 1.platform_owners, 2.platform_stakeholders, 3. peers, 4.partners, 5.transactions, 6.channel_and_contexts, 7.services, 8.value_propositions, 9.infrastructure_and_components
    name = CharField()
    backlog = TextField()
    datetime_print = TextField()
    datetime_sql = IntegerField()

def create_tables():
    with database:
        database.create_tables([Pdc])

# Initialize Flask app
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = "this is secret"

class ResourcePdc(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('kodekelompok', location='args', required=True)
        args = parser.parse_args()

		
        if args['kodekelompok'] == "":
            data_return = {
				"data":None,
				"message":"Query PDC Failed. kodekelompok can't be null or blank",
				"code":"400",
				"error":None
			}
            return make_response(data_return, 400)

        platform_owners = [] 
        platform_stakeholders = []
        peers = [] 
        partners = [] 
        transactions = []
        channel_and_contexts = []
        services = []
        value_propositions = []
        infrastructure_and_components = []

        # Get pdc by kodekelompok
        pdc = Pdc.select().where(Pdc.kodekelompok == args["kodekelompok"]).dicts()
        for i in pdc:
            match i['type']:
                case 1:
                    platform_owners.append(i)
                case 2:
                    platform_stakeholders.append(i)
                case 3:
                    peers.append(i)
                case 4:
                    partners.append(i)
                case 5:
                    transactions.append(i)
                case 6:
                    channel_and_contexts.append(i)
                case 7:
                    services.append(i)
                case 8:
                    value_propositions.append(i)
                case 9:
                    infrastructure_and_components.append(i)
        
        data = {
            "platform_owners":platform_owners,
            "platform_stakeholders":platform_stakeholders,
            "peers":peers,
            "partners":partners,
            "transactions":transactions,
            "channel_and_contexts":channel_and_contexts,
            "services":services,
            "value_propositions":value_propositions,
            "infrastructure_and_components":infrastructure_and_components
        }

        data_return = {
            "data":data,
            "message":"Success Get PDC",
            "code":"200",
            "error":None
        }
        return jsonify(data_return)

    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('kodekelompok', location='json', required=True)
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('backlog', location='json', required=True)
        parser.add_argument('type', location='json', required=True, type=int)

        args = parser.parse_args()

        if args['type'] not in [1,2,3,4,5,6,7,8,9]:
            data_return = {
				"data":None,
				"message":"Create PDC Failed. type must be 1 to 9",
				"code":"400",
				"error":None
			}
            return make_response(data_return, 400)

        # Generate Timestamp
        datetime_sql = time.time()
        # Format Timestamp to string
        datetime_print = datetime.datetime.fromtimestamp(datetime_sql).strftime('%Y-%m-%d %H:%M:%S')

        Pdc.create(
            kodekelompok = args['kodekelompok'],
            name = args['name'],
            backlog = args['backlog'],
            type = args['type'],
            datetime_print = datetime_print,
            datetime_sql = datetime_sql
        )

        data_return = {
			"data":None,
			"message":"Success Create PDC.",
			"code":"200",
			"error":None
		}
        return jsonify(data_return)

api.add_resource(ResourcePdc, '/api/pdc')

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, port=5005)