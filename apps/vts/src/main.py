"""
Voxelle VTube Studio Integration Entry Point
Handles graceful shutdown on Ctrl+C
"""

import yaml
import asyncio
import signal
import sys
from utils.args import args
from utils.logging import logger
from utils.vts_plugin import VTSHotkeyPlugin

# Global reference for cleanup
vts_plugin: VTSHotkeyPlugin = None


async def shutdown():
    """Gracefully shutdown the VTS plugin"""
    global vts_plugin
    logger.info("Shutting down VTS plugin...")
    if vts_plugin and hasattr(vts_plugin, "stop"):
        await vts_plugin.stop()
    logger.info("VTS plugin stopped")


async def main():
    global vts_plugin

    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    vts_plugin = VTSHotkeyPlugin(config)

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
        await vts_plugin.start()
        logger.info("VTS Hotkey Plugin initialized and running")

        # Wait for shutdown signal
        await shutdown_event.wait()
    except asyncio.CancelledError:
        logger.info("VTS plugin cancelled")
    finally:
        await shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown requested via keyboard interrupt")
    except SystemExit:
        pass
