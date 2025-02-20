import discord
from discord.ext import commands
import psutil
import os
import time
from datetime import datetime, timedelta  # Perbaikan di sini: import timedelta
import logging

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()  # Waktu mulai bot aktif
        logging.info("Stats Cog telah diinisialisasi.")

    @commands.command()
    async def stats(self, ctx):
        """Menampilkan statistik beban kerja bot"""

        # Waktu sejak bot aktif
        uptime_seconds = time.time() - self.start_time
        uptime = str(timedelta(seconds=uptime_seconds))  # Gunakan timedelta yang sudah diimport

        # CPU Usage
        cpu_usage = psutil.cpu_percent(interval=1)

        # Memory Usage
        memory_info = psutil.virtual_memory()
        memory_usage = memory_info.percent

        # Latency
        latency = round(self.bot.latency * 1000, 2)  # dalam milidetik

        # Jumlah guild dan pengguna
        guild_count = len(self.bot.guilds)
        member_count = sum([guild.member_count for guild in self.bot.guilds])

        # Menghasilkan hasil
        embed = discord.Embed(title="Bot Resources usage", color=discord.Color.green())
        embed.add_field(name="Uptime", value=uptime, inline=False)
        embed.add_field(name="CPU (%)", value=f"{cpu_usage}%", inline=True)
        embed.add_field(name="Memori (%)", value=f"{memory_usage}%", inline=True)
        embed.add_field(name="Latency (ms)", value=f"{latency} ms", inline=True)
        embed.add_field(name="Server (Guilds)", value=str(guild_count), inline=True)
        embed.add_field(name="Pengguna (Members)", value=str(member_count), inline=True)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Stats(bot))
    logging.info("Cog Stats telah di-load ke bot.")
