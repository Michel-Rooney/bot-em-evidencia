from datetime import datetime

import discord
import requests
from bs4 import BeautifulSoup
from decouple import config
from discord.ext import commands, tasks
from discord.ext.commands import Bot

from app.utils import msg_log

DEVOCIONAL_URL = config('DEVOCIONAL_URL', '')
DEVOCIONAL_CHANNEL_ID = int(config('DEVOCIONAL_CHANNEL_ID', 0))
GUILD_ID = int(config('GUILD_ID', 0))


class Devocional(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        Faz os primeios ajustes
        """

        self.devocional.start()
        msg_log(f'Cog - {__name__} is online!')

    @tasks.loop(seconds=10)
    async def devocional(self) -> None:
        guild = self.bot.get_guild(GUILD_ID)
        channel = guild.get_channel(DEVOCIONAL_CHANNEL_ID)
        scraped = self.web_scraping()

        if not scraped:
            await channel.send('Nenhum devocional capturado!')
            return

        embed = self.embed(scraped)
        await channel.send(embed=embed)

    def web_scraping(self) -> dict:
        response = requests.get(DEVOCIONAL_URL)
        soup = BeautifulSoup(response.text, 'html.parser')

        titulo_diario = soup.select_one(
            'div.page_hero__zOHEm:nth-child(1) > div:nth-child(2) > h2:nth-child(2)'
        )
        mensagem_diaria = soup.select_one('.FragmentView_text__g6Uq2').children
        link_diario = soup.select_one('.FragmentView_refLink__mssLX')

        scraped = {
            'titulo': titulo_diario,
            'mensagem': mensagem_diaria,
            'link': link_diario
        }

        return scraped

    def embed(self, scraped: dict) -> discord.Embed:
        link = scraped['link']
        link_texto = link.text.strip()
        link_url = link['href']
        mensagem = []
        data_atual = datetime.now().strftime('%d/%m/%Y')

        for msg in scraped['mensagem']:
            mensagem.append(f'{msg.text.strip()}')
        mensagem.append(f'\n [{link_texto}]({link_url})')

        embed = discord.Embed(
            title=f'📖 Devocional Diário - {data_atual}',
            url=DEVOCIONAL_URL,
            color=discord.Color.dark_orange(),
        )

        embed.add_field(
            name=f"{scraped['titulo'].text.strip()}\n",
            value='\n'.join(mensagem)
        )

        embed.set_footer(
            text="Devocional coletado no site bibliaonline.com.br"
        )
        embed.set_thumbnail(
            url='https://images.unsplash.com/photo-1509021436665-8f07dbf5bf1d?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3'
        )

        return embed


async def setup(bot):
    await bot.add_cog(Devocional(bot))
