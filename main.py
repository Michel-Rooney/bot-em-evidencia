import asyncio
import os

import discord
from decouple import config
from discord.ext import commands

from app import concursos_brasil, lock_unlock_vip, move_users

TOKEN = config('TOKEN', '')
GUILD_ID = int(config('GUILD_ID', 0))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!b3e ', intents=intents)


@bot.event
async def on_ready():
    concursos_brasil.start(bot, GUILD_ID)
    move_users.start(bot, GUILD_ID)
    lock_unlock_vip.start(bot, GUILD_ID)
    print(f'Logged in as {bot.user}')


@bot.command()
async def sync(ctx: commands.Context):
    sincs = await bot.tree.sync()
    await ctx.reply(f"{len(sincs)} comandos sicronizados")


async def load():
    path = os.path.join(BASE_DIR, 'app/cogs')

    for filename in os.listdir(path):
        if filename.endswith('.py') and not ('__init__' in filename):
            await bot.load_extension(f'app.cogs.{filename[:-3]}')


async def main():
    async with bot:
        await load()
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
