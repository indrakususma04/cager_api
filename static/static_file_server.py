from flask import Blueprint, send_from_directory, current_app

static_file_server = Blueprint('static_file_server', __name__)
UPLOAD_FOLDER = 'storage/image'  # Direktori untuk menyimpan gambar produk

@static_file_server.route("/show_image/<path:image_name>", methods=["GET"])
def show_image(image_name):
    """Menampilkan gambar dari direktori statis."""
    return send_from_directory(current_app.root_path, f'{UPLOAD_FOLDER}/{image_name}')
