from flask import Flask, jsonify, abort, request, make_response, render_template
from flask_restful import Api, Resource, reqparse
from peewee import *
import time, datetime

# Setup database
db = "ces_service.db"
database = SqliteDatabase(db)

class BaseModel(Model):
    class Meta:
        database=database

class Cause(BaseModel):
    id = AutoField(primary_key=True)
    kodekelompok = CharField()
    name = CharField()
    backlog = TextField()
    datetime_print = TextField()
    datetime_sql = IntegerField()

class Effect(BaseModel):
    id = AutoField(primary_key=True)
    cause_id = ForeignKeyField(Cause, backref="effects")
    kodekelompok = CharField()
    name = CharField()
    backlog = TextField()
    datetime_print = TextField()
    datetime_sql = IntegerField()

class Solution(BaseModel):
    id = AutoField(primary_key=True)
    effect_id = ForeignKeyField(Effect, backref="solutions")
    kodekelompok = CharField()
    name = CharField()
    backlog = TextField()
    datetime_print = TextField()
    datetime_sql = IntegerField()

def create_tables():
    with database:
        database.create_tables([Cause,Effect,Solution])

# Initialize Flask app
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = "this is secret"

class ResourceCES(Resource):
    def get(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('kodekelompok', location="args", required=True)
        args = parser.parse_args()

        if args['kodekelompok'] == "":
            data_return = {
                "data":None,
                "message":"Query F/NF Failed. kodekelompok can't be null",
                "code":"400",
                "error":None
            }
            return make_response(data_return, 400)

        causes = list(Cause.select().where(Cause.kodekelompok == args['kodekelompok']).dicts())
        
        effects_query = Effect.select().where(Effect.kodekelompok == args['kodekelompok'])
        effects = []
        for i in effects_query:
            data = {}
            data['id'] = i.id
            data['cause_id'] = int(str(i.cause_id))
            data['kodekelompok'] = i.kodekelompok
            data['name'] = i.name
            data['backlog'] = i.backlog
            data['datetime_print'] = i.datetime_print
            data['datetime_sql'] = i.datetime_sql
            get_cause = Cause.select().where(Cause.id == int(str(i.cause_id)))
            get_cause = get_cause.dicts().get()
            data['cause'] = get_cause
            effects.append(data)
        
        solutions_query = Solution.select().where(Solution.kodekelompok == args['kodekelompok'])
        solutions = []
        for i in solutions_query:
            data = {}
            data['id'] = i.id
            data['effect_id'] = int(str(i.effect_id))
            data['kodekelompok'] = i.kodekelompok
            data['name'] = i.name
            data['backlog'] = i.backlog
            data['datetime_print'] = i.datetime_print
            data['datetime_sql'] = i.datetime_sql
            get_effect = Effect.select().where(Effect.id == int(str(i.effect_id)))
            get_effect = get_effect.dicts().get()
            data['effect'] = get_effect
            solutions.append(data)

        data_return = {
			"data":{"causes":causes, "effects":effects, "solutions":solutions},
			"message":"Success Create Cause in CES.",
			"code":"200",
			"error":None
		}
        return jsonify(data_return)

class ResourceCause(Resource):
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('kodekelompok', location='json', required=True)
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('backlog', location='json', required=True)
        args = parser.parse_args()

        # Generate Timestamp
        datetime_sql = time.time()
        # Format Timestamp to string
        datetime_print = datetime.datetime.fromtimestamp(datetime_sql).strftime('%Y-%m-%d %H:%M:%S')

        Cause.create(
            kodekelompok=args['kodekelompok'], 
            name=args['name'], 
            backlog=args['backlog'], 
            datetime_print=datetime_print, 
            datetime_sql=datetime_sql
        )

        data_return = {
			"data":None,
			"message":"Success Create Cause in CES.",
			"code":"200",
			"error":None
		}
        return jsonify(data_return)

    def put(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('cause_id', location='json', type=int, required=True)
        parser.add_argument('name', location='json', required=True)
        args = parser.parse_args()

        update_cause = Cause.update(name=args['name']).where(Cause.id == args['cause_id'])
        update_cause.execute()

        data_return = {
			"data":None,
			"message":"Success Update Cause in CES.",
			"code":"200",
			"error":None
		}
        return jsonify(data_return)

    def delete(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('cause_id', location='args', type=int, required=True)
        args = parser.parse_args()

        # cek if any effect relate to this cause
        effect_check = Effect.select().where(Effect.cause_id == args['cause_id'])
        if effect_check.exists():
            data_return = {
                "data":None,
                "message":"Failed Delete Cause in CES. There still effect that connect to this cause",
                "code":"400",
                "error":None
            }
            return make_response(data_return,400)

        delete_cause = Cause.delete().where(Cause.id == args['cause_id'])
        delete_cause.execute()
        data_return = {
			"data":None,
			"message":"Success Delete Cause in CES.",
			"code":"200",
			"error":None
		}
        return jsonify(data_return)

class ResourceEffect(Resource):
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('kodekelompok', location='json', required=True)
        parser.add_argument('cause_id', location='json', type=int, required=True)
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('backlog', location='json', required=True)
        args = parser.parse_args()

        # Generate Timestamp
        datetime_sql = time.time()
        # Format Timestamp to string
        datetime_print = datetime.datetime.fromtimestamp(datetime_sql).strftime('%Y-%m-%d %H:%M:%S')

        # cek if cause_id with kodekelompok
        cause_check = Cause.select().where((Cause.kodekelompok == args['kodekelompok'])&(Cause.id == args['cause_id']))
        if cause_check.exists():
            Effect.create(
                cause_id = args['cause_id'],
                kodekelompok = args['kodekelompok'],
                name = args['name'],
                backlog = args['backlog'],
                datetime_sql = datetime_sql,
                datetime_print = datetime_print
            )
            data_return = {
                "data":None,
                "message":"Success Create Effect in CES.",
                "code":"200",
                "error":None
            }
            return jsonify(data_return)
        else:
            data_return = {
                "data":None,
                "message":"Failed Create Effect in CES. cause_id and kodekelompok not match",
                "code":"400",
                "error":None
            }
            return make_response(data_return, 400)

    def put(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('effect_id', location='json', type=int, required=True)
        parser.add_argument('name', location='json', required=True)
        args = parser.parse_args()

        update_effect = Effect.update(name=args['name']).where(Effect.id == args['effect_id'])
        update_effect.execute()

        data_return = {
			"data":None,
			"message":"Success Update Effect in CES.",
			"code":"200",
			"error":None
		}
        return jsonify(data_return)

    def delete(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('effect_id', location='args', type=int, required=True)
        args = parser.parse_args()

        # cek if any solution relate to this effect
        solution_check = Solution.select().where(Solution.id == args['effect_id'])
        if solution_check.exists():
            data_return = {
                "data":None,
                "message":"Failed Delete Effect in CES. There still solution that connect to this effect",
                "code":"400",
                "error":None
            }
            return make_response(data_return,400)

        delete_effect = Effect.delete().where(Effect.id == args['effect_id'])
        delete_effect.execute()
        data_return = {
			"data":None,
			"message":"Success Delete Effect in CES.",
			"code":"200",
			"error":None
		}
        return jsonify(data_return)

class ResourceSolution(Resource):
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('kodekelompok', location='json', required=True)
        parser.add_argument('effect_id', location='json', type=int, required=True)
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('backlog', location='json', required=True)
        args = parser.parse_args()

        # Generate Timestamp
        datetime_sql = time.time()
        # Format Timestamp to string
        datetime_print = datetime.datetime.fromtimestamp(datetime_sql).strftime('%Y-%m-%d %H:%M:%S')

        # cek if effect_id with kodekelompok
        effect_check = Effect.select().where((Effect.kodekelompok == args['kodekelompok'])&(Effect.id == args['effect_id']))
        if effect_check.exists():
            Solution.create(
                effect_id = args['effect_id'],
                kodekelompok = args['kodekelompok'],
                name = args['name'],
                backlog = args['backlog'],
                datetime_sql = datetime_sql,
                datetime_print = datetime_print
            )
            data_return = {
                "data":None,
                "message":"Success Create Solution in CES.",
                "code":"200",
                "error":None
            }
            return jsonify(data_return)
        else:
            data_return = {
                "data":None,
                "message":"Failed Create Solution in CES. effect_id and kodekelompok not match",
                "code":"400",
                "error":None
            }
            return make_response(data_return, 400)
    
    def put(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('solution_id', location='json', type=int, required=True)
        parser.add_argument('name', location='json', required=True)
        args = parser.parse_args()

        update_solution = Solution.update(name=args['name']).where(Solution.id == args['solution_id'])
        update_solution.execute()

        data_return = {
			"data":None,
			"message":"Success Update Solution in CES.",
			"code":"200",
			"error":None
		}
        return jsonify(data_return)

    def delete(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('solution_id', location='args', type=int, required=True)
        args = parser.parse_args()

        delete_solution = Solution.delete().where(Solution.id == args['solution_id'])
        delete_solution.execute()
        data_return = {
			"data":None,
			"message":"Success Delete Solution in CES.",
			"code":"200",
			"error":None
		}
        return jsonify(data_return)

api.add_resource(ResourceCES, '/api/ces')
api.add_resource(ResourceCause, '/api/cause')
api.add_resource(ResourceEffect, '/api/effect')
api.add_resource(ResourceSolution, '/api/solution')

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, port=5004)
