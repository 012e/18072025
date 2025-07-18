import asyncio
import hashlib
import logging
import os
import sys

from loki_logger_handler.loki_logger_handler import LokiLoggerHandler
from pydantic.dataclasses import dataclass

from config.config import load_config
from scraper.optiapi.models import Article
from scraper.scraper import OptiSignsScraper
from uploader.uploader import FileUploader
from utils.path import slugify


@dataclass
class FileMetadata:
    """Metadata for a file to be uploaded."""

    openai_file_id: str
    content_hash: str


file_metadata_cache: dict[str, FileMetadata] = {}


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


async def save_articles(articles: list[Article]) -> list[str]:
    """Saves articles to the configured output path and returns the file paths."""
    config = load_config()
    logger = logging.getLogger(__name__)

    if not os.path.exists(config.scrape_output_path):
        os.makedirs(config.scrape_output_path)

    saved_paths = []
    for article in articles:
        path = os.path.join(
            config.scrape_output_path, f"{slugify(article.name, allow_unicode=True)}.md"
        )
        with open(path, "w+", encoding="utf-8") as file:
            file.write(article.body)
        article.path = path
        saved_paths.append(path)
        logger.info(f"Article '{article.name}' saved to {path}")

    logger.info(f"All {len(articles)} articles have been saved successfully.")
    return saved_paths


def generate_file_hashes(
    articles: list[Article], successful_uploads: list[tuple[str, str]]
) -> dict[str, FileMetadata]:
    """
    Generates a mapping of file paths to their metadata for successfully uploaded articles.

    Args:
        articles: List of articles that were processed
        successful_uploads: List of tuples containing (file_path, openai_file_id) for successful uploads

    Returns:
        Dictionary mapping file paths to FileMetadata objects
    """
    file_metadata = {}
    upload_dict = dict(successful_uploads)  # Convert to dict for O(1) lookup

    for article in articles:
        if article.path and article.path in upload_dict:
            content_hash = hashlib.sha256(article.body.encode("utf-8")).hexdigest()
            openai_file_id = upload_dict[article.path]
            file_metadata[article.path] = FileMetadata(
                openai_file_id=openai_file_id, content_hash=content_hash
            )

    return file_metadata


def attach_openai_file_ids_to_articles(
    articles: list[Article], successful_uploads: list[tuple[str, str]]
) -> None:
    """
    Attaches OpenAI file IDs to articles that were successfully uploaded.

    Args:
        articles: List of articles to update
        successful_uploads: List of tuples containing (file_path, openai_file_id) for successful uploads
    """
    upload_dict = dict(successful_uploads)  # Convert to dict for O(1) lookup

    for article in articles:
        if article.path and article.path in upload_dict:
            article.openai_file_id = upload_dict[article.path]


def update_global_file_metadata(new_metadata: dict[str, FileMetadata]) -> None:
    """Updates the global file metadata cache with new file metadata."""
    global file_metadata_cache
    file_metadata_cache = new_metadata


async def main():
    """Main entry point for the application."""
    logger = setup_logging()

    try:
        logger.info("Scraping articles from OptiSigns...")
        scraper = OptiSignsScraper()
        articles = await scraper.get_articles()

        if not articles:
            logger.warning("No articles found to process.")
            return

        logger.info(f"Found {len(articles)} articles to process.")

        logger.info("Saving articles to local files...")
        saved_paths = await save_articles(articles)

        logger.info("Starting upload of articles to vector store...")
        uploader = FileUploader()
        # TODO: retry logic for failed uploads
        result = await uploader.upload_files_batch(saved_paths)
        logger.info(
            f"Batch upload completed. Successful uploads: {len(result.successful_uploads)}, "
            f"Failed uploads: {len(result.failed_uploads)}"
        )

        if result.failed_uploads:
            logger.warning(
                f"Failed to upload the following files: {result.failed_uploads}"
            )

        # Attach OpenAI file IDs to successfully uploaded articles
        if result.successful_uploads:
            attach_openai_file_ids_to_articles(articles, result.successful_uploads)
            logger.info(
                f"Attached OpenAI file IDs to {len(result.successful_uploads)} articles."
            )

            # Generate and update file hashes for successful uploads
            file_hashes = generate_file_hashes(articles, result.successful_uploads)
            update_global_file_metadata(file_hashes)
            logger.info(f"Updated file hashes for {len(file_hashes)} files.")
        else:
            logger.error("No files were successfully uploaded.")

    except Exception as e:
        logger.error(f"An error occurred during execution: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
