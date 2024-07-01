from flask import Blueprint
from api.kategori import kategori_bp
from api.produk import produk_bp
from api.auth import auth_endpoints
from api.penyewa import rental_bp
from static.static_file_server import static_file_server
# Memperbaiki: Import blueprint penyewa

api_bp = Blueprint('api', __name__)

# Register blueprints
api_bp.register_blueprint(kategori_bp)
api_bp.register_blueprint(produk_bp)
api_bp.register_blueprint(auth_endpoints)
api_bp.register_blueprint(rental_bp)
api_bp.register_blueprint(static_file_server, url_prefix='/storage')
