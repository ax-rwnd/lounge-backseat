from flask import Flask, jsonify, g, request
from flask_restful import Resource, Api
from bcrypt import hashpw, gensalt
import MySQLdb as sql

# Load hardcoded config
from config import Config
cfg = Config()

app = Flask(__name__)
api = Api(app)

@app.before_request
def before_request():
	""" Open database and make cursors available to the requests. """
	g.db = sql.connect(host=cfg.host, port=cfg.port, user=cfg.user,\
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
		""" Register a user, requires username, email and a password to be hashed. """
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
	
class Login(Resource):
	def post (self):
		obj = request.get_json()
		if ('username' not in obj) or ('secret' not in obj):
			return {"status":"MISSING_PARAMS"}
		else:
			db = getattr(g,'db', None)
			with db as cur:
				qry = "SELECT hash WHERE username=%s;"
				cur.execute(qry, (obj['username'],))

				secret = cur.fetchone()
				if False: #TODO continue
					return {"status":"LOGIN_OK", "hash":""}
				else:
					return {"status":"LOGIN_FAILED"}


class Playlist(Resource):
	def get(self, user_id):
		db = getattr(g, 'db', None)
		
		playlists = None
		with db as cur:
			qry = "SELECT id,title FROM playlists WHERE user_id = %s;"
			cur.execute(qry, (user_id,))
			playlists = cur.fetchall()

		if playlists == None:
			return {'status':'QUERY_FAILED'}
		elif len(playlists) == 0:
			return {'status':'NO_PLAYLISTS'}
		else:
			return {'status':'QUERY_OK', 'ids':playlists}


class Activation(Resource):
	def get(self, key):
		return ""
	pass

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
api.add_resource(Activation, '/api/activate/<string:key>')
api.add_resource(Playlist, '/api/playlist/<string:user_id>')

if __name__ == '__main__':
	app.run(debug=True)
