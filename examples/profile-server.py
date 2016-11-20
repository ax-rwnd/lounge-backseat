from flask import Flask, jsonify, g
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
	def get(self, user_id):
		db = getattr(g, 'db', None)
		dbreq = "SELECT * FROM profiles WHERE username = %s;"
		with db as cursor:
			cursor.execute(dbreq, (user_id,))

		return {'items':cursor.fetchone()}
	
	def post (self, user_id):
		db = getattr(g, 'db', None)
		with db as cur:
			dbreq = "UPDATE profiles SET email = 'hello.world@gmx.com' WHERE username = %s;"
			cur.execute(dbreq, (user_id,))
		db.commit()


#class Login(Resource):
#	def get (self, secret}:
#		return 
	
api.add_resource(Profile, '/api/profile/<string:user_id>')

if __name__ == '__main__':
	app.run(debug=True)
