from flask import Flask
from init_database import init_db
from api import api_bp
import logging

# Настройка логирования
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///presentations.db?timeout=60&check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_timeout': 60,
    'pool_recycle': 299,
    'pool_size': 5,
    'max_overflow': 10,
}

init_db(app)

app.register_blueprint(api_bp, url_prefix='/api_backend')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=True)