import asyncio
import logging
import sys

from loki_logger_handler.loki_logger_handler import LokiLoggerHandler

from config.config import load_config
from orchestrator.orchestrator import ScraperOrchestrator


def setup_logging() -> logging.Logger:
    """Sets up logging configuration with both console and Loki handlers."""
    config = load_config()

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    root_logger.addHandler(stream_handler)

    loki_handler = LokiLoggerHandler(
        url=config.grafana_loki_url,
        labels={"application": "Test", "environment": "Develop"},
        label_keys={},
        timeout=10,
    )
    root_logger.addHandler(loki_handler)

    return logging.getLogger(__name__)


async def main():
    """Main entry point for the application."""
    setup_logging()
    logger = logging.getLogger(__name__)

    orches = ScraperOrchestrator()
    while True:
        try:
            await orches.sync()
            await asyncio.sleep(60 * 60 * 2) # Sleep for 2 hours
        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
            orches = ScraperOrchestrator()
            await asyncio.sleep(5)
        


if __name__ == "__main__":
    asyncio.run(main())
