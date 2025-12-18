import discord
from typing import Optional

from src.config import MOD_LOG_CHANNEL_ID


async def send_mod_log(bot: discord.Client, title: str, description: str, *, color: int = 0xE67E22):
    if not MOD_LOG_CHANNEL_ID:
        return
    chan = bot.get_channel(MOD_LOG_CHANNEL_ID)
    if not isinstance(chan, discord.TextChannel):
        return
    embed = discord.Embed(title=title, description=description, color=color)
    try:
        await chan.send(embed=embed)
    except Exception:
        pass
