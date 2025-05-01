import asyncpg
import asyncio
import logging
import config

# -------------------------------
# Inisialisasi Connection Pool (Async)
# -------------------------------
connection_pool: asyncpg.pool.Pool = None

async def init_db_pool():
    """Inisialisasi pool koneksi asyncpg."""
    global connection_pool
    try:
        connection_pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            host=config.DB_HOST,
            port=config.DB_PORT,
            min_size=1,
            max_size=20
        )
        logging.info("✅ Database connection pool berhasil dibuat.")
    except Exception as e:
        logging.error(f"❌ Gagal membuat database connection pool: {e}")
        connection_pool = None

# -------------------------------
# Fungsi untuk mendapatkan koneksi database
# -------------------------------
async def get_db_connection():
    """Mengambil koneksi dan cursor (simulasi seperti psycopg2)."""
    if connection_pool:
        try:
            conn = await connection_pool.acquire()
            logging.info("--------- [ OPEN_DB_POOL ]")

            return conn, conn 
        except Exception as e:
            logging.error(f"❌ Gagal mendapatkan koneksi database: {e}")
            return None, None
    else:
        logging.error("❌ Connection pool tidak tersedia.")
        return None, None

async def release_db_connection(connection, _):
    """Mengembalikan koneksi ke pool setelah digunakan."""
    try:
        if connection:
            await connection_pool.release(connection)
            logging.info("--------- [ RELEASE_DB_POOL ]")
    except Exception as e:
        logging.error(f"❌ Gagal mengembalikan koneksi ke pool: {e}")

async def close_db_pool():
    """Menutup semua koneksi dalam pool saat bot dimatikan."""
    global connection_pool
    if connection_pool:
        try:
            await connection_pool.close()
            logging.info("✅ Semua koneksi dalam pool telah ditutup.")
        except Exception as e:
            logging.error(f"❌ Gagal menutup connection pool: {e}")
