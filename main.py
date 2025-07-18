import asyncio
import logging
import os
import sys

import logging_loki

from config.config import load_config
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

    loki_handler = logging_loki.LokiHandler(
        url=str(config.grafana_loki_url),
        auth=(config.grafana_loki_user, config.grafana_loki_password),
        tags={"application": "Test"},
    )
    root_logger.addHandler(loki_handler)

    return logging.getLogger(__name__)


async def main():
    logger = setup_logging()

    config = load_config()
    scraper = OptiSignsScraper()
    articles = await scraper.get_articles()

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

    logger.info("Starting upload of articles to vector store...")
    uploader = FileUploader()

    result = uploader.upload_files_batch(paths)
    while result.status == "in_progress":
        logger.info("Waiting for file upload to complete...")
        await asyncio.sleep(5)
    logger.info(f"File upload succeeded with {result.file_counts.completed} files.")

    if result.file_counts.failed > 0:
        logger.error(f"File upload failed with {result.file_counts.failed} files.")


if __name__ == "__main__":
    asyncio.run(main())
