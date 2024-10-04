import datetime
import random

import discord
from decouple import config
from discord.ext import tasks
from discord.ext.commands import Bot

from app.utils import msg_time

LOCK_CHANNEL_ID = int(config('LOCK_CHANNEL_ID', 0))
UTC = int(config('UTC', 1))
ROLE_ID = int(config('ROLE_ID', 0))

H_OPEN = int(config('H_OPEN', 5))
M_OPEN = int(config('M_OPEN', 30))

H_CLOSE = int(config('H_CLOSE', 0))
M_CLOSE = int(config('M_CLOSE', 0))


OFFSET = datetime.timedelta(hours=UTC)
TZ = datetime.timezone(OFFSET)

TIME_TO_OPEN = datetime.time(hour=H_OPEN, minute=M_OPEN, tzinfo=TZ)
TIME_TO_CLOSE = datetime.time(hour=H_CLOSE, minute=M_CLOSE, tzinfo=TZ)


MOTIVATIONAL_QUOTES: list[str] = [
    "Você é mais forte do que imagina.",
    "Nunca desista dos seus sonhos.",
    "Acredite em si mesmo e tudo será possível.",
    "O sucesso é a soma de pequenos esforços repetidos dia após dia.",
    "A vida começa onde sua zona de conforto termina.",
    "Seja a mudança que você deseja ver no mundo.",
    "Cada dia é uma nova chance para melhorar.",
    "A persistência é o caminho do êxito.",
    "Faça o que você ama e nunca terá que trabalhar um dia na vida.",
    "Seus sonhos não têm data de validade.",
    "Desafios são oportunidades disfarçadas.",
    "Nunca é tarde para ser o que você poderia ter sido.",
    "O sucesso é a soma de pequenos esforços.",
    "Se você pode sonhar, você pode realizar.",
    "Grandes conquistas começam com pequenos passos.",
    "A vitória pertence ao mais persistente.",
    "O único limite para o seu sucesso é a sua mente.",
    "Não espere por uma oportunidade, crie-a.",
    "Acredite que você pode e já está no meio do caminho.",
    "Você não precisa ser grande para começar, mas precisa começar para ser grande.",  # noqa: E501
    "O caminho para o sucesso é sempre em construção.",
    "Transforme seus obstáculos em oportunidades.",
    "Não conte os dias, faça os dias contarem.",
    "O fracasso é apenas a oportunidade de começar de novo, com mais inteligência.",  # noqa: E501
    "Seja corajoso. A vida recompensa quem ousa.",
    "O futuro pertence àqueles que acreditam na beleza de seus sonhos.",
    "Cada dia é uma nova oportunidade para mudar sua vida.",
    "A única maneira de fazer um excelente trabalho é amar o que você faz.",
    "A jornada de mil milhas começa com um único passo.",
    "Você é capaz de realizar coisas incríveis."
]

SLEEP_MOTIVATIONAL_QUOTES: list[str] = [
    "Uma boa noite de sono é o melhor investimento para um dia produtivo.",
    "Dormir bem é o primeiro passo para acordar com energia e motivação.",
    "O descanso adequado é a chave para uma mente e corpo saudáveis.",
    "Um sono de qualidade é a fundação do sucesso e da felicidade.",
    "Cada boa noite de sono é um passo em direção ao seu melhor eu.",
    "O sono reparador é a melhor forma de recarregar suas energias.",
    "Dormir bem é um ato de autocuidado e amor próprio.",
    "A qualidade do seu sono determina a qualidade do seu dia.",
    "Uma mente descansada é uma mente criativa e produtiva.",
    "Aproveite cada noite de sono como uma oportunidade para se renovar e crescer."  # noqa: E501
]


@tasks.loop(time=[TIME_TO_OPEN, TIME_TO_CLOSE])
async def lock_unlock_vip(bot: Bot, GUILD_ID: int) -> None:
    """
    Libera e bloqueia o chat geral
    """

    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(int(LOCK_CHANNEL_ID))

    vip_role = guild.get_role(ROLE_ID)

    overwrite = channel.overwrites_for(vip_role)
    message = 'Mensagem não carregada. Avisar os moderadores.'
    quote = 'Mensagem não carregada. Avisar os moderadores.'
    color = discord.Color.blue()

    if overwrite.send_messages:
        overwrite.send_messages = False
        quote = random.choice(SLEEP_MOTIVATIONAL_QUOTES)
        color = discord.Color.purple()

        message = (
            'Canal bloqueado. Boa noite! '
            '**Bora de dormes,** amanhã é outro dia 💤'
        )

    else:
        overwrite.send_messages = True
        quote = random.choice(MOTIVATIONAL_QUOTES)
        color = discord.Color.yellow()

        message = (
            'Canal liberado. Bom dia! '
            '**Foco no papiro!!** 🎯'
        )

    embed = discord.Embed(
        title=message,
        color=color,
        description=quote,
    )

    embed.set_footer(text="[MENSAGEM AUTOMÁTICA] pelo @Bot em Evidência#3468")
    await channel.send(embed=embed)
    await channel.set_permissions(vip_role, overwrite=overwrite)
    print(f'{msg_time()} LOCK_CHAT: Loop completo')
