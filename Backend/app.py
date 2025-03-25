from flask import Flask
from init_database import init_db
from api import api_bp

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///presentations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)

app.register_blueprint(api_bp, url_prefix='/api_backend')

if __name__ == '__main__':
    app.run(debug=True, port=5000)