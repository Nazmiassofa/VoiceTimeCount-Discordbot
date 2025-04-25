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

@bot.command(name='list_tasks')
@commands.is_owner()  # Hanya pemilik bot yang dapat menggunakan perintah ini
async def list_tasks(ctx):
    """Menampilkan daftar task yang sedang berjalan."""
    tasks = asyncio.all_tasks()
    embed = discord.Embed(
        title="Daftar Tasks yang Sedang Berjalan",
        color=discord.Color.green()
    )
    if not tasks:
        embed.description = "Tidak ada task yang sedang berjalan."
    else:
        for idx, task in enumerate(tasks, start=1):
            embed.add_field(name=f"Task #{idx}", value=f"{task.get_name()}", inline=False)

    await ctx.send(embed=embed)

@bot.command(name='reset_tasks')
@commands.is_owner()  # Hanya pemilik bot yang dapat menggunakan perintah ini
async def reset_tasks(ctx):
    """Menghentikan semua tasks yang sedang berjalan."""
    tasks = asyncio.all_tasks()
    stopped_count = 0
    for task in tasks:
        if task is not asyncio.current_task():  # Jangan hentikan task perintah ini
            task.cancel()  # Membatalkan task
            stopped_count += 1
    await ctx.send(f"✅ {stopped_count} task berhasil dihentikan.")
    logging.info(f"{stopped_count} task berhasil dihentikan.")

@bot.command(name='reboot', aliases=['restart'])
@commands.is_owner()  # Hanya pemilik bot yang bisa menjalankan perintah ini
async def reboot(ctx):
    """Perintah untuk me-reboot bot dan memuat ulang semua konfigurasi."""
    try:
        await ctx.send("🔄 Sedang melakukan reboot...")

        # Memuat ulang semua cog
        for extension in list(bot.extensions):
            await bot.unload_extension(extension)  # Unload cog
            logging.info(f"Cog {extension} berhasil di-unload.")

        await load_cogs()  # Reload cog
        logging.info("Semua cog berhasil dimuat ulang.")

        # Mengirim notifikasi selesai reboot
        await ctx.send("✅ Reboot selesai! Semua konfigurasi berhasil dimuat ulang.")
        logging.info("Bot berhasil direboot.")

    except Exception as e:
        await ctx.send(f"❌ Terjadi kesalahan saat reboot: {e}")
        logging.error(f"Kesalahan saat reboot: {e}")
        
@bot.command(name='reload', aliases=['rl'])
@commands.is_owner()  # Hanya pemilik bot yang dapat menggunakan perintah ini
async def reload_cog(ctx, cog_name: str):
    """Reload cog tertentu berdasarkan nama file."""
    try:
        # Format nama file menjadi modul cog
        extension = f"cogs.{cog_name}"
        if extension in bot.extensions:
            await bot.unload_extension(extension)
            logging.info(f"Cog {cog_name} berhasil di-unload.")
        
        await bot.load_extension(extension)
        logging.info(f"Cog {cog_name} berhasil di-reload.")
        await ctx.send(f"✅ Cog **{cog_name}** berhasil di-reload.")
    except Exception as e:
        logging.error(f"Gagal mereload cog {cog_name}: {e}")
        await ctx.send(f"❌ Gagal mereload cog **{cog_name}**: {e}")


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

