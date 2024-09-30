import sqlite3

import streamlit as st
from decouple import config
from discord import Member
from discord.ext import commands
from discord.ext.commands import Bot, Cog

DB = config('DB', '')
GUILD_ID = int(config('GUILD_ID', 0))


class Home(Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        Faz os primeiros ajustes
        """
        print(f'Cog - {__name__} is online')

    def start(self) -> None:
        st.title('Bot em Evidência!')
        st.divider()
        self.search()

    def search(self):
        users = self.get_users_return_name()
        title = st.selectbox('Selecione o usuário:', users)
        st.write('Dica: Você pode escrever o nome de usuário.', title)

    def get_users_return_name(self) -> list[str]:
        conn = sqlite3.connect(DB)
        c = conn.cursor()

        users = c.execute('''
            SELECT * FROM user
        ''').fetchall()

        users_name = []
        print(users[:10])

        # for user in users:
        #     print(self.bot.get_user(int(user[1])))
        #     guild = self.bot.get_guild(GUILD_ID)
        #     print(guild)
        #     user_discord: Member = guild.get_member(user[1])
        #
        #     if user_discord:
        #         users_name.append(user_discord.nick)

        conn.close()
        return users_name


async def setup(bot):
    await bot.add_cog(Home(bot))
