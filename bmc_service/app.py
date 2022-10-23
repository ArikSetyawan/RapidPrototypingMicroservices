from unicodedata import name
from flask import Flask, jsonify, abort, request, make_response, render_template
from flask_restful import Api, Resource, reqparse
from peewee import *
import time, datetime

# Setup database
db = "bmc_service.db"
database = SqliteDatabase(db)

class BaseModel(Model):
    class Meta:
        database=database

class Bmc(BaseModel):
    id = AutoField(primary_key=True)
    kodekelompok = TextField()
    type = IntegerField() # 1 for Value Proposition, 2 for Customer Segments, 3 for Customer RelationShip, 4 for Channels, 5 for Key Activities, 6 for Key Resources, 7 for Key Partners, 8 For Cost Structures, 9 for Revenue Streams
    name = CharField()
    backlog = TextField()
    datetime_print = TextField()
    datetime_sql = IntegerField()

def create_tables():
    with database:
        database.create_tables([Bmc])

# Initialize Flask app
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = "this is secret"

class ResourceBmc(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('kodekelompok', location='args', required=True)
        args = parser.parse_args()

		
        if args['kodekelompok'] == "":
            data_return = {
				"data":None,
				"message":"Query Bmc Failed. kodekelompok can't be null or blank",
				"code":"400",
				"error":None
			}
            return make_response(data_return, 400)

        value_propositions = []
        customer_segments = []
        customer_relationships = [] 
        channels = [] 
        key_activities = []
        key_resources = []
        key_partners = []
        cost_structures = []
        revenue_streams = []

        # Get bmc by kodekelompok
        bmc = Bmc.select().where(Bmc.kodekelompok == args["kodekelompok"]).dicts()
        for i in bmc:
            match i['type']:
                case 1:
                    value_propositions.append(i)
                case 2:
                    customer_segments.append(i)
                case 3:
                    customer_relationships.append(i)
                case 4:
                    channels.append(i)
                case 5:
                    key_activities.append(i)
                case 6:
                    key_resources.append(i)
                case 7:
                    key_partners.append(i)
                case 8:
                    cost_structures.append(i)
                case 9:
                    revenue_streams.append(i)
        
        data = {
            "value_propositions":value_propositions,
            "customer_segments":customer_segments,
            "customer_relationships":customer_relationships,
            "channels":channels,
            "key_activities":key_activities,
            "key_resources":key_resources,
            "key_partners":key_partners,
            "cost_structures":cost_structures,
            "revenue_streams":revenue_streams
        }

        data_return = {
            "data":data,
            "message":"Success Get BMC",
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
				"message":"Create BMC Failed. type must be 1 to 9",
				"code":"400",
				"error":None
			}
            return make_response(data_return, 400)

        # Generate Timestamp
        datetime_sql = time.time()
        # Format Timestamp to string
        datetime_print = datetime.datetime.fromtimestamp(datetime_sql).strftime('%Y-%m-%d %H:%M:%S')

        Bmc.create(
            kodekelompok = args['kodekelompok'],
            name = args['name'],
            backlog = args['backlog'],
            type = args['type'],
            datetime_print = datetime_print,
            datetime_sql = datetime_sql
        )

        data_return = {
			"data":None,
			"message":"Success Create Bmc.",
			"code":"200",
			"error":None
		}
        return jsonify(data_return)

api.add_resource(ResourceBmc, '/api/bmc')

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, port=5006)