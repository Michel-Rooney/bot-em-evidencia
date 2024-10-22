import io
from datetime import datetime, timedelta
from typing import Optional

import discord
import matplotlib.pyplot as plt
from decouple import config
from discord import Member, VoiceState, app_commands
from discord.ext import commands
from discord.ext.commands import Bot
from peewee import fn

from app.db.models import Study, User, db
from app.utils import msg_log

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
        self.sync_db()
        msg_log(f'Cog - {__name__} is online')

    def sync_db(self):
        db.connect()
        db.create_tables([User, Study], safe=True)

    @app_commands.command(description='xp ping')
    @app_commands.describe(member="Membro")
    async def xp_ping(
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
            f'XP Pong {member.mention}', ephemeral=True
        )

    @app_commands.command(description='Mostra as estatísticas de xp do user.')
    @app_commands.describe(
        offset="O período de tempo para o gráfico.",
        target_member="Usuário que deseja visualizar as estatísticas."
    )
    @app_commands.choices(offset=[
        app_commands.Choice(name='Dia', value='day'),
        app_commands.Choice(name='Semana', value='week'),
        app_commands.Choice(name='Quinzenal', value='fortnightly'),
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

        buffer = self.create_graphic(member, user, target_member, offset.value)
        embed, file = self.create_embed(
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

        rank_users_embed = []
        for user in users_position:
            user_discord = interact.guild.get_member(user['discord'])
            user_mention = user['discord']

            if user_discord is not None:
                user_mention = user_discord.mention

            rank_users_embed.append(
                f'#{user['position']} | {user_mention} - XP: `{user['xp']}`'
            )

        user_rank_discord = interact.guild.get_member(user_position['discord'])
        message = (
            f'**#{user_position['position']} | {user_rank_discord.mention} '
            f'- XP: `{user_position['xp']}`**'
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

        await interact.response.send_message(member.mention, embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: Member,
        before: VoiceState,
        after: VoiceState
    ) -> None:
        """
        Monitora as ações dos usuários nas calls
        """

        if member.bot:
            msg_log(f'XP: Bot {member.name} ignorado no move_users.')
            return

        if before.channel is None and after.channel is not None:
            if after.channel.id not in ALLOWED_CHANNELS:
                return

            user = self.get_user(member)
            Study.create(user=user, channel=after.channel.id)

        elif before.channel is not None and after.channel is None:
            if before.channel.id not in ALLOWED_CHANNELS:
                return

            user = self.get_user(member)
            study = Study.select().where(Study.user == user).order_by(
                Study.created_at.desc()
            ).first()

            self.update_study(member, user, study)

        if before.channel is not None and after.channel is not None:
            before_id = before.channel.id
            after_id = after.channel.id

            if before_id not in ALLOWED_CHANNELS:
                if after_id in ALLOWED_CHANNELS:
                    user = self.get_user(member)
                    Study.create(user=user, channel=after.channel.id)

            if before_id in ALLOWED_CHANNELS:
                try:
                    user = self.get_user(member)
                    study = Study.select().where(Study.user == user).order_by(
                        Study.created_at.desc()
                    ).first()
                    self.update_study(member, user, study)
                except Exception as err:
                    msg_log(f'UPDATE BEFORE IN ALLOWED_CHANNELS - {err}')

                if after_id in ALLOWED_CHANNELS:
                    user = self.get_user(member)
                    Study.create(user=user, channel=after.channel.id)

        db.close()

    def get_user(self, member: Member):
        try:
            user = User.get(User.discord == member.id)
        except User.DoesNotExist:
            guild = self.bot.get_guild(GUILD_ID)
            user = User.create(discord=member.id, guild=guild.id)

        return user

    def calc_xp(self, member, total_time):
        xp_point = int(config('XP_POINT', 1))
        xp_per_min = int(total_time.total_seconds() / TIME_XP)

        xp = 0
        if xp_per_min > 0:
            xp = xp_per_min * xp_point

        return xp

    def update_study(self, member, user, study):
        start_time = study.start_time
        end_time = datetime.now()
        total_time = end_time - start_time
        xp = self.calc_xp(member, total_time)

        study.end_time = end_time
        study.total_time = total_time.total_seconds()
        study.xp = xp
        study.save()

        user.xp = user.xp + xp
        user.save()

    def create_graphic(
        self, member: discord.Member, user,
        target_member: discord.Member, offset='week'
    ):
        today = datetime.now()

        match offset:
            case 'day':
                categories, values = self.graphic_data(user, days=1)
            case 'week':
                categories, values = self.graphic_data(user, days=6)
            case 'fortnightly':
                categories, values = self.graphic_data(user, days=14)

        bar = plt.bar(categories, values)
        plt.xlabel('Dia')
        plt.ylabel('Horas')
        plt.title(
            f'Gráfico de Horas Estudadas {today.year} - {target_member.name}'
        )

        plt.xticks(rotation=45, fontsize=6)
        plt.bar_label(bar)

        ax = plt.gca()
        ax.set_ylim(0)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(1)

        plt.clf()
        return buffer

    def graphic_data(self, user, days=6):
        today = datetime.now()
        categories = []
        values = []

        for i in range(days, -1, -1):
            dia = today - timedelta(days=i)
            formated_date = dia.strftime('%Y-%m-%d')
            categories.append(dia.strftime('%d/%m'))

            total_time_sum = (
                Study.select(
                    fn.SUM(Study.total_time)
                ).where(
                    (Study.user == user) &
                    (fn.DATE(Study.created_at) == formated_date)
                ).scalar()
            )

            if total_time_sum is None:
                values.append(0)
                continue

            valor = round(total_time_sum / 3600, 2)
            values.append(valor)

        return categories, values

    def create_embed(self, member, member_user, buffer, user, offset='week'):
        hours, minutes = self.total_hours_embed(user)
        channel, channel_hours, channel_minutes = self.most_used_channel(user)
        channel_time = f'**{channel_hours}h {channel_minutes}min**'
        user_position = self.user_position_rank(member)

        match offset:
            case 'day':
                title_day = 'do dia'
            case 'week':
                title_day = 'semanal'
            case 'fortnightly':
                title_day = 'quinzenal'

        embed = discord.Embed(
            title=f'Estatísticas {title_day} de {member_user.name}',
        )

        embed.add_field(
            name=f'{member_user.name}, você tem',
            value=f'{user.xp} xp 😎',
            inline=True
        )

        embed.add_field(
            name='Tempo total de estudos',
            value=f'{hours}h {minutes}min',
            inline=True
        )

        embed.add_field(
            name='Posição no rank',
            value=f'#{user_position['position']}',
            inline=True
        )

        embed.add_field(
            name='Canal de voz mais conectado 🔊',
            value=f'{channel} - {channel_time}',
            inline=False
        )

        embed.set_footer(
            text=f'{datetime.now().strftime("%d %b %Y %H:%M:%S")}')

        buffer.seek(0)
        file = discord.File(fp=buffer, filename='grafico.png')
        embed.set_image(url='attachment://grafico.png')

        return embed, file

    def total_hours_embed(self, user):
        total_time_sum = (
            Study.select(
                fn.SUM(Study.total_time)
            ).where(
                (Study.user == user)
            ).scalar()
        )
        hours, minutes = 0, 0

        if total_time_sum is not None:
            total_time = total_time_sum / 3600
            hours = int(total_time)
            minutes = int((total_time - hours) * 60)

        return hours, minutes

    def most_used_channel(self, user):
        channel_db = (
            Study.select(
                Study.channel,
                fn.COUNT(Study.channel).alias('count'),
                fn.SUM(Study.total_time).alias('sum')
            ).where(
                Study.user == user
            ).group_by(
                Study.channel
            ).order_by(
                fn.SUM(Study.total_time).desc()
            ).limit(
                1
            ).dicts(
            ).first()
        )

        guild = self.bot.get_guild(GUILD_ID)
        channel = 'Nenhum canal registrado'
        hours, minutes = 0, 0

        if channel_db is not None:
            if channel_db is not None:
                channel = guild.get_channel(channel_db['channel'])

            if channel_db is not None:
                if channel_db['sum'] > 0:
                    total_time = channel_db['sum'] / 3600
                    hours = int(total_time)
                    minutes = int((total_time - hours) * 60)

        return channel, hours, minutes

    def get_ranked_users(self):
        return (
            User.select(
                User.id,
                User.discord,
                User.xp,
                fn.RANK().over(order_by=[User.xp.desc()]).alias('position')
            )
        )

    def get_ranked_users_month(self):
        ranked_users = (
            User.select(
                User.id.alias('id'),
                User.discord.alias('discord'),
                fn.SUM(Study.xp).alias('xp'),
                fn.RANK().over(
                    order_by=[fn.SUM(Study.xp).desc()]).alias('position')
            ).join(
                Study, on=(User.id == Study.user)
            ).where(
                fn.TO_CHAR(Study.created_at,
                           'YYYY-MM') == fn.TO_CHAR(fn.NOW(), 'YYYY-MM')
            ).group_by(
                User.id, User.discord
            ).alias('ranked_users')
        )

        return ranked_users

    def user_position_rank(self, member):
        user = self.get_user(member)

        if not user:
            return None

        ranked_user = self.get_ranked_users().where(
            User.id == user.id
        ).dicts().first()
        return ranked_user

    def user_position_rank_month(self, member):
        user = self.get_user(member)

        if not user:
            return None

        ranked_users = self.get_ranked_users_month()

        ranked_user = User.select(
            ranked_users.c.id.alias('id'),
            ranked_users.c.discord.alias('discord'),
            ranked_users.c.xp.alias('xp'),
            ranked_users.c.position.alias('position')
        ).from_(
            ranked_users
        ).where(
            ranked_users.c.id == user.id
        ).dicts().first()

        return ranked_user

    def users_position_rank(self):
        users_position = self.get_ranked_users().limit(LIMIT).dicts()
        return users_position

    def users_position_rank_month(self):
        ranked_users = self.get_ranked_users_month()

        ranked_users_limit = User.select(
            ranked_users.c.id.alias('id'),
            ranked_users.c.discord.alias('discord'),
            ranked_users.c.xp.alias('xp'),
            ranked_users.c.position.alias('position')
        ).from_(
            ranked_users
        ).limit(
            LIMIT
        ).dicts()

        return ranked_users_limit


async def setup(bot):
    await bot.add_cog(Xp(bot))
