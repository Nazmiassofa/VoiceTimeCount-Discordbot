import discord
from discord.ext import commands
import config 
from utils.logger import setup_logging  
import logging
import asyncio
import os
import sys 
import importlib 

setup_logging()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=config.PREFIX, intents=intents, help_command=None)

@bot.event
async def on_ready():
    logging.info(f'Bot {bot.user} is online!')

@bot.event
async def on_command_error(ctx, error):
    logging.error(f"Error with command: {error}")
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"{ctx.author.mention} Command not found")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Need more argument {ctx.author.mention}")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You have no permission.")
    else:
        await ctx.send(f"check your typing command. {ctx.author.mention}")

async def load_cogs():
    for filename in os.listdir('./voicecounter'):
        if filename.endswith('.py') and filename not in ['__init__.py', 'db.py']:
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                logging.info(f"Cog {filename[:-3]} berhasil dimuat.")
            except Exception as e:
                logging.error(f"Failed to load cog {filename[:-3]}: {e}")

if __name__ == "__main__":
    async def main():
        try:
            await load_cogs()
            await bot.start(config.TOKEN)
        except Exception as e:
            logging.error(f"Error saat menjalankan bot: {e}")

    asyncio.run(main())

