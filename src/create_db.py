import MySQLdb as sql
from config import Config
import sys

cfg = Config()

def get_connection():
	""" Establish connection to database """
	return sql.connect(host=cfg.host, port=cfg.port, user=cfg.user,\
		passwd=cfg.password, db=cfg.database,\
		charset=cfg.charset)

def create_db ():
	""" Initialize database """
	conn = get_connection()
	create_profiles(conn)
	create_music(conn)
	create_lounges(conn)
	create_playlists(conn)
	create_playlistlines(conn)
	create_chatlines(conn)

def clean_db():
	""" Remove tables from database """
	conn = get_connection()

	with conn as cur:
		cur.execute("DROP TABLE IF EXISTS chatlines;")
		cur.execute("DROP TABLE IF EXISTS playlistlines;")
		cur.execute("DROP TABLE IF EXISTS playlists;")
		cur.execute("DROP TABLE IF EXISTS lounges;")
		cur.execute("DROP TABLE IF EXISTS music;")
		cur.execute("DROP TABLE IF EXISTS profiles;")
	conn.commit()

def create_tests():
	""" Add testdata to the db """
	conn = get_connection()

	with conn as cur:
		cur.execute("INSERT INTO profiles VALUES (default, 'rwnd',\
				'test@test.xxx', TRUE);") 
	conn.commit()
		

def create_profiles(conn):
	""" Create profile table"""

	""" FIELDS
		id		profile id
		username	the shown username
		email		contact infor for the profile
		active		the activation status.
		secret		bcrypt hash
	"""
	with conn as cur:
		qry = "CREATE TABLE IF NOT EXISTS profiles (id INT NOT\
			 NULL AUTO_INCREMENT, username VARCHAR(32) UNIQUE NOT NULL,\
			 email VARCHAR(255) UNIQUE NOT NULL, active BOOLEAN, secret BINARY(60) NOT NULL, PRIMARY KEY(id));"
		cur.execute(qry)

	conn.commit()

def create_music(conn):
	""" Create music->file mapping table """
	
	""" FIELDS
		id	track id
		user_id	owner user id
		title	track title
		path	filesystem path
	"""
	with conn as cur:
		qry = "CREATE TABLE IF NOT EXISTS music (id int,\
			user_id INT, title VARCHAR(255), path varchar(1024),\
			PRIMARY KEY(id), FOREIGN KEY (user_id)\
			REFERENCES profiles(id));"
		cur.execute(qry)
	conn.commit()

def create_lounges(conn):
	""" Create user lounges consisting of
		1 lounge -> 1 playlist
		1 lounge -> many chat messages """

	""" FIELDS
		id	lounge id, same as user?
		
	"""
	with conn as cur:
		qry = "CREATE TABLE IF NOT EXISTS lounges\
			(id INT NOT NULL, PRIMARY KEY(id));"
		cur.execute(qry);
	
	conn.commit()

def create_playlists(conn):
	""" Create lounge->music mapping """

	""" FIELDS
		id	playlist id
		title	name of playlist
		user_id owner user id
	"""
	with conn as cur:
		qry = "CREATE TABLE IF NOT EXISTS playlists\
			(id INT NOT NULL, title VARCHAR(255),\
			user_id INT NOT NULL, PRIMARY KEY(id),\
			FOREIGN KEY(user_id) REFERENCES profiles(id));"
		cur.execute(qry)

	conn.commit()

def create_playlistlines (conn):
	""" Creates linked-list structure for each playlist """

	""" FIELDS
		id		line id, uniqye
		next_id		next track
		playlist_id	belonging to playlist
		music_id	target track
	"""
	with conn as cur:
		qry = "CREATE TABLE IF NOT EXISTS playlistlines\
			(id INT NOT NULL AUTO_INCREMENT, next_id INT NULL,\
			playlist_id INT NOT NULL, music_id INT NOT NULL,\
			PRIMARY KEY(id),\
			FOREIGN KEY(next_id) REFERENCES playlistlines(id),\
			FOREIGN KEY(music_id) REFERENCES music(id));"
		cur.execute(qry)

	conn.commit()

def create_chatlines(conn):
	""" Chats for every lounge. """
	
	""" FIELDS
		user_id		user who posted the message
		lounge_id	the lounge it was posted to
		message		the message
		timestamp	the time when the message was posted
	"""
	with conn as cur:
		qry = "CREATE TABLE IF NOT EXISTS chatlines\
			(user_id INT NOT NULL,\
			lounge_id INT NOT NULL,\
			message VARCHAR(256),\
			time DATETIME,\
			PRIMARY KEY(user_id, lounge_id, time));"
		cur.execute(qry)
	conn.commit()

if __name__ == "__main__":
	if len(sys.argv)!=2:
		print "Usage: create_db.py [create] [clean] [tests]"
	else:
		if sys.argv[1] == 'create':
			create_db()
		elif sys.argv[1] == 'clean':
			clean_db()
		elif sys.argv[1] == 'tests':
			create_tests()
		else:
			print "Unknown command!"
