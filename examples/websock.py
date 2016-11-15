from flask import Flask, render_template
from flask_socketio import SocketIO
from config import Config

cfg = Config()

app = Flask(__name__)
app.config['SECRET_KEY'] = cfg.secret
socketio = SocketIO(app)

@app.route("/api/sock")
def wsock():
	return render_template('wsock.html')

if __name__ == '__main__':
	app.run(debug=True, port=5000)
