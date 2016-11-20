import requests
from flask import Flask, render_template

app = Flask(__name__)

api_page = 'http://127.0.0.1:5000/api/profile/'

@app.route('/profile/<string:userid>')
def get_profile(userid):
	return requests.get(api_page+userid).content

@app.route('/profile/update/<string:userid>')
def set_profile(userid):
	return requests.post(api_page+userid, data={'username':'ax-rwnd'}).content

if __name__ == "__main__":
	app.run(debug=True, port=5001)
