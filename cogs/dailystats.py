import discord
from discord.ext import commands, tasks
import logging
import time
from datetime import datetime
import pytz
from cogs.db import get_db_connection

# Zona Waktu Jakarta
jakarta_tz = pytz.timezone('Asia/Jakarta')

# Pengaturan Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DailyStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reset_daily_stats.start()  # Mulai tugas untuk mereset statistik setiap hari
        logging.info("DailyStats Cog telah diinisialisasi.")

    @tasks.loop(hours=24)  # Reset statistik harian setiap hari
    async def reset_daily_stats(self):
        try:
            conn, cursor = get_db_connection()

            # Hapus statistik harian untuk hari sebelumnya
            today = datetime.now(jakarta_tz).date()  # Mendapatkan tanggal hari ini
            cursor.execute("DELETE FROM voisa.daily_stats WHERE date < %s", (today,))
            conn.commit()
            logging.info(f"Menghapus data lebih lama dari {today}")

        except Exception as e:
            logging.error(f"Error resetting daily stats: {e}")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @reset_daily_stats.before_loop
    async def before_reset_daily_stats(self):
        # Menunggu hingga bot siap
        await self.bot.wait_until_ready()

    async def cog_unload(self):
        """Dipanggil saat cog di-unload. Membersihkan data yang belum tersimpan."""
        logging.info("Cog DailyStats akan di-unload.")
        await self.sync_to_db()

async def setup(bot):
    await bot.add_cog(DailyStats(bot))
    logging.info("Cog DailyStats telah di-load ke bot.")
