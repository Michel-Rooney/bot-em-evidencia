from time import sleep

from decouple import config
from discord.ext import tasks
from discord.ext.commands import Bot

from app.utils import msg_time

MOVE_USER_LOOP_INTERVAL_MIN = int(config('MOVE_USER_LOOP_INTERVAL_MIN', 2))
MOVE_USER_SOURCE_CHANNEL_ID = list(map(lambda id: int(id), config(
    'MOVE_USER_SOURCE_CHANNEL_ID', 0
).split(', ')))
MOVE_USER_TARGET_CHANNEL_ID = int(config('MOVE_USER_TARGET_CHANNEL_ID', 0))


@tasks.loop(minutes=MOVE_USER_LOOP_INTERVAL_MIN)
async def move_users(bot: Bot, GUILD_ID: int) -> None:
    """
    Move os usuários da call, no qual não estão com a câmera
    ou a transmissão ligada
    """

    members = []
    guild = bot.get_guild(GUILD_ID)
    source_channel = map(
        lambda id: guild.get_channel(id),
        MOVE_USER_SOURCE_CHANNEL_ID
    )
    target_channel = guild.get_channel(MOVE_USER_TARGET_CHANNEL_ID)

    for channel in source_channel:
        members.extend(channel.members)

    if (not source_channel) or (not target_channel):
        print(
            f'{msg_time()} MOVE_USER: SOURCE_CHANNEL',
            'OU TARGET_CHANNEL INVÁLIDO.'
        )
        return

    for member in members:
        sleep(0.5)

        if member.bot:
            print(
                f'{msg_time()} MOVE_USERS: Bot',
                f'{member.name} ignorado no move_users.'
            )
            continue

        if member.voice.self_video or member.voice.self_stream:
            continue

        try:
            message = (
                f'**[MODERAÇÃO ESTUDOS EM EVIDÊNCIA]** Olá **{member.name}**,'
                'o canal **"(WEBCAM OU TELA ON)"** é apenas para câmeras ou'
                'streams ligadas. Portanto, você foi movido para sala'
                '**"GERAL"**.'
            )
            await member.send(message)
            await member.move_to(target_channel)

            print(
                f'{msg_time()} MOVE_USERS: MOVED',
                f'{member.name} to {target_channel.name}'
            )
        except Exception as e:
            print(
                f'{msg_time()} MOVE_USER: ERRO AO ENVIAR',
                f'MENSAGEM: {member.name}\n {e}'
            )

    print(f'{msg_time()} MOVE_USERS: Loop completo')
