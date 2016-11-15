class Config:
	''' Container for the various configurations required within the backend.
	    The options are simply parsed by importing and instantiating this
	    class. '''

	user = None
	password = None
	host = None
	port = None
	secret = None
	database = None
	charset = None	

	def __init__(self):
		self.user = 'webuser'
		self.password = 'SecretsInProd'
		self.host = "127.0.0.1"
		self.port = 3306
		self.secret = 'SuperSecretKey'
		self.database = 'loungematic'
		self.charset = 'utf8'
