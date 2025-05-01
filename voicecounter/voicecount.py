import discord
import logging
from discord.ext import commands, tasks
import time
from utils.db import get_db_connection, release_db_connection
from datetime import datetime
import pytz

jakarta_tz = pytz.timezone('Asia/Jakarta')

logging = logging.getLogger(__name__)

class Voicecount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_points.start()
        self.track_voice_time.start()
        self.flush_message_buffer.start()

        self.voice_start_times = {}  
        self.message_buffer = {}
        self.voice_count_buffer = {}


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user_id = int(message.author.id)
        username = message.author.name

        # Tambahkan ke buffer
        if user_id in self.message_buffer:
            _, count = self.message_buffer[user_id]
            self.message_buffer[user_id] = (username, count + 1)
        else:
            self.message_buffer[user_id] = (username, 1)

        logging.info(f"[BUFFER] {username} +1 Pesan (total: {self.message_buffer[user_id][1]})")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        current_time = time.time()

        if before.channel is None and after.channel is not None:
            self.voice_start_times[member.id] = current_time
            self.voice_count_buffer[member.id] = self.voice_count_buffer.get(member.id, 0) + 1
            logging.info(f"[BUFFER] {member.name} +1 Gabung Voice (total: {self.voice_count_buffer[member.id]})")

        elif before.channel is not None and after.channel is None:
            if member.id in self.voice_start_times:
                duration = round(current_time - self.voice_start_times.pop(member.id))
                await self.update_voice_time_in_db(member.id, duration)
                await self.update_daily_stats(member.id, member.name, duration)

        elif before.channel is not None and after.channel is not None:
            if member.id in self.voice_start_times:
                duration = round(current_time - self.voice_start_times.pop(member.id))
                await self.update_voice_time_in_db(member.id, duration)
                await self.update_daily_stats(member.id, member.name, duration)

            self.voice_start_times[member.id] = current_time  # Reset time for new channel
            self.voice_count_buffer[member.id] = self.voice_count_buffer.get(member.id, 0) + 1
            logging.info(f"[BUFFER] {member.name} +1 Gabung Voice (total: {self.voice_count_buffer[member.id]})")

    async def update_voice_time_in_db(self, member_id: int, duration: int):
        """Update the voice time in the leveling table."""
        conn, resource = await get_db_connection()
        if not conn:
            logging.error("❌ Gagal mendapatkan koneksi database.")
            return

        try:
            query = """
                UPDATE voisa.leveling
                SET voice_time = voice_time + $1
                WHERE member_id = $2
            """
            await conn.execute(query, duration, int(member_id))  # gunakan str(member_id) jika kolom TEXT
        except Exception as e:
            logging.error(f"❌ Error updating voice time in leveling table for {member_id}: {e}")
        finally:
            await release_db_connection(conn, resource)

    async def update_daily_stats(self, member_id: int, username: str, voice_duration: int):
        """Update the daily stats table for voice time."""
        conn, resource = await get_db_connection()
        if not conn:
            logging.error("❌ Gagal mendapatkan koneksi database.")
            return

        try:
            today = datetime.now(jakarta_tz).date()  # datetime.date object, bisa langsung dipakai oleh asyncpg

            query = """
                INSERT INTO voisa.daily_stats (member_id, date, voice_time, username)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (member_id, date)
                DO UPDATE SET voice_time = voisa.daily_stats.voice_time + $5
            """
            await conn.execute(query, member_id, today, voice_duration, username, voice_duration)
        except Exception as e:
            logging.error(f"❌ Error updating daily stats for member {member_id}: {e}")
        finally:
            await release_db_connection(conn, resource)

    @tasks.loop(seconds=30)  # Update every 30 seconds
    async def track_voice_time(self):
        """Track time every 30 seconds and buffer the data."""
        current_time = time.time()

        for member_id, start_time in list(self.voice_start_times.items()):
            voice_duration = round(current_time - start_time)  # Calculate time spent so far

            user = self.bot.get_user(member_id)
            if not user:
                continue  # skip if user not found

            logging.info(f"({user.name}) + {voice_duration} detik.")

            conn, resource = await get_db_connection()
            if not conn:
                logging.error(f"❌ Gagal koneksi saat update voice_time untuk {member_id}")
                continue

            try:
                # Update voice_time in voisa.leveling
                await conn.execute(
                    "UPDATE voisa.leveling SET voice_time = voice_time + $1 WHERE member_id = $2",
                    voice_duration, int(member_id)
                )

                # Update daily stats
                await self.update_daily_stats(int(member_id), user.name, voice_duration)

                # Reset the start time to the current time
                self.voice_start_times[member_id] = current_time

            except Exception as e:
                logging.error(f"❌ Error updating voice time for member {member_id}: {e}")
            finally:
                await release_db_connection(conn, resource)

    @tasks.loop(minutes=30)
    async def update_points(self):
        try:
            conn, resource = await get_db_connection()
            if not conn:
                logging.error("Database connection failed in update_points.")
                return

            results = await conn.fetch("SELECT member_id, message_count, voice_time, poin FROM voisa.leveling")

            for row in results:
                member_id = str(row["member_id"])
                message_count = row["message_count"]
                voice_time = row["voice_time"]
                current_poin = row["poin"]

                new_poin = message_count + (voice_time // 10)

                if new_poin != current_poin:
                    today = datetime.now(jakarta_tz).date()
                    await conn.execute(
                        """
                        UPDATE voisa.leveling
                        SET poin = $1, last_activity = $2
                        WHERE member_id = $3
                        """,
                        new_poin, today, int(member_id)
                    )

        except Exception as e:
            logging.error(f"Error in update_points: {e}")
        finally:
            await release_db_connection(conn, resource)
        
    @tasks.loop(seconds=120)
    async def flush_voice_count_buffer(self):
        if not self.voice_count_buffer:
            return  # Tidak ada data yang perlu disinkron

        logging.info(f"[Sync] {len(self.voice_count_buffer)} voice join ke-Database")

        conn, res = await get_db_connection()
        if not conn:
            logging.error("❌ Gagal koneksi ke DB saat flush_voice_count_buffer")
            return

        try:
            async with conn.transaction():
                for member_id, count in self.voice_count_buffer.items():
                    query = """
                        UPDATE voisa.leveling
                        SET voice_count = voice_count + $1
                        WHERE member_id = $2
                    """
                    await conn.execute(query, count, int(member_id))

            logging.info("[Berhasil] flush voice_count buffer ke DB.")
            self.voice_count_buffer.clear()

        except Exception as e:
            logging.error(f"❌ Error saat flush_voice_count_buffer: {e}")
        finally:
            await release_db_connection(conn, res)
            
    @tasks.loop(seconds=120)
    async def flush_message_buffer(self):
        if not self.message_buffer:
            return  # Tidak ada yang perlu disinkron

        logging.info(f"[Sync]{len(self.message_buffer)} ke-Database")

        conn, res = await get_db_connection()
        if not conn:
            logging.error("❌ Gagal koneksi ke DB saat flush_message_buffer")
            return

        try:
            async with conn.transaction():
                for member_id, (username, count) in self.message_buffer.items():
                    # Coba update dulu
                    query_update = """
                        UPDATE voisa.leveling
                        SET message_count = message_count + $1,
                            username = $2
                        WHERE member_id = $3
                    """
                    result = await conn.execute(query_update, count, username, member_id)

                    # Jika tidak ada baris diupdate (user belum ada), insert baru
                    if result == "UPDATE 0":
                        query_insert = """
                            INSERT INTO voisa.leveling (member_id, username, message_count, voice_time, poin)
                            VALUES ($1, $2, $3, 0, 0)
                        """
                        await conn.execute(query_insert, member_id, username, count)

            logging.info("[Berhasil] flush message buffer ke DB.")
            self.message_buffer.clear()

        except Exception as e:
            logging.error(f"❌ Error saat flush_message_buffer: {e}")
        finally:
            await release_db_connection(conn, res)

    @update_points.before_loop
    async def before_update_points(self):
        await self.bot.wait_until_ready()
        
    @flush_message_buffer.before_loop
    async def before_flush(self):
        await self.bot.wait_until_ready()

    @flush_voice_count_buffer.before_loop
    async def before_flush_voice(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Voicecount(bot))
