import asyncio
import os

import discord
from decouple import config
from discord.ext import commands

from concursos_brasil import concursos_brasil
from lock_unlock_chat import lock_unlock_vip
from move_user import move_users

TOKEN = config('TOKEN', '')
GUILD_ID = int(config('GUILD_ID', 0))

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
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')


async def main():
    async with bot:
        await load()
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
