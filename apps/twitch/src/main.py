"""
Voxelle Twitch Integration Entry Point
Handles graceful shutdown on Ctrl+C
"""

from dotenv import load_dotenv
import asyncio
import signal
import sys
import logging
from utils.args import args

load_dotenv(dotenv_path=args.env)

from utils.logging import logger
from utils.twitch_monitor import TwitchContextMonitor

# Global reference for cleanup
twitch_monitor: TwitchContextMonitor = None


async def shutdown():
    """Gracefully shutdown the Twitch monitor"""
    global twitch_monitor
    logger.info("Shutting down Twitch monitor...")
    if twitch_monitor and hasattr(twitch_monitor, "stop"):
        await twitch_monitor.stop()
    logger.info("Twitch monitor stopped")


async def main():
    global twitch_monitor
    twitch_monitor = TwitchContextMonitor()

    # Setup graceful shutdown for asyncio
    loop = asyncio.get_running_loop()
    shutdown_event = asyncio.Event()

    def signal_handler():
        logger.info("Received shutdown signal...")
        shutdown_event.set()

    # Register signal handlers (Unix-style, works differently on Windows)
    if sys.platform != "win32":
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)

    try:
        # Start the monitor
        await twitch_monitor.run()

        # Wait for shutdown signal or monitor to complete
        await shutdown_event.wait()
    except asyncio.CancelledError:
        logger.info("Twitch monitor cancelled")
    finally:
        await shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown requested via keyboard interrupt")
    except SystemExit:
        pass
