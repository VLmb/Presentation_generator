from flask import Flask
from api import api_bp

app = Flask(__name__)

app.register_blueprint(api_bp, url_prefix='/api.neuro_part')

if __name__ == '__main__':
    app.run(debug=True)