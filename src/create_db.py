import MySQLdb as sql
from config import Config
import sys

cfg = Config()

def get_connection():
	""" Establish connection to database """
	return sql.connect(host=cfg.dbhost, port=cfg.dbport, user=cfg.user,\
		passwd=cfg.password, db=cfg.database,\
		charset=cfg.charset)

def create_db ():
	""" Initialize database """
	conn = get_connection()
	create_api_keys()
	create_profiles(conn)
	create_friends(conn)
	#create_lounges(conn)
	create_playlists(conn)
	create_music(conn)
	#create_chatlines(conn)

def drop_table(cur, table):
	print "Dropping",table,"...",	
	cur.execute("DROP TABLE IF EXISTS "+table+";")
	print "Done"

def clean_db():
	""" Remove tables from database """
	conn = get_connection()

	with conn as cur:
		drop_table(cur, "api_keys")
		drop_table(cur, "friends")
		#drop_table(cur, "chatlines")
		drop_table(cur, "music")
		#drop_table(cur, "lounges")
		drop_table(cur, "playlists")
		drop_table(cur, "profiles")
	conn.commit()

def create_api_keys ():
	""" Create table for registered API keys. """
	conn = get_connection()

	""" FIELDS
		key -- the 32-char string used to identify the service
	"""
	print "Setting up api keys...",
	with conn as cur:
		cur.execute("CREATE TABLE IF NOT EXISTS api_keys (apikey VARCHAR(32) NOT NULL, PRIMARY KEY(apikey));")
	conn.commit()
	print "Done"

def create_tests():
	""" Add testdata to the db """
	conn = get_connection()

	print "Creating test data...",
	with conn as cur:
		cur.execute('INSERT INTO api_keys VALUES ("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA");')
	conn.commit()
	print "Done"
		

def create_profiles(conn):
	""" Create profile table"""

	""" FIELDS
		id		profile id
		username	the shown username
		email		contact infor for the profile
		active		the activation status.
		secret		bcrypt hash
		session		session token
		steam_id	steam_id number
		playlist	current lounge playlist
		track		current lounge track
	"""
	print "Creating profiles...",
	with conn as cur:
		qry = "CREATE TABLE IF NOT EXISTS profiles\
			(id INT NOT NULL AUTO_INCREMENT,\
			username VARCHAR(32) UNIQUE NOT NULL,\
			email VARCHAR(255) UNIQUE NOT NULL,\
			active BOOLEAN, secret VARCHAR(60) NOT NULL,\
			steam_id VARCHAR(24), session VARCHAR(60),\
			playlist INT, track INT,\
			PRIMARY KEY(id));"
		cur.execute(qry)
	print "Done"

	conn.commit()

def create_friends(conn):
	""" Create friends table """
	""" FIELDS
		target		the user who consider friend its friend
		friend		the friend in question
	"""
	print "Creating friends...",
	with conn as cur:
		qry = "CREATE TABLE IF NOT EXISTS friends\
			(target INT NOT NULL, friend INT NOT NULL,\
			PRIMARY KEY(target, friend),\
			FOREIGN KEY(target) REFERENCES profiles(id),\
			FOREIGN KEY(friend) REFERENCES profiles(id));"
		cur.execute(qry)
	print "Done"
	conn.commit()

def create_music(conn):
	""" Create music->file mapping table """
	
	""" FIELDS
		id		track id
		user_id		owner user id
		title		track title
		path		filesystem path
		playlist_id	id of the playlist
	"""
	print "Creating music...",
	with conn as cur:
		qry = "CREATE TABLE IF NOT EXISTS music (id int NOT NULL AUTO_INCREMENT,\
			user_id INT NOT NULL, title VARCHAR(255), path varchar(1024),\
			playlist_id INT NOT NULL, PRIMARY KEY(id), FOREIGN KEY (user_id)\
			REFERENCES profiles(id), FOREIGN KEY(playlist_id) REFERENCES playlists(id));"
		cur.execute(qry)
	print "Done"
	conn.commit()

def create_lounges(conn):
	""" Create user lounges consisting of
		1 lounge -> 1 playlist
		1 lounge -> many chat messages """

	""" FIELDS
		id		lounge id
		owner_id	profile that owns lounge
		playlist_id	current playlist
		song_id		current song
		
	"""
	print "Creating lounges...",
	with conn as cur:
		qry = "CREATE TABLE IF NOT EXISTS lounges\
			(id INT NOT NULL AUTO_INCREMENT, PRIMARY KEY(id));"#,\
			#owner_id INT NOT NULL,\
			#playlist_id INT NOT NULL,\
			#song_id INT NOT NULL, PRIMARY KEY(id),\
			#FOREIGN KEY(owner_id) REFERENCES profiles(id),\
			#FOREIGN KEY(playlist_id) REFERENCES playlists(id),\
			#FOREIGN KEY(song_id) REFERENCES music(id));"
		cur.execute(qry);
	conn.commit()
	print "Done"

def create_playlists(conn):
	""" Create lounge->music mapping """

	""" FIELDS
		id	playlist id
		title	name of playlist
		user_id owner user id
	"""
	print "Creating playlists...",
	with conn as cur:
		qry = "CREATE TABLE IF NOT EXISTS playlists\
			(id INT NOT NULL AUTO_INCREMENT, title VARCHAR(255),\
			user_id INT NOT NULL, PRIMARY KEY(id),\
			FOREIGN KEY(user_id) REFERENCES profiles(id));"
		cur.execute(qry)
	conn.commit()
	print "Done"

def create_playlistlines (conn):
	""" Creates linked-list structure for each playlist """

	""" FIELDS
		id		line id, unique
		next_id		next track
		playlist_id	belonging to playlist
		music_id	target track
	"""
	print "Creating playlistlines...",
	with conn as cur:
		qry = "CREATE TABLE IF NOT EXISTS playlistlines\
			(id INT NOT NULL AUTO_INCREMENT, next_id INT NULL,\
			playlist_id INT NOT NULL, music_id INT NOT NULL,\
			PRIMARY KEY(id),\
			FOREIGN KEY(next_id) REFERENCES playlistlines(id),\
			FOREIGN KEY(music_id) REFERENCES music(id));"
		cur.execute(qry)
	conn.commit()
	print "Done"

def create_chatlines(conn):
	""" Chats for every lounge. """
	
	""" FIELDS
		user_id		user who posted the message
		lounge_id	the lounge it was posted to
		message		the message
		timestamp	the time when the message was posted
	"""
	print "Creating chatlines...",
	with conn as cur:
		qry = "CREATE TABLE IF NOT EXISTS chatlines\
			(user_id INT NOT NULL,\
			lounge_id INT NOT NULL,\
			message VARCHAR(256),\
			time DATETIME,\
			PRIMARY KEY(user_id, lounge_id, time),\
			FOREIGN KEY(user_id) REFERENCES profiles(id),\
			FOREIGN KEY(lounge_id) REFERENCES lounges(id));"
		cur.execute(qry)
	conn.commit()
	print "Done"

if __name__ == "__main__":
	if len(sys.argv)!=2:
		print "Usage: create_db.py [create] [clean] [tests]"
	else:
		if sys.argv[1] == 'create':
			create_db()
		elif sys.argv[1] == 'clean':
			clean_db()
		elif sys.argv[1] == 'recreate':
			clean_db()
			create_db()
		elif sys.argv[1] == 'tests':
			create_tests()
		else:
			print "Unknown command!"
