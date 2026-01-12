"""
Voxelle Discord Bot Entry Point
Handles graceful shutdown on Ctrl+C
"""

from utils.args import args
from utils.logging import setup_logging

setup_logging()
from dotenv import load_dotenv

load_dotenv(dotenv_path=args.env)

import os
import asyncio
import signal
import sys
import logging
from utils.bot import DiscordBot

# Global reference for cleanup
discord_bot: DiscordBot = None


async def shutdown(bot: DiscordBot):
    """Gracefully shutdown the Discord bot"""
    logging.info("Shutting down Discord bot...")
    if bot and not bot.is_closed():
        await bot.close()
    logging.info("Discord bot stopped")


async def main():
    global discord_bot
    discord_bot = DiscordBot()

    # Setup graceful shutdown for asyncio
    loop = asyncio.get_running_loop()

    def signal_handler():
        logging.info("Received shutdown signal...")
        asyncio.create_task(shutdown(discord_bot))

    # Register signal handlers (Unix-style, works differently on Windows)
    if sys.platform != "win32":
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)

    try:
        await discord_bot.login(os.getenv("DISCORD_BOT_TOKEN"))
        await discord_bot.connect()
    except asyncio.CancelledError:
        logging.info("Bot connection cancelled")
    finally:
        await shutdown(discord_bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutdown requested via keyboard interrupt")
    except SystemExit:
        pass
