from datetime import datetime

import discord
import requests
from bs4 import BeautifulSoup
from decouple import config
from discord.ext import tasks
from discord.ext.commands import Bot

from app.utils import msg_time

CON_BR_CHANNEL_ID = int(config('CON_BR_CHANNEL_ID', 0))
CON_BR_ROLE_NOTICIA_ID = int(config('CON_BR_ROLE_NOTICIA_ID', 0))
CON_BR_URL = config('CON_BR_URL', '')
CON_BR_LOOP_INTERVAL_MIN = int(config('CON_BR_LOOP_INTERVAL_MIN', 10))

tempo_ultima_noticia = ''


@tasks.loop(minutes=CON_BR_LOOP_INTERVAL_MIN)
async def concursos_brasil(bot: Bot, GUILD_ID: int) -> int:
    """
    Envia as notícias do site Concursos Brasil
    """

    global tempo_ultima_noticia

    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(CON_BR_CHANNEL_ID)
    response = requests.get(CON_BR_URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    concursos_recentes = soup.select_one('.recentes-container')
    description = []

    if not tempo_ultima_noticia:
        tempo_ultima_noticia = datetime.now()

    for article in concursos_recentes.children:
        link = article.select_one('a')['href']
        localidade = article.select_one('.sigla').text.strip()
        titulo = article.select_one('.post-title').text.strip()
        tempo = article.select_one('time').text.strip()
        author = article.select_one('span > span').text.strip()

        tempo_article = datetime.strptime(
            tempo, "%d/%m/%Y às %Hh%M"
        )

        if tempo_article < tempo_ultima_noticia:
            continue

        description.append(
            f"## [{localidade} - {titulo}]({link})\n{tempo} por {author}"
        )

    tempo_ultima_noticia = datetime.now()

    time = datetime.now().strftime('%Y-%m-%d %H:%M')

    if len(description) <= 0:
        print(f'{msg_time()} Sem notícias recentes.')
        return

    embed = discord.Embed(
        title=f'📢 Concursos Brasil - Notícias Recentes" [{time}]',  # noqa: E501
        url=CON_BR_URL,
        color=discord.Color.green(),
        description="\n".join(description)
    )

    embed.set_footer(text="[MENSAGEM AUTOMÁTICA] pelo @Bot em Evidência#3468")
    embed.set_thumbnail(
        url='https://i.ibb.co/KyTkq14/concursos-brasil.jpg'  # noqa: E501
    )

    role_noticias = guild.get_role(CON_BR_ROLE_NOTICIA_ID)

    await channel.send(role_noticias.mention, embed=embed)
