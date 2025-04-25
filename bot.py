import discord
from discord.ext import commands
import config 
from logger import setup_logging  
import logging
import asyncio
import os
import sys 
import importlib 

# Setup logging
setup_logging()

# Inisialisasi bot dengan intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=config.PREFIX, intents=intents)

@bot.event
async def on_ready():
    """Event yang dijalankan saat bot berhasil online."""
    logging.info(f'Bot {bot.user} telah online!')
    logging.info(f'Prefix perintah: {config.PREFIX}')
    
    # Menampilkan aktivitas bot sebagai "Watching"
    activity = discord.Game(name="Voisa Apps!")
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.event
async def on_command_error(ctx, error):
    """Event untuk menangani kesalahan perintah."""
    logging.error(f"Kesalahan pada perintah: {error}")
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"{ctx.author.mention} Jangan ngaco-ngaco dah.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Kayaknya ada yang kurang deh. {ctx.author.mention}")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("U siapa anjg.")
    else:
        await ctx.send(f"Ah yang bener dong ngetiknya. {ctx.author.mention}")

async def load_cogs():
    """Memuat semua cog yang ada di folder 'cogs', kecuali file tertentu."""
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename not in ['__init__.py', 'db.py']:
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                logging.info(f"Cog {filename[:-3]} berhasil dimuat.")
            except Exception as e:
                logging.error(f"Gagal memuat cog {filename[:-3]}: {e}")

if __name__ == "__main__":
    async def main():
        """Fungsi utama untuk menjalankan bot."""
        try:
            # Muat semua cog
            await load_cogs()
            # Mulai bot
            await bot.start(config.TOKEN)
        except Exception as e:
            logging.error(f"Error saat menjalankan bot: {e}")

    asyncio.run(main())

