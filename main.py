import discord
from decouple import config
from discord.ext import commands

from concursos_brasil import concursos_brasil
from lock_unlock_chat import lock_unlock_vip
from move_user import move_users

TOKEN = config('TOKEN', '')
GUILD_ID = int(config('GUILD_ID', 0))


INTENTS = discord.Intents.default()
BOT = commands.Bot(command_prefix='!evidencia', intents=INTENTS)


@BOT.event
async def on_ready():
    print(f'Logged in as {BOT.user}')
    concursos_brasil.start(BOT, GUILD_ID)
    move_users.start(BOT, GUILD_ID)
    lock_unlock_vip.start(BOT, GUILD_ID)


if __name__ == '__main__':
    BOT.run(TOKEN)
