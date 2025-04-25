import discord
import logging
from discord.ext import commands, tasks
import time
from cogs.db import get_db_connection  
from datetime import datetime
import pytz

jakarta_tz = pytz.timezone('Asia/Jakarta')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Voicecount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_start_times = {}  # Menyimpan waktu masuk voice
        self.update_points.start()
        self.track_voice_time.start()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        logging.info(f"Chat dari {message.author.name} : {message.content}")

        try:
            conn, cursor = get_db_connection()
            if conn is None or cursor is None:
                logging.error("Database connection failed.")
                return

            cursor.execute("SELECT message_count FROM voisa.leveling WHERE member_id = %s", (message.author.id,))
            result = cursor.fetchone()

            if result is None:
                logging.info(f"User baru ditambahkan: {message.author.name}")
                cursor.execute(
                    "INSERT INTO voisa.leveling (member_id, username, message_count, voice_time, poin) VALUES (%s, %s, %s, %s, %s)",
                    (message.author.id, message.author.name, 1, 0, 0)
                )
            else:
                new_message_count = result[0] + 1
                logging.info(f"Tambah total pesan {message.author.name} menjadi {new_message_count}")
                cursor.execute(
                    "UPDATE voisa.leveling SET message_count = %s, username = %s WHERE member_id = %s",
                    (new_message_count, message.author.name, message.author.id)
                )

            conn.commit()
        except Exception as e:
            logging.error(f"Error in on_message: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        current_time = time.time()

        # User Join Voice
        if before.channel is None and after.channel is not None:
            self.voice_start_times[member.id] = current_time

        # User Leave Voice
        elif before.channel is not None and after.channel is None:
            if member.id in self.voice_start_times:
                duration = round(current_time - self.voice_start_times.pop(member.id))
                self.update_voice_time_in_db(member.id, duration)
                self.update_daily_stats(member.id, member.name, duration)

        # User Switch Channel
        elif before.channel is not None and after.channel is not None:
            if member.id in self.voice_start_times:
                duration = round(current_time - self.voice_start_times.pop(member.id))
                self.update_voice_time_in_db(member.id, duration)
                self.update_daily_stats(member.id, member.name, duration)

            self.voice_start_times[member.id] = current_time  # Reset time for new channel

    def update_voice_time_in_db(self, member_id, duration):
        try:
            conn, cursor = get_db_connection()
            cursor.execute(
                "UPDATE voisa.leveling SET voice_time = voice_time + %s WHERE member_id = %s",
                (duration, member_id)
            )
            conn.commit()
        except Exception as e:
            logging.error(f"Error updating voice time in leveling table for {member_id}: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def update_daily_stats(self, member_id, username, voice_duration):
        """Update the daily stats table for voice time"""
        try:
            conn, cursor = get_db_connection()
            today = datetime.now(jakarta_tz).date()

            # Insert or update daily stats for the member
            cursor.execute(
                """
                INSERT INTO voisa.daily_stats (member_id, date, voice_time, username)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (member_id, date)
                DO UPDATE SET voice_time = voisa.daily_stats.voice_time + %s
                """,
                (member_id, today, voice_duration, username, voice_duration)
            )

            conn.commit()
        except Exception as e:
            logging.error(f"Error updating daily stats for member {member_id}: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @tasks.loop(seconds=30)  # Update every 30 seconds
    async def track_voice_time(self):
        """Track time every 30 seconds and buffer the data"""
        current_time = time.time()
        for member_id, start_time in list(self.voice_start_times.items()):
            voice_duration = round(current_time - start_time)  # Calculate time spent so far
            logging.info(f"({self.bot.get_user(member_id).name}) + {voice_duration} detik.")

            try:
                conn, cursor = get_db_connection()
                cursor.execute(
                    "UPDATE voisa.leveling SET voice_time = voice_time + %s WHERE member_id = %s",
                    (voice_duration, member_id)
                )
                conn.commit()

                # Insert or update daily stats for the member
                self.update_daily_stats(member_id, self.bot.get_user(member_id).name, voice_duration)

                # Reset the start time to the current time
                self.voice_start_times[member_id] = current_time

            except Exception as e:
                logging.error(f"Error updating voice time for member {member_id}: {e}")
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

    @tasks.loop(minutes=2)
    async def update_points(self):
        try:
            conn, cursor = get_db_connection()
            if conn is None or cursor is None:
                logging.error("Database connection failed in update_points.")
                return

            cursor.execute("SELECT member_id, message_count, voice_time, poin FROM voisa.leveling")
            results = cursor.fetchall()

            for member_id, message_count, voice_time, current_poin in results:
                new_poin = message_count + (voice_time // 10)

                if new_poin != current_poin:
                    local_time = datetime.now(jakarta_tz)
                    cursor.execute(
                        """
                        UPDATE voisa.leveling
                        SET poin = %s, last_activity = %s
                        WHERE member_id = %s
                        """,
                        (new_poin, local_time, member_id)
                    )

            conn.commit()
        except Exception as e:
            logging.error(f"Error in update_points: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @update_points.before_loop
    async def before_update_points(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Voicecount(bot))
    logging.info("Cog Voicecount telah di-load ke bot.")
