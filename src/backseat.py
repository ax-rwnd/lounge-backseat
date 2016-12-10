from flask import Flask, jsonify, g, request
from flask_restful import Resource, Api
from bcrypt import hashpw, checkpw, gensalt
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

def authenticate (username, in_session):
	""" Tests uf a user session is authenticated. """
	db = getattr(g, 'db', None)

	with db as cur:
		qry = "SELECT session FROM profiles WHERE username=%s;"

		lines = cur.execute(qry, (username,))
		if lines == 0:
			return {"status":"AUTH_FAIL"}

		session = cur.fetchone()[0]
		if session == in_session:
			return {"status":"AUTH_OK"}
		else:
			return {"status":"AUTH_FAIL"}
	return {"status":"AUTH_ERROR"}

def test_api_key (key):
	""" Test if a given key is in the api-key list. """
	db = getattr(g,'db', None)

	if isinstance(key, unicode):
		key = key.encode('utf-8')

	qry = "SELECT apikey FROM api_keys WHERE apikey=%s;"
	with db as cur:
		return 0 < cur.execute(qry, (key,))

class Profile(Resource):
	def get(self, username):
		""" Retrieves profile for username """
		db = getattr(g, 'db', None)

		qry = "SELECT username,email,active,steamid FROM\
			profiles WHERE username = %s;"
		with db as cursor:
			cursor.execute(qry, (username,))

		return {'profile':cursor.fetchone()}

	def post(self, username=''):
		""" Update profile information. """
		obj = request.get_json()
		db = getattr(g, 'db', None)

		# make sure session was set
		if ('session' not in obj):
			return {'status':'AUTH_FAIL'}

		# make sure the username and password was supplied
		elif ('username' not in obj) or ('secret' not in obj):
			return {'status':'MISSING_PARAMS'}

		# sanitize login
		username = obj['username']
		if isinstance(username, unicode):
			username = username.encode('utf-8')

		secret = obj['secret']
		if isinstance(secret, unicode):
			secret = secret.encode('utf-8')
		
		
		# make sure the user is properly authenticated
		if authenticate(username, obj['session'])['status'] == 'AUTH_FAIL':
			return {'status':'AUTH_FAIL'}
		else:
			#update password
			if ('newsecret' in obj):
				qry = "UPDATE profiles SET secret=%s WHERE username=%s;"

				newsecret = obj['newsecret']
				if isinstance(newsecret, unicode):
					newsecret = newsecret.encode('utf-8')

				hashed = hashpw(newsecret, gensalt())
				with db as cur:
					cur.execute(qry, (hashed, username))
					db.commit()

			# update steamid
			if ('steamid' in obj):
				steamid = obj['steamid']
				if isinstance(steamid, unicode):
					steamid = steamid.encode('utf-8')
				
				qry = "UPDATE profiles SET steam_id=%s WHERE username=%s;"
				with db as cur:
					cur.execute(qry, (steamid, username))
					db.commit()

			return {"status":"USER_UPDATED"}


class Registration(Resource):
	def post (self):
		""" Register a user, requires username, email and a password to be hashed. """
		obj = request.get_json()

		if (('username' not in obj) or ('email' not in obj) or ('secret' not in obj)):
			return {"status":"MISSING_PARAMS"}
		elif (len(obj['username'])<4 or len(obj['username'])>25):
			return {"status":"USER_NAME_LENGTH"}

		db = getattr(g, 'db', None)
		with db as cur:
			qry = "INSERT INTO profiles VALUES (default, %s, %s, FALSE, %s, '', '');"
			try:

				secret = obj['secret']
				if isinstance(secret, unicode):
					secret = secret.encode('utf-8')

				hashed = hashpw(secret, gensalt())
				cur.execute(qry, (obj['username'],obj['email'], hashed))
				db.commit()
				return {"status":"USER_CREATED"}
			except:
				return {"status":"USER_EXISTS"}
	


class Login(Resource):
	def post (self):
		""" Tests some plaintext password against the stored
		database hash, if successful a new token is returned."""
		obj = request.get_json()

		# steam login
		if ('api_key' in obj) and ('steam_id' in obj):
			db = getattr(g,'db', None)
			
			if not test_api_key(obj['api_key']):
				return {"status":"INVALID_API_KEY"+obj['api_key']}

			steam_id = obj['steam_id']
			if isinstance(steam_id, unicode):
				steam_id = steam_id.encode('utf-8')

			with db as cur:
				qry = "UPDATE profiles SET session=%s WHERE steam_id=%s;"
				newsession = hashpw(steam_id, gensalt())
				lines = cur.execute(qry, (newsession, steam_id))
				if lines >= 1:
					qry = "SELECT username, id FROM profiles WHERE steam_id=%s;"
					cur.execute(qry, (steam_id,))
					username, uid = cur.fetchone()
					return {"status":"LOGIN_OK", "session":newsession, "username":username, "uid": uid}

			return {"status":"LOGIN_FAILED"}

		elif ('username' in obj) and ('secret' in obj):
			db = getattr(g,'db', None)

			with db as cur:
				qry = "SELECT secret,id FROM profiles WHERE username=%s;"
				lines = cur.execute(qry, (obj['username'],))

				if lines >= 1:
					secret,uid = cur.fetchone()
					if isinstance(secret, unicode):
						secret = secret.encode('utf-8')

					encpw = obj['secret']
					if isinstance(encpw, unicode):
						encpw = encpw.encode('utf-8')
					
					# Login ok, set session
					if checkpw(encpw, secret):
						qry = "UPDATE profiles SET session=%s WHERE username=%s;"
						newsession = hashpw(secret, gensalt())
						cur.execute(qry, (newsession,obj['username']))
						return {"status":"LOGIN_OK", "session":newsession, "username":obj['username'],"uid":uid}
		else:
			return {"status":"MISSING_PARAMS"}
		return {"status":"LOGIN_FAILED"}

class Auth(Resource):
	def post(self):
		""" Test if the user is logged in. """
		obj = request.get_json()

		if ('username' not in obj) or ('session' not in obj):
			return {"status":"MISSING_PARAMS"}
		
		return authenticate(obj['username'], obj['session'])

class Test(Resource):
	def post(self,user_id):
		obj= request.get_json()
		print "obj:",obj
		db=getattr(g,'db', None)
		with db as cur:
			qry="INSERT INTO playlists VALUES(default, 'qwe',(select id from profiles where id=%s));"
			cur.execute(qry,(user_id,))
			db.commit()
			return{"status":"PLAYLIST_ADDED"}
		

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

		return {'status':'QUERY_OK', 'ids':playlists}

class Music(Resource):
	def get(self, track_id):
		""" Retrieves fully qualified address for requesting music. """
		db = getattr(g, 'db', None)

		with db as cur:
			qry = "SELECT title,path FROM music WHERE id=%s;"
			cur.execute(qry, (track_id,))
			result = cur.fetchone()
			if result != None:
				return {'status':'TRACK_FOUND', 'title':result[0], 'path':result[1]}

		return {'status':'TRACK_UNKNOWN'}


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
			return {"status":"OK"}
		else:
			return {"status":"FAIL"}
class Chat(Resource):
	def post(self):
		""" Retrieve chat messages for this room. """
		db = getattr(g, 'db', None)
		obj = request.get_json()

		if 'lounge_id' in obj and isinstance(obj['lounge_id'], str):
			with db as cur:
				qry = "SELECT chatlines.time, profile.username, chatlines.message FROM chatlines\
				INNER JOIN profiles ON chatlines.lounge_id = %s AND profile.id = chatlines.user_id;"
				cur.execute(qry, (obj['lounge_id'],))


api.add_resource(Activation, '/api/activate/<string:key>')
api.add_resource(Auth, '/api/auth')
api.add_resource(Login, '/api/login')
api.add_resource(Lounge, '/api/lounge/<string:username>')
api.add_resource(Test, '/api/test/<string:user_id>')
api.add_resource(Music, '/api/music/<string:track_id>')
api.add_resource(Playlist, '/api/playlist/<string:user_id>')
api.add_resource(Profile, '/api/profile/<string:username>')
api.add_resource(Registration, '/api/register')

if __name__ == '__main__':
	app.run(host=cfg.host, port=cfg.port, debug=True)
