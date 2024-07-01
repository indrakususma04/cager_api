from flask import Flask
from flask_cors import CORS
from api import api_bp
from flask_jwt_extended import JWTManager

app = Flask(__name__)

# Set up CORS
CORS(app)
app.config['JWT_SECRET_KEY'] = 'my_secret_key_123'

app.config['UPLOAD_FOLDER'] = 'storage/image'

# Set up JWT
jwt = JWTManager(app)

# Register blueprint with URL prefix '/api'
app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
