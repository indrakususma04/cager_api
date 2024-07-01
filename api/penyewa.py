from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from helper.db_helper import get_connection

rental_bp = Blueprint('rental', __name__)

@rental_bp.route('/rental', methods=['GET'])
def get_rentals():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                u.id_user, u.username,
                p.id_produk, p.nama_produk, p.harga,
                r.tanggal_mulai, r.tanggal_selesai, r.status, r.total_harga
            FROM rentals r
            JOIN user u ON r.id_user = u.id_user
            JOIN produk p ON r.id_produk = p.id_produk
        """)

        results = cursor.fetchall()
        cursor.close()
        conn.close()

        # Mengonversi format tanggal
        for result in results:
            result['tanggal_mulai'] = result['tanggal_mulai'].strftime('%Y-%m-%d')
            result['tanggal_selesai'] = result['tanggal_selesai'].strftime('%Y-%m-%d')

        return jsonify(results), 200
    
    except Exception as e:
        print(f"Error: {str(e)}")  # Log error to the server terminal
        return jsonify({'message': f'Error: {str(e)}'}), 500
    
@rental_bp.route('/booking', methods=['GET'])
@jwt_required()
def get_user_bookings():
    try:
        current_user = get_jwt_identity()
        user_id = current_user['user_id'] 
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Query untuk mengambil semua booking berdasarkan ID user yang sedang login
        cursor.execute("""
            SELECT 
                r.id_rental, r.tanggal_mulai, r.tanggal_selesai, r.status, r.total_harga,
                p.id_produk, p.nama_produk, p.harga, p.deskripsi, p.gambar_url
            FROM rentals r
            JOIN produk p ON r.id_produk = p.id_produk
            WHERE r.id_user = %s
        """, (user_id,))

        bookings = cursor.fetchall()
        cursor.close()
        conn.close()

        # Mengonversi format tanggal jika diperlukan
        for booking in bookings:
            booking['tanggal_mulai'] = booking['tanggal_mulai'].strftime('%Y-%m-%d')
            booking['tanggal_selesai'] = booking['tanggal_selesai'].strftime('%Y-%m-%d')

        return jsonify(bookings), 200
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'message': f'Error: {str(e)}'}), 500


@rental_bp.route('/rental/<int:id_rental>', methods=['PUT'])
@jwt_required()
def update_rental_status(id_rental):
    try:
        current_user = get_jwt_identity()
        if not current_user:
            return jsonify({'message': 'Invalid token'}), 401
        
        # Memastikan user yang meminta adalah admin
        if current_user.get('role') != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        conn = get_connection()
        cursor = conn.cursor()

        data = request.get_json()
        new_status = data.get('status')

        if not new_status:
            return jsonify({'message': 'Missing field: status'}), 400

        try:
            cursor.execute("""
                UPDATE rentals
                SET status = %s
                WHERE id_rental = %s
            """, (new_status, id_rental))

            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({'message': 'Rental status updated successfully'}), 200
        
        except Exception as e:
            conn.rollback()
            print(f"Error: {str(e)}")
            return jsonify({'message': f'Error: {str(e)}'}), 500
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'message': f'Error: {str(e)}'}), 500

@rental_bp.route('/sewa', methods=['POST'])
@jwt_required()
def add_rental():
    try:
        current_user = get_jwt_identity()
        if not current_user:
            return jsonify({'message': 'Invalid token'}), 401
      
        id_user = current_user['user_id']

        data = request.get_json()
        required_fields = ['id_produk', 'tanggal_mulai', 'tanggal_selesai', 'total_harga']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing field: {field}'}), 400

        try:
            tanggal_mulai = datetime.strptime(data['tanggal_mulai'], '%Y-%m-%d').date()
            tanggal_selesai = datetime.strptime(data['tanggal_selesai'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Incorrect date format, should be YYYY-MM-DD'}), 400

        # Mengatur default status jika tidak ada dalam data
        status = data.get('status', 'proses')

        conn = get_connection()
        cursor = conn.cursor()

        try:
            # Perbaikan query SQL untuk memastikan tabel dan kolom sesuai dengan struktur yang benar
            query = "SELECT id_user FROM user WHERE id_user = %s"
            cursor.execute(query, (id_user,))
            user = cursor.fetchone()

            if not user:
                return jsonify({'message': 'User not found'}), 404

            # Menggunakan nilai status yang telah disiapkan untuk disisipkan ke dalam database
            cursor.execute("""
                INSERT INTO rentals (id_user, id_produk, tanggal_mulai, tanggal_selesai, status, total_harga)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_user, data['id_produk'], tanggal_mulai, tanggal_selesai, status, data['total_harga']))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Rental added successfully'}), 201
        
        except Exception as e:
            conn.rollback()
            print(f"Error: {str(e)}")
            return jsonify({'message': f'Error: {str(e)}'}), 500
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'message': f'Error: {str(e)}'}), 500
