"""
Voxelle Core Server Entry Point
Handles graceful shutdown on Ctrl+C
"""

from utils.logging import setup_logger

setup_logger()

from utils.args import args
from dotenv import load_dotenv

load_dotenv(dotenv_path=args.env)

import asyncio
import signal
import sys
import logging
from utils.server import start_web_server


def handle_shutdown(signum, frame):
    """Handle shutdown signals gracefully"""
    sig_name = signal.Signals(signum).name
    logging.info(f"Received {sig_name}, initiating graceful shutdown...")
    sys.exit(0)


def main():
    # Register signal handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # Windows-specific: handle Ctrl+C properly
    if sys.platform == "win32":
        signal.signal(signal.SIGBREAK, handle_shutdown)

    try:
        asyncio.run(start_web_server())
    except KeyboardInterrupt:
        logging.info("Shutdown requested via keyboard interrupt")
    except SystemExit:
        pass
    finally:
        logging.info("Voxelle Core Server stopped")


if __name__ == "__main__":
    main()
