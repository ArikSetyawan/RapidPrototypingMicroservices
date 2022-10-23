from flask import Flask, jsonify, abort, request, make_response, render_template
from flask_restful import Api, Resource, reqparse
from peewee import *

# Setup database
db = "fnf_service.db"
database = SqliteDatabase(db)

class BaseModel(Model):
    class Meta:
        database=database

class fnf(BaseModel):
	id = AutoField(primary_key=True)
	kodekelompok = CharField()
	type = IntegerField() # 1 for functional, 2 for non functional
	name = CharField()
	description = TextField(null=True)
	backlog = TextField()
	assign_to = CharField(null=True)
	target_finish = IntegerField(null=True)
	target_finish_print = CharField(null=True)
	status = CharField(null=True) # status progress fitur

class create_tables():
    with database:
        database.create_tables([fnf])

# Initialize Flask app
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = "this is secret"

# CUSTOM FUNCTION
def get_parameter(args):
	parameter = None
	for key,value in args.items():
		if value != None:
			parameter = key
	return parameter

class Resource_fnf(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('kodekelompok', location='args', required=True)
		args = parser.parse_args()

		
		if args['kodekelompok'] == "":
			data_return = {
				"data":None,
				"message":"Query F/NF Failed. kodekelompok can't be null or blank",
				"code":"400",
				"error":None
			}
			return make_response(data_return, 400)
		
		fn = []
		nf = []
		data_fnf = fnf.select().where(fnf.kodekelompok == args['kodekelompok'])
		data_fnf = data_fnf.dicts()
		for i in data_fnf:
			if i['type'] ==1:
				fn.append(i)
			else:
				nf.append(i)

		data_return = {
			"data":{
				'functional':fn,
				'non_functional':nf
			},
			"message":"Success Get FNF",
			"code":"200",
			"error":None
		}
		return jsonify(data_return)
			

	def post(self):
		parser = reqparse.RequestParser(bundle_errors=True)
		parser.add_argument('kodekelompok', location='json', required=True)
		parser.add_argument('type', location='json',type=int, required=True)
		parser.add_argument('name', location='json', required=True)
		parser.add_argument('backlog', location='json', required=True)

		args = parser.parse_args()

		if args['type'] not in [1,2]:
			data_return = {
				"data":None,
				"message":"Create F/NF Failed. type must be 1 or 2",
				"code":"400",
				"error":None
			}
			return make_response(data_return, 400)
		
		# insert fnf
		fnf.create(kodekelompok=args['kodekelompok'],type=args['type'],name=args['name'],backlog=args['backlog'])
		data_return = {
			"data":None,
			"message":"Success Create FNF.",
			"code":"200",
			"error":None
		}
		return jsonify(data_return)

api.add_resource(Resource_fnf,'/api/fnf')

if __name__ == '__main__':
	create_tables()
	app.run(debug=True, port=5003)