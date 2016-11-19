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

def clean_db():
	""" Remove tables from database """
	conn = get_connection()

	with conn as cur:
		cur.execute("DROP TABLE IF EXISTS profiles;")
		cur.execute("DROP TABLE IF EXISTS music;")
	conn.commit()

def create_tests():
	conn = get_connection()

	with conn as cur:
		cur.execute("INSERT INTO profiles VALUES (default, 'rwnd', 'test@test.xxx', TRUE);") 
	conn.commit()
		

def create_profiles(conn):
	""" Create profile table"""

	with conn as cur:
		qry = "CREATE TABLE IF NOT EXISTS profiles (id INT NOT\
			 NULL AUTO_INCREMENT, username VARCHAR(32),\
			 email VARCHAR(255), active BOOLEAN, PRIMARY KEY(id));"
		cur.execute(qry)
	conn.commit()

def create_music(conn):
	""" Create music->file mapping table """

	with conn as cur:
		qry = "CREATE TABLE IF NOT EXISTS music (id int,\
			user_id INT, title VARCHAR(255), path varchar(1024),\
			PRIMARY KEY(id), FOREIGN KEY (user_id)\
			REFERENCES profiles(id));"
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
