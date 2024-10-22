from decouple import config
from discord import Member, VoiceState
from discord.ext import commands, tasks
from discord.ext.commands import Bot

from app.db.models import Study, User, db
from app.utils import msg_time

ALLOWED_CHANNELS = list(
    map(lambda x: int(x), config('ALLOWED_CHANNELS').split(', '))
)
GUILD_ID = int(config('GUILD_ID', 0))
TIME_XP = int(config('TIME_XP', 60))

LIMIT = int(config('LIMIT', 10))


class Xp2(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        Faz os primeiros ajustes
        """
        print(f'Cog - {__name__} is online')

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
            print(
                f'{msg_time()} XP: Bot',
                f'{member.name} ignorado no move_users.'
            )
            return

        print('03')
        db.connect()
        db.create_tables([User, Study])

        print('oi2')
        if before.channel is None and after.channel is not None:
            if after.channel.id not in ALLOWED_CHANNELS:
                return

            print('oi')
            print(after.channel.id)

            user = self.get_user(member)
            print(user)
            study = Study.create(
                user=user,
                channel=after.channel.id
            )
            print('oi0')
            study.save()
            print('User', user)
            print('Study', study)

        db.close()

    def get_user(self, member: Member):
        db.connect()
        user = User.get(User.discord == member.id)
        guild = self.bot.get_guild(GUILD_ID)

        print(guild)
        print('foda')
        print(user)

        if not user:
            user = User.create(
                discord=member.id,
                guild=guild.id,
                xp=0
            )
            user.save()

        print(user)

        db.close()
        return user


async def setup(bot):
    ...
    # await bot.add_cog(Xp2(bot))
