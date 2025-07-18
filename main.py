import asyncio
import logging
import os
import sys

from loki_logger_handler.loki_logger_handler import LokiLoggerHandler

from config.config import load_config
from scraper.optiapi.models import Article
from scraper.scraper import OptiSignsScraper
from uploader.uploader import FileUploader
from utils.path import slugify


def setup_logging():
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


async def save_articles(articles: list[Article]) -> list[str]:
    """Saves articles to the configured output path."""
    config = load_config()
    logger = setup_logging()

    if not os.path.exists(config.scrape_output_path):
        os.makedirs(config.scrape_output_path)

    paths = [
        os.path.join(
            config.scrape_output_path, f"{slugify(article.name, allow_unicode=True)}.md"
        )
        for article in articles
    ]
    article_and_paths = list(zip(articles, paths))
    for article, path in article_and_paths:
        with open(path, "w+", encoding="utf-8") as file:
            file.write(article.body)
        logger.info(f"Article '{article.name}' will be saved to {path}")
    logger.info("All articles have been saved successfully.")
    return paths


async def main():
    logger = setup_logging()

    logger.info("Scraping articles from OptiSigns...")
    scraper = OptiSignsScraper()
    articles = await scraper.get_articles()
    scraped_paths = await save_articles(articles)

    logger.info("Starting upload of articles to vector store...")
    uploader = FileUploader()
    result = await uploader.upload_files_batch(scraped_paths)
    logger.info(
        f"Batch upload completed. Successful uploads: {len(result.successful_uploads)}, Failed uploads: {len(result.failed_uploads)}"
    )


if __name__ == "__main__":
    asyncio.run(main())
