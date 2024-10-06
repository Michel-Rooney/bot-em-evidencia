import io
import sqlite3
from datetime import datetime, timedelta
from typing import Optional

import discord
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from decouple import config
from discord import VoiceState, app_commands
from discord.ext import commands
from discord.ext.commands import Bot

from app.utils import msg_time

DB = config('DB', '')
ALLOWED_CHANNELS = list(
    map(lambda x: int(x), config('ALLOWED_CHANNELS').split(', '))
)
GUILD_ID = int(config('GUILD_ID', 0))
TIME_XP = int(config('TIME_XP', 60))

LIMIT = int(config('LIMIT', 10))


class Xp(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        Faz os primeiros ajustes
        """

        self.migrations()
        print(f'Cog - {__name__} is online')

    @app_commands.command(description='ping')
    @app_commands.describe(member="Membro")
    async def ping(
        self,
        interact: discord.Interaction,
        member: Optional[discord.Member] = None,
    ) -> None:
        """
        Retorna pong para testar a conectividade do bot
        """

        if member is None:
            member = interact.user

        await interact.response.send_message(
            f'Pong {member.mention}', ephemeral=True
        )

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: VoiceState,
        after: VoiceState
    ) -> None:
        """
        Monitora as ações dos usuários nas calls
        """

        if member.bot:
            print(
                f'{msg_time()} XP: Bot',
                f'{member.name} ignorado no move_users.'
            )
            return

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        if before.channel is None and after.channel is not None:
            if after.channel.id not in ALLOWED_CHANNELS:
                return

            user = self.get_user(member)

            c.execute('''
                INSERT INTO study (
                    user,
                    start_time,
                    channel_id
                ) VALUES (?, ?, ?)
            ''', (user[0], self.time_now(), after.channel.id))
            conn.commit()

        elif before.channel is not None and after.channel is None:
            if before.channel.id not in ALLOWED_CHANNELS:
                return

            user = self.get_user(member)
            study = self.get_study_by_user(user[0])

            start_time = self.convert_time(study[2])
            end_time = self.time_now()
            end_time_converted = self.convert_time(self.time_now())
            total_time = end_time_converted - start_time
            xp = self.calc_xp(member, total_time)

            if total_time.total_seconds() > 57600:
                print(
                    f'{msg_time()} XP: {member.name} ',
                    'mais de 16h em call, não contou XP.'
                )
                c.execute('''
                DELETE FROM study WHERE id = ?
                ''', (study[0]))
            conn.commit()
            return

            c.execute('''
                UPDATE study
                SET end_time = ?,
                    total_time = ?,
                    xp = ?
                WHERE id = ?
            ''', (end_time, int(total_time.total_seconds()), xp, study[0]))

            c.execute('''
                UPDATE user
                SET xp = ?
                WHERE id = ?
            ''', (user[3] + xp, user[0]))

            conn.commit()

        if before.channel is not None and after.channel is not None:
            before_id = before.channel.id
            after_id = after.channel.id

            if before_id not in ALLOWED_CHANNELS:
                if after_id in ALLOWED_CHANNELS:
                    user = self.get_user(member)

                    c.execute('''
                        INSERT INTO study (
                            user,
                            start_time,
                            channel_id
                        ) VALUES (?, ?, ?)
                    ''', (user[0], self.time_now(), after.channel.id))
                    conn.commit()

            if before_id in ALLOWED_CHANNELS:
                try:
                    user = self.get_user(member)
                    study = self.get_study_by_user(user[0])

                    start_time = self.convert_time(study[2])
                    end_time = self.time_now()
                    end_time_converted = self.convert_time(self.time_now())
                    total_time = end_time_converted - start_time
                    xp = self.calc_xp(member, total_time)

                    if total_time.total_seconds() > 57600:
                        print(
                            f'{msg_time()} XP: {member.name} ',
                            'mais de 16h em call, não contou XP.'
                        )
                        c.execute('''
                        DELETE FROM study WHERE id = ?
                        ''', (study[0]))
                    conn.commit()
                    return

                    c.execute('''
                        UPDATE study
                        SET end_time = ?,
                            total_time = ?,
                            xp = ?
                        WHERE id = ?
                    ''', (end_time, int(total_time.total_seconds()), xp, study[0]))

                    c.execute('''
                        UPDATE user
                        SET xp = ?
                        WHERE id = ?
                    ''', (user[3] + xp, user[0]))

                    conn.commit()
                except Exception as err:
                    print(f'{msg_time()} UPDATE BEFORE IN ALLOWED_CHANNELS - {err}')

                if after_id in ALLOWED_CHANNELS:
                    user = self.get_user(member)

                    c.execute('''
                        INSERT INTO study (
                            user,
                            start_time,
                            channel_id
                        ) VALUES (?, ?, ?)
                    ''', (user[0], self.time_now(), after.channel.id))
                    conn.commit()

        conn.close()

    @app_commands.command(description='Mostra as estatísticas de xp do user.')
    @app_commands.describe(
        offset="O período de tempo para o gráfico.",
        target_member="Usuário que deseja visualizar as estatísticas."
    )
    @app_commands.choices(offset=[
        app_commands.Choice(name='Dia', value='day'),
        app_commands.Choice(name='Semana', value='week'),
        app_commands.Choice(name='Mês', value='month'),
        app_commands.Choice(name='Ano', value='year'),
    ])
    async def xp(
            self,
            interact: discord.Interaction,
            offset: Optional[app_commands.Choice[str]] = None,
            target_member: Optional[discord.Member] = None
    ) -> None:
        """
        Retorna as informações referente ao XP
        """

        if offset is None:
            offset = app_commands.Choice(name='Semana', value='week')

        if target_member is None:
            target_member = interact.user

        member: discord.Member = interact.user

        user = self.get_user(target_member)

        if not user:
            message = (
                f'{target_member.mention} Ainda não foi cadastrado na nossa '
                'base de dados. Por favor entre na call WEBCAM ON ou '
                'Participe de algum grupo.'
            )
            await interact.response.send_message(message, ephemeral=True)
            return

        buffer = self.criar_grafico(member, user, offset.value)
        embed, file = self.criar_embed(
            member, target_member, buffer, user, offset.value)

        await interact.response.send_message(
            member.mention, embed=embed, file=file
        )

    @app_commands.command(description='Mostra o rank de xp.')
    @app_commands.describe(
        member="Mostra a posição do usuário no rank.",
        mensal="Mostra o rank do mês",
    )
    @app_commands.choices(mensal=[
        app_commands.Choice(name='Sim', value='1'),
        app_commands.Choice(name='Não', value='0'),
    ])
    async def rank(
        self,
        interact: discord.Interaction,
        member: Optional[discord.Member] = None,
        mensal: Optional[app_commands.Choice[str]] = None,
    ):
        mensal_msg = ''

        if member is None:
            member = interact.user

        if mensal is None:
            mensal = app_commands.Choice(name='Não', value='0')

        if mensal.value == '1':
            user_position = self.user_position_rank_month(member)
            users_position = self.users_position_rank_month()
            mensal_msg = '(Mês)'
        else:
            user_position = self.user_position_rank(member)
            users_position = self.users_position_rank()

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        if not user_position:
            message = (
                f'{member.mention} Você ainda não foi cadastrado na nossa '
                'base de dados do mês. Por favor entre na call WEBCAM ON ou '
                'Participe de algum grupo.'
            )
            await interact.response.send_message(message, ephemeral=True)
            return

        rank_users_embed = []
        for user in users_position:
            user_discord = interact.guild.get_member(user[1])
            user_mention = user[1]

            if user_discord is not None:
                user_mention = user_discord.mention

            rank_users_embed.append(
                f'#{user[3]} | {user_mention} - XP: `{int(user[2])}`'
            )

        user_rank_discord = interact.guild.get_member(user_position[1])
        message = (
            f'**#{user_position[3]} | {user_rank_discord.mention} '
            f'- XP: `{int(user_position[2])}`**'
        )
        rank_users_embed.append(message)

        embed = discord.Embed(
            title="📋 Rank do servidor"
        )

        embed.add_field(
            name=f'🎙Top {LIMIT} - Voz {mensal_msg}',
            value='\n'.join(rank_users_embed),
            inline=False,
        )

        c.close()
        await interact.response.send_message(member.mention, embed=embed)

    def migrations(self):
        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id INTEGER,
                guild_id INTEGER,
                xp INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS study (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user INTEGER,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                total_time INTEGER,
                xp INTEGER,
                channel_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user) REFERENCES user (id)
            )
        ''')

        conn.commit()
        conn.close()

    def get_user(self, member):
        conn = sqlite3.connect(DB)
        c = conn.cursor()

        guild = self.bot.get_guild(GUILD_ID)

        user = c.execute('''
            SELECT * FROM user WHERE discord_id = ?
        ''', (member.id,)).fetchone()

        if not user:
            user = c.execute('''
                INSERT INTO user (discord_id, guild_id, xp)
                VALUES (?, ?, ?)
            ''', (member.id, guild.id, 0))

            conn.commit()
            user = self.get_user(member)

        conn.close()
        return user

    def get_study_by_user(self, user_id):
        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute('''
            SELECT * FROM study
            WHERE user = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (user_id,))

        study = c.fetchone()

        conn.close()
        return study

    def create_user(self, member, guild_id):
        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute('''
            INSERT INTO user (id_discord, id_guild, xp)
            VALUES (?, ?, ?)
        ''', (member.id, guild_id, 0))

        conn.commit()
        conn.close()

    def time_now(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def convert_time(self, time):
        return datetime.strptime(time, '%Y-%m-%d %H:%M:%S')

    def calc_xp(self, member, total_time):
        xp_point = int(config('XP_POINT', 1))
        xp_per_min = int(total_time.total_seconds() / TIME_XP)

        # if member.premium_since is not None:
        #     xp_point = xp_point * 1.5

        xp = 0
        if xp_per_min > 0:
            xp = xp_per_min * xp_point

        return xp

    def total_horas_embed(self, user):
        conn = sqlite3.connect(DB)
        c = conn.cursor()

        total_horas_sum = c.execute('''
            SELECT SUM(total_time) FROM study
            WHERE user = ?
        ''', (user[0],)).fetchone()[0]

        horas, minutos = 0, 0

        if total_horas_sum is not None:
            total_horas = total_horas_sum / 3600
            horas = int(total_horas)
            minutos = int((total_horas - horas) * 60)

        conn.close()

        return horas, minutos

    def canal_mais_usa(self, user):
        conn = sqlite3.connect(DB)
        c = conn.cursor()

        canal_db = c.execute('''
            SELECT channel_id, COUNT(channel_id), SUM(total_time) AS occurrences
            FROM study
            WHERE user = ?
            GROUP BY channel_id
            ORDER BY occurrences DESC
            LIMIT 1
        ''', (user[0],)).fetchone()

        guild = self.bot.get_guild(GUILD_ID)

        canal = 'Nenhum canal registrado'
        horas, minutos = 0, 0

        if canal_db is not None:
            if canal[0] is not None:
                canal = guild.get_channel(canal_db[0])

            if canal_db[2] is not None:
                if canal_db[2] > 0:
                    total_horas = canal_db[2] / 3600
                    horas = int(total_horas)
                    minutos = int((total_horas - horas) * 60)

        c.close()
        return canal, horas, minutos

    def users_position_rank(self):
        conn = sqlite3.connect(DB)
        c = conn.cursor()

        users_rank = f'''
            WITH RankedUsers AS (
                SELECT
                    id,
                    discord_id,
                    xp,
                    RANK() OVER (ORDER BY xp DESC) AS position
                FROM user
            )
            SELECT *
            FROM RankedUsers
            LIMIT {LIMIT}
        '''

        users_position = c.execute(users_rank).fetchall()
        c.close()

        return users_position

    def users_position_rank_month(self):
        conn = sqlite3.connect(DB)
        c = conn.cursor()

        users_rank = f'''
            WITH RankedUsers AS (
                SELECT
                    u.id,
                    u.discord_id,
                    SUM(s.xp) AS total_xp,
                    RANK() OVER (ORDER BY SUM(s.xp) DESC) AS position
                FROM
                    user u
                JOIN
                    study s ON u.id = s.user
                WHERE
                    strftime('%Y-%m', s.created_at) = strftime('%Y-%m', 'now')
                GROUP BY
                    u.id, u.discord_id
            )
            SELECT *
            FROM RankedUsers
            LIMIT {LIMIT}
        '''

        users_position = c.execute(users_rank).fetchall()
        c.close()

        return users_position

    def user_position_rank(self, member):
        conn = sqlite3.connect(DB)
        c = conn.cursor()

        user = self.get_user(member)

        if not user:
            return None

        user_rank = '''
            WITH RankedUsers AS (
                SELECT
                    id,
                    discord_id,
                    xp,
                    RANK() OVER (ORDER BY xp DESC) AS position
                FROM user
            )
            SELECT *
            FROM RankedUsers
            WHERE id = ?;
        '''

        user_position = c.execute(user_rank, (user[0],)).fetchone()
        c.close()

        return user_position

    def user_position_rank_month(self, member):
        conn = sqlite3.connect(DB)
        c = conn.cursor()

        user = self.get_user(member)

        if not user:
            return None

        user_rank = '''
            WITH RankedUsers AS (
                SELECT
                    u.id,
                    u.discord_id,
                    SUM(s.xp) AS total_xp,
                    RANK() OVER (ORDER BY SUM(s.xp) DESC) AS position
                FROM
                    user u
                JOIN
                    study s ON u.id = s.user
                WHERE
                    strftime('%Y-%m', s.created_at) = strftime('%Y-%m', 'now')
                GROUP BY
                    u.id, u.discord_id
            )
            SELECT *
            FROM RankedUsers
            WHERE id = ?
        '''

        user_position = c.execute(user_rank, (user[0],)).fetchone()
        c.close()

        if not user_position:
            return (
                user[0], user[1], 0, 'Sem rank'
            )

        return user_position

    def criar_embed(self, member, member_user, buffer, user, offset='week'):
        horas, minutos = self.total_horas_embed(user)
        canal, canal_horas, canal_minutos = self.canal_mais_usa(user)
        canal_tempo = f'**{canal_horas}h {canal_minutos}min**'

        user_position = self.user_position_rank(member)

        match offset:
            case 'day':
                title_day = 'do dia'
            case 'week':
                title_day = 'semanal'
            case 'month':
                title_day = 'mensal'
            case 'year':
                title_day = 'anual'

        embed = discord.Embed(
            title=f'Estatísticas {title_day} de {member_user.name}',
        )

        embed.add_field(
            name=f'{member_user.name}, você tem',
            value=f'{int(user[3])} xp 😎',
            inline=True
        )

        embed.add_field(
            name='Tempo total de estudos',
            value=f'{horas}h {minutos}min',
            inline=True
        )

        embed.add_field(
            name='Posição no rank',
            value=f'#{user_position[3]}',
            inline=True
        )

        embed.add_field(
            name='Canal de voz mais conectado 🔊',
            value=f'{canal} - {canal_tempo}',
            inline=False
        )

        embed.set_footer(
            text=f'{datetime.now().strftime("%d %b %Y %H:%M:%S")}')

        buffer.seek(0)
        file = discord.File(fp=buffer, filename='grafico.png')
        embed.set_image(url='attachment://grafico.png')

        return embed, file

    def dados_grafico(self, user, days=6):
        conn = sqlite3.connect(DB)
        c = conn.cursor()

        today = datetime.now()
        categorias = []
        valores = []

        for i in range(days, -1, -1):
            dia = today - timedelta(days=i)
            data_formatada = dia.strftime('%Y-%m-%d')
            categorias.append(dia.strftime('%d/%m'))

            total_time_sum = c.execute('''
                SELECT SUM(total_time) FROM study
                WHERE user = ? AND DATE(created_at) = ?
            ''', (user[0], data_formatada)).fetchone()[0]

            if total_time_sum is None:
                valores.append(0)
                continue

            valor = round(total_time_sum / 3600, 2)
            valores.append(valor)

        conn.close()
        return categorias, valores

    def dados_grafico_year(self, user, months=11):
        conn = sqlite3.connect(DB)
        c = conn.cursor()

        today = datetime.now()
        categorias = []
        valores = []

        for i in range(months, -1, -1):
            dia = today - relativedelta(months=i)
            data_formatada = dia.strftime('%Y-%m')
            categorias.append(dia.strftime('%m/%Y'))

            total_time_sum = c.execute('''
                SELECT SUM(total_time) FROM study
                WHERE user = ? AND strftime('%Y-%m', created_at) = ?
            ''', (user[0], data_formatada)).fetchone()[0]

            if total_time_sum is None:
                valores.append(0)
                continue

            valor = round(total_time_sum / 3600, 2)
            valores.append(valor)

        conn.close()
        return categorias, valores

    def criar_grafico(self, member, user, offset='week'):
        today = datetime.now()

        match offset:
            case 'day':
                categorias, valores = self.dados_grafico(user, days=1)
            case 'week':
                categorias, valores = self.dados_grafico(user, days=6)
            case 'month':
                categorias, valores = self.dados_grafico(user, days=29)
            case 'year':
                categorias, valores = self.dados_grafico_year(user, months=11)

        bar = plt.bar(categorias, valores)
        plt.xlabel('Dia')
        plt.ylabel('Horas')
        plt.title(f'Gráfico de Horas Estudadas {today.year} - {member.name}')

        plt.xticks(rotation=45, fontsize=6)
        plt.bar_label(bar)

        ax = plt.gca()
        ax.set_ylim(0)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(1)

        plt.clf()
        return buffer


async def setup(bot):
    await bot.add_cog(Xp(bot))
