import MySQLdb as sql
from config import Config
from flask import Flask, render_template, request, g

cfg = Config()
app = Flask(__name__)

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

@app.route("/api/index")
def index():
	'''Render the index page.'''
	conn = getattr(g, 'db', None)
	
	items = {}
	with conn as cursor:
		cursor.execute("select * from stock;")
		items = cursor.fetchall()
	
	return render_template('index.html', it=items)

if __name__ == '__main__':
	app.run(debug=True, port=5000)
