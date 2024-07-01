import os
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
from helper.db_helper import get_connection

produk_bp = Blueprint('produk', __name__)

UPLOAD_FOLDER = 'storage/image'  # Direktori untuk menyimpan gambar produk
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Ekstensi file yang diperbolehkan

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@produk_bp.route('/produk', methods=['POST'])
def tambah_produk():
    # Menerima data produk dari form
    id_produk = request.form.get('id_produk')
    id_kategori_produk = request.form.get('id_kategori_produk')
    nama_produk = request.form.get('nama_produk')
    harga = request.form.get('harga')
    stok = request.form.get('stok')
    deskripsi = request.form.get('deskripsi')

    # Cek jika ada file gambar yang dikirim
    if 'gambar' not in request.files:
        return jsonify({'message': 'Gambar tidak ada'}), 400
    
    gambar = request.files['gambar']
    
    # Validasi ekstensi file
    if not allowed_file(gambar.filename):
        return jsonify({'message': 'Ekstensi file tidak diperbolehkan'}), 400

    # Secure filename agar aman dari serangan berbahaya
    filename = secure_filename(gambar.filename)

    # Simpan gambar ke direktori yang ditentukan
    gambar.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    
    # Konstruksi URL gambar (hanya nama file)
    gambar_url = filename

    # Simpan data produk ke database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Produk (id_produk, id_kategori_produk, nama_produk, harga, stok, deskripsi, gambar_url) VALUES (%s, %s, %s, %s, %s, %s, %s)", (id_produk, id_kategori_produk, nama_produk, harga, stok, deskripsi, gambar_url))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        'message': 'Produk telah ditambahkan',
        'produk': {
            'id_produk': id_produk,
            'id_kategori_produk': id_kategori_produk,
            'nama_produk': nama_produk,
            'harga': harga,
            'stok': stok,
            'deskripsi': deskripsi,
            'gambar_url': gambar_url  
        }
    }), 201

@produk_bp.route('/produk', methods=['GET'])
def semua_produk():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    offset = (page - 1) * limit

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Produk LIMIT %s OFFSET %s", (limit, offset))
    results = cursor.fetchall()

    # Menghitung total jumlah produk untuk pagination
    cursor.execute("SELECT COUNT(*) FROM Produk")
    total_products = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    formatted_results = []
    for row in results:
        formatted_results.append({
            'id_produk': row[0],
            'id_kategori_produk': row[1],
            'nama_produk': row[2],
            'harga': row[3],
            'stok': row[4],
            'deskripsi': row[5],
            'gambar_url': f"/storage/show_image/{row[6]}"
        })

    return jsonify({
        'total': total_products,
        'page': page,
        'limit': limit,
        'products': formatted_results
    })

@produk_bp.route('/produk/kategori/<string:nama_kategori>', methods=['GET'])
def produk_by_kategori(nama_kategori):
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    offset = (page - 1) * limit

    conn = get_connection()
    cursor = conn.cursor()

    # Dapatkan id_kategori berdasarkan nama_kategori
    cursor.execute("SELECT id_kategori_produk FROM Kategori_produk WHERE nama_kategori = %s", (nama_kategori,))
    kategori = cursor.fetchone()
    if not kategori:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Kategori tidak ditemukan'}), 404
    
    id_kategori = kategori[0]

    # Query untuk mendapatkan produk berdasarkan id_kategori dengan pagination
    cursor.execute(
        "SELECT p.id_produk, p.id_kategori_produk, p.nama_produk, p.harga, p.stok, p.deskripsi, p.gambar_url "
        "FROM Produk p "
        "JOIN Kategori_produk k ON p.id_kategori_produk = k.id_kategori_produk "
        "WHERE k.nama_kategori = %s LIMIT %s OFFSET %s", 
        (nama_kategori, limit, offset)
    )
    results = cursor.fetchall()

    # Menghitung total jumlah produk untuk pagination
    cursor.execute(
        "SELECT COUNT(*) "
        "FROM Produk p "
        "JOIN Kategori_produk k ON p.id_kategori_produk = k.id_kategori_produk "
        "WHERE k.nama_kategori = %s", 
        (nama_kategori,)
    )
    total_products = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    formatted_results = []
    for row in results:
        formatted_results.append({
            'id_produk': row[0],
            'id_kategori_produk': row[1],
            'nama_produk': row[2],
            'harga': row[3],
            'stok': row[4],
            'deskripsi': row[5],
            'gambar_url': f"/storage/show_image/{row[6]}"
        })

    return jsonify({
        'total': total_products,
        'page': page,
        'limit': limit,
        'products': formatted_results
    })

@produk_bp.route('/produk/<int:id_produk>', methods=['PUT'])
def update_produk(id_produk):
    data = request.get_json()
    nama_produk = data['nama_produk']
    harga = data['harga']
    stok = data['stok']
    deskripsi = data['deskripsi']
    gambar_url = data['gambar_url']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Produk SET nama_produk = %s, harga = %s, stok = %s, deskripsi = %s, gambar_url = %s WHERE id_produk = %s", (nama_produk, harga, stok, deskripsi, gambar_url, id_produk))
    conn.commit()  # Don't forget to commit the transaction
    cursor.close()
    conn.close()
    return jsonify({'message': 'Produk telah diperbarui', 'produk': {'id_produk': id_produk, 'nama_produk': nama_produk, 'harga': harga, 'stok': stok, 'deskripsi': deskripsi, 'gambar_url': gambar_url}}), 200

@produk_bp.route('/produk/<int:id_produk>', methods=['DELETE'])
def hapus_produk(id_produk):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Produk WHERE id_produk = %s", (id_produk,))
    conn.commit()  # Commit the transaction
    cursor.close()
    conn.close()
    return jsonify({'message': 'Produk telah dihapus', 'produk': {'id_produk': id_produk}}), 200
