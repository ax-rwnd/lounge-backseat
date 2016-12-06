from flask import Flask, jsonify, g, request
from flask_restful import Resource, Api
import MySQLdb as sql

# Load hardcoded config
from config import Config
cfg = Config()

app = Flask(__name__)
api = Api(app)

@app.before_request
def before_request():
	""" Open database and make cursors available to the requests. """
	g.db = sql.connect(host=cfg.dbhost, port=cfg.dbport, user=cfg.user,\
		passwd=cfg.password, db=cfg.database,\
		charset=cfg.charset)

@app.teardown_request
def teardown_request(exception):
	""" Close database at end of request. """
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()
	else:
		print "DB was null!"

class Profile(Resource):
	def get(self, username):
		""" Retrieves profile for usernamse """
		db = getattr(g, 'db', None)

		qry = "SELECT username,email,active FROM\
			profiles WHERE username = %s;"
		with db as cursor:
			cursor.execute(qry, (username,))

		return {'profile':cursor.fetchone()}

class Registration(Resource):
	def post (self):
		obj = request.get_json()

		if (('username' not in obj) or ('email' not in obj) or ('secret' not in obj)):
			return {"status":"MISSING_PARAMS"}

		db = getattr(g, 'db', None)
		with db as cur:
			qry = "INSERT INTO profiles VALUES (default, %s, %s, FALSE, %s);"
			try:
				cur.execute(qry, (obj['username'],obj['email'],obj['secret']))
				db.commit()
				return {"status":"USER_CREATED"}
			except:
				return {"status":"USER_EXISTS"}
	
class Lounge(Resource):
	def get(self, username):
		db = getattr(g, 'db', None)
		result = None
		with db as cur:
			qry = "SELECT id FROM lounges WHERE id=(SELECT id FROM profiles WHERE username=%s);"
			cur.execute(qry, (username,))
			result = cur.fetchall()
		if len(result)>0:
			print "results!"	
			return {"status":"OK"}
		else:
			print "no such lounge!"	
			return {"status":"FAIL"}

api.add_resource(Profile, '/api/profile/<string:username>')
api.add_resource(Registration, '/api/register')
api.add_resource(Lounge, '/api/lounge/<string:username>')

if __name__ == '__main__':
	app.run(host=cfg.host, port=cfg.port, debug=True)
