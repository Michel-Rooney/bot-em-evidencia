# import locale
from datetime import datetime, timedelta, timezone

import discord
import requests
from bs4 import BeautifulSoup
from decouple import config
from discord.ext import commands, tasks
from discord.ext.commands import Bot

from app.utils import msg_log

GUILD_ID = int(config('GUILD_ID', 0))

ESTRATEGIA_URL = config('ESTRATEGIA_URL')
ESTRATEGIA_CHANNEL_ID = int(config('ESTRATEGIA_CHANNEL_ID'))
ESTRATEGIA_LOOP_INTERVAL_MIN = int(config('ESTRATEGIA_LOOP_INTERVAL_MIN'))

UTC = int(config('UTC', -3))
OFFSET = timedelta(hours=UTC)
TZ = timezone(OFFSET)

last_news_time = ''

MONTHS_PT_TO_EN = {
    "janeiro": "January", "fevereiro": "February",
    "março": "March", "abril": "April",
    "maio": "May", "junho": "June",
    "julho": "July", "agosto": "August",
    "setembro": "September", "outubro": "October",
    "novembro": "November", "dezembro": "December"
}


class EstrategiaNoticias(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        Faz os primeiros ajustes
        """
        self.news.start()
        msg_log(f'Cog - {__name__} is online!')

    @tasks.loop(minutes=ESTRATEGIA_LOOP_INTERVAL_MIN)
    async def news(self) -> None:
        global last_news_time

        guild = self.bot.get_guild(GUILD_ID)
        channel = guild.get_channel(ESTRATEGIA_CHANNEL_ID)
        response = requests.get(ESTRATEGIA_URL)
        soup = BeautifulSoup(response.text, 'html.parser')

        recent_news = soup.select_one('.archive-main')
        articles = reversed(list(recent_news.children)[:6])

        if not last_news_time:
            last_news_time = datetime.now(TZ)

        for article in articles:
            thumb: str = article.select_one('img')['src']
            title_root = article.select_one('.entry-title a')
            title: str = title_root.text.strip()
            link: str = title_root['href']
            author: str = article.select_one('.author a').text.strip()
            time: str = article.select_one('.meta-date').text.strip()

            time = time\
                .replace('Publicado', '')\
                .replace('Atualizado', '')\
                .replace('em', '')\
                .replace('de ', '')\
                .strip()

            for pt, en in MONTHS_PT_TO_EN.items():
                time = time.replace(pt, en)

            article_time = datetime.strptime(
                time, '%d %B %Y'
            ).replace(tzinfo=TZ)

            if article_time < last_news_time:
                continue

            time = datetime.now(TZ).strftime('%Y-%m-%d %H:%M')

            embed = discord.Embed(
                title=f'📢 {title} - {time}',
                url=link,
                color=discord.Color.teal(),
                description=f"Por **{author}**"
            )

            embed.set_footer(
                text="[MENSAGEM AUTOMÁTICA] pelo @Bot em Evidência#3468")
            embed.set_image(url=thumb)

            await channel.send(embed=embed)

        last_news_time = article_time + timedelta(minutes=1)
        return


async def setup(bot):
    await bot.add_cog(EstrategiaNoticias(bot))
