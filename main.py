import asyncio
import os
from time import sleep

import discord
from decouple import config
from discord.ext import commands

from app import concursos_brasil, lock_unlock, move_users

TOKEN = config('TOKEN', '')
GUILD_ID = int(config('GUILD_ID', 0))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!b3e ', intents=intents)


@bot.event
async def on_ready():
    concursos_brasil.start(bot, GUILD_ID)
    move_users.start(bot, GUILD_ID)
    # lock_unlock.start(bot, GUILD_ID)
    print(f'Logged in as {bot.user}')


@bot.command()
async def sync(ctx: commands.Context):
    sincs = await bot.tree.sync()
    await ctx.reply(f"{len(sincs)} comandos sicronizados", ephemeral=True)


"""
    MOVE USERS
"""


@bot.command()
async def movestart(ctx: commands.Context):
    move_users.start(bot, GUILD_ID)
    await ctx.reply("Funcionalidade Move Users startou", ephemeral=True)


@bot.command()
async def moverestart(ctx: commands.Context):
    move_users.stop()
    sleep(3)
    move_users.start(bot, GUILD_ID)
    await ctx.reply("Funcionalidade Move Users restartada", ephemeral=True)


@bot.command()
async def movestop(ctx: commands.Context):
    move_users.stop()
    await ctx.reply("Funcionalidade Move Users stopou", ephemeral=True)


"""
    LOCK CHAT
"""


@bot.command()
async def lockstart(ctx: commands.Context):
    lock_unlock.start(bot, GUILD_ID)
    await ctx.reply("Funcionalidade Lock Chat startou", ephemeral=True)


@bot.command()
async def lockrestart(ctx: commands.Context):
    lock_unlock.stop()
    sleep(3)
    lock_unlock.start(bot, GUILD_ID)
    await ctx.reply("Funcionalidade Lock Chat restartada", ephemeral=True)


@bot.command()
async def lockstop(ctx: commands.Context):
    lock_unlock.stop()
    await ctx.reply("Funcionalidade Lock Chat stopou", ephemeral=True)


"""
    CONCURSOS BRASIL
"""


@bot.command()
async def concursosstart(ctx: commands.Context):
    concursos_brasil.start(bot, GUILD_ID)
    await ctx.reply("Funcionalidade Concursos Brasil startada", ephemeral=True)


@bot.command()
async def concursosrestart(ctx: commands.Context):
    concursos_brasil.stop()
    sleep(3)
    concursos_brasil.start(bot, GUILD_ID)
    await ctx.reply("Funcionalidade Concursos Brasil restartada", ephemeral=True)


@bot.command()
async def concursosstop(ctx: commands.Context):
    concursos_brasil.stop()
    await ctx.reply("Funcionalidade Concursos Brasil stopada", ephemeral=True)


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
