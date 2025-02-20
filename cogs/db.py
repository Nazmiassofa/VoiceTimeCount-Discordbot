import psycopg2
import logging
import config

# Inisialisasi logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_db_connection():
    try:
        # Membuat koneksi ke PostgreSQL
        conn = psycopg2.connect(
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=config.DB_PORT,
            options="-c search_path=voisa"  # Atur schema default menjadi voisa
        )
        cursor = conn.cursor()  # Menambahkan cursor
        return conn, cursor  # Mengembalikan koneksi dan cursor
    except Exception as e:
        logging.error(f"Error saat menghubungkan ke PostgreSQL: {e}")
        return None, None  # Jika terjadi kesalahan, mengembalikan None untuk keduanya
