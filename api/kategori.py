from flask import Blueprint, jsonify, request
from helper.db_helper import get_connection

kategori_bp = Blueprint('kategori', __name__)

@kategori_bp.route('/kategori', methods=['POST'])
def tambah_kategori():
    try:
        data = request.get_json()
        id_kategori_produk = data['id_kategori_produk']
        nama_kategori = data['nama_kategori']
        deskripsi_kategori = data['deskripsi_kategori']
        
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO kategori_produk (id_kategori_produk, nama_kategori, deskripsi_kategori) VALUES (%s, %s, %s)", 
                    (id_kategori_produk, nama_kategori, deskripsi_kategori)
                )
                conn.commit()
        
        return jsonify({
            'message': 'Kategori telah ditambahkan',
            'kategori': {
                'id_kategori_produk': id_kategori_produk,
                'nama_kategori': nama_kategori,
                'deskripsi_kategori': deskripsi_kategori
            }
        }), 201
    except Exception as e:
        print("Error inserting data:", e)
        return jsonify({'message': 'Error inserting data', 'error': str(e)}), 500

@kategori_bp.route('/kategori', methods=['GET'])
def semua_kategori():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM kategori_produk")
                results = cursor.fetchall()
        
        formatted_results = [
            {'id_kategori': row[0], 'nama_kategori': row[1], 'deskripsi_kategori': row[2]} 
            for row in results
        ]
        return jsonify(formatted_results)
    except Exception as e:
        print("Error fetching data:", e)
        return jsonify({'message': 'Error fetching data', 'error': str(e)}), 500

@kategori_bp.route('/kategori/<int:id_kategori>', methods=['PUT'])
def update_kategori(id_kategori):
    try:
        data = request.get_json()
        nama_kategori = data['nama_kategori']
        deskripsi_kategori = data['deskripsi_kategori']
        
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE kategori_produk SET nama_kategori = %s, deskripsi_kategori = %s WHERE id_kategori_produk = %s", 
                    (nama_kategori, deskripsi_kategori, id_kategori)
                )
                conn.commit()
        
        return jsonify({
            'message': 'Kategori telah diperbarui',
            'kategori': {
                'id_kategori': id_kategori,
                'nama_kategori': nama_kategori,
                'deskripsi_kategori': deskripsi_kategori
            }
        }), 200
    except Exception as e:
        print("Error updating data:", e)
        return jsonify({'message': 'Error updating data', 'error': str(e)}), 500

@kategori_bp.route('/kategori/<int:id_kategori>', methods=['DELETE'])
def hapus_kategori(id_kategori):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM kategori_produk WHERE id_kategori_produk = %s", (id_kategori,))
                conn.commit()
        
        return jsonify({'message': 'Kategori telah dihapus', 'kategori': {'id_kategori': id_kategori}}), 200
    except Exception as e:
        print("Error deleting data:", e)
        return jsonify({'message': 'Error deleting data', 'error': str(e)}), 500
