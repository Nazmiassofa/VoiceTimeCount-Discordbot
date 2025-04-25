import discord
import time
import pytz

from discord.ext import commands, tasks
from datetime import datetime
from cogs.db import get_db_connection
from utils.logger import setup_logging

jakarta_tz = pytz.timezone('Asia/Jakarta') # Change this with your local timezone
setup_logging()

class DailyCounter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reset_daily_stats.start() 

    @tasks.loop(hours=24)  # Reset daily statistic
    async def reset_daily_stats(self):
        try:
            conn, cursor = get_db_connection()

            today = datetime.now(jakarta_tz).date()  # Mendapatkan tanggal hari ini
            cursor.execute("DELETE FROM 'DAILY_TABLE' WHERE date < %s", (today,))
            conn.commit()
            logging.info(f"Removing data longer than {today}")

        except Exception as e:
            logging.error(f"Error resetting daily stats: {e}")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @reset_daily_stats.before_loop
    async def before_reset_daily_stats(self):
        await self.bot.wait_until_ready()

    async def cog_unload(self):
        logging.info("Unloading DailyCounters Cog.")
        await self.sync_to_db()

async def setup(bot):
    await bot.add_cog(DailyCounter(bot))
    logging.info("Cog DailyCounter has been loaded.")
