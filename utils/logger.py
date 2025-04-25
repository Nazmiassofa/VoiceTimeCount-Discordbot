# logger.py
import logging

def setup_logging():
    # Mengkonfigurasi logging
    logging.basicConfig(
        level=logging.INFO,  # Level log, INFO berarti log level yang lebih rendah (seperti DEBUG) akan diabaikan
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),  # Menyimpan log ke file bot.log
            logging.StreamHandler()  # Menampilkan log ke terminal
        ]
    )
