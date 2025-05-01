import discord
from discord.ext import commands, tasks
import logging
import time
from datetime import datetime
import pytz
from utils.db import get_db_connection, release_db_connection

jakarta_tz = pytz.timezone('Asia/Jakarta')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DailyCount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reset_daily_stats.start()  
        logging.info("DailyStats Cog telah diinisialisasi.")

    @tasks.loop(hours=24)  
    async def reset_daily_stats(self):
        conn, resource = await get_db_connection()

        try:
            if not conn:
                logging.error("❌ Gagal mendapatkan koneksi database.")
                return

            today = datetime.now(jakarta_tz).date()

            await conn.execute(
                "DELETE FROM voisa.daily_stats WHERE date < $1",
                today
            )
            logging.info(f"Menghapus data lebih lama dari {today}")

        except Exception as e:
            logging.error(f"Error resetting daily stats: {e}")

        finally:
            await release_db_connection(conn, resource)

    @reset_daily_stats.before_loop
    async def before_reset_daily_stats(self):
        await self.bot.wait_until_ready()

    async def cog_unload(self):
        logging.info("Cog DailyStats akan di-unload.")
        await self.sync_to_db()

async def setup(bot):
    await bot.add_cog(DailyCount(bot))
