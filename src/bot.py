import argparse
import logging
import sys

import discord
from discord.ext import commands

from src.config import DISCORD_TOKEN, require_token, GUILD_ID
from src.utils.logger import setup_logging


def load_cogs(bot: commands.Bot) -> None:
    logger = logging.getLogger("Aethor")
    for ext in ("src.cogs.general", "src.cogs.admin", "src.cogs.minecraft", "src.cogs.management"):
        try:
            bot.load_extension(ext)
            logger.info(f"Loaded cog {ext}")
        except Exception as e:
            logger.exception(f"Failed to load {ext}: {e}")


def build_bot() -> commands.Bot:
    intents = discord.Intents.default()
    intents.message_content = True  # for prefix commands
    bot = commands.Bot(command_prefix="!", intents=intents)
    return bot


def main() -> None:
    parser = argparse.ArgumentParser(description="Aethor Discord Bot")
    parser.add_argument("--check", action="store_true", help="Validate setup and cogs, then exit.")
    parser.add_argument("--sync", action="store_true", help="Sync slash commands on ready.")
    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger("Aethor")

    bot = build_bot()
    load_cogs(bot)

    if args.check:
        logger.info("Smoke-check complete: config imported and cogs loaded.")
        sys.exit(0)

    require_token()

    @bot.event
    async def on_ready():
        logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
        if args.sync:
            try:
                if GUILD_ID:
                    guild = discord.Object(id=GUILD_ID)
                    await bot.tree.sync(guild=guild)
                    logger.info(f"Synced slash commands to guild {GUILD_ID}")
                else:
                    await bot.tree.sync()
                    logger.info("Synced global slash commands")
            except Exception as e:
                logger.exception(f"Failed to sync commands: {e}")

    bot.run(DISCORD_TOKEN, log_handler=None)


if __name__ == "__main__":
    main()
