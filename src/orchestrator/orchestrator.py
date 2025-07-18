import hashlib
import logging
import os

from appredis.redis import get_redis
from config.config import load_config
from diffcheck.diff import get_dict_differences
from diffcheck.lock import ContentLock, FileId
from diffcheck.remote import RemoteContentLockStore
from scraper.optiapi.models import Article
from scraper.scraper import OptiSignsScraper
from uploader.uploader import FileUploader, OpenAIFileId
from utils.path import slugify


class ScraperOrchestrator:
    REDIS_KEY_ARTICLE_OPENAI_ID = "article_openai_id"

    def __init__(self):
        self._config = load_config()
        self._scraper = OptiSignsScraper()
        self._logger = logging.getLogger(__name__)
        self._remote_content_lock_store = RemoteContentLockStore()
        self._current_articles: list[Article] = []
        self._uploader = FileUploader()
        self._redis = get_redis()

    def _get_articles_by_names(self, article_names: list[str]) -> list[Article]:
        """
        Retrieves articles by their names from the current articles list.

        Args:
            article_names: List of article names to search for.

        Returns:
            List of Article objects that match the provided names.
        """
        return [
            article
            for article in self._current_articles
            if article.name in article_names
        ]

    async def _save_articles(self, articles: list[Article]):
        """Saves articles to the configured output path and returns the file paths."""
        logger = logging.getLogger(__name__)

        if not os.path.exists(self._config.scrape_output_path):
            os.makedirs(self._config.scrape_output_path)

        saved_paths = []
        for article in articles:
            path = os.path.join(
                self._config.scrape_output_path,
                f"{slugify(article.name, allow_unicode=True)}.md",
            )
            with open(path, "w+", encoding="utf-8") as file:
                file.write(article.body)
            article.file_path = path
            saved_paths.append(path)
            logger.debug(f"Article '{article.name}' saved to {path}")

        logger.info(f"All {len(articles)} articles have been saved successfully.")

    def _generate_file_hashes(self, articles: list[Article]) -> ContentLock:
        res: ContentLock = {}
        for article in articles:
            if not article.body:
                raise ValueError(f"Article '{article.name}' has no body content.")
            content_hash = hashlib.sha256(article.body.encode("utf-8")).hexdigest()
            res[article.id] = content_hash

        return res

    async def _create_new_articles(self, article_ids: list[int]):
        if not article_ids or len(article_ids) == 0:
            return
        selected_article_paths = [
            article.file_path
            for article in self._current_articles
            if article.id in article_ids and article.file_path is not None
        ]

        result = await self._uploader.upload_files_batch(selected_article_paths)
        self._logger.info(
            f"Batch upload completed. Successful uploads: {len(result.successful_uploads)}, "
            f"Failed uploads: {len(result.failed_uploads)}"
        )

        # Save the OpenAI file IDs for the successfully uploaded articles.
        await self._save_article_openai_file_ids(result.successful_uploads)

    async def _update_new_articles(self, article_ids: list[int]):
        if not article_ids or len(article_ids) == 0:
            return

        file_and_openai_id: dict[str, str] = await self._redis.hgetall(
            self.REDIS_KEY_ARTICLE_OPENAI_ID
        )  # type: ignore

        valid_file_paths: list[str] = []
        valid_openai_ids: list[str] = []
        articles_missing_filepath: list[int] = []
        articles_missing_openai_id: list[int] = []

        for article in self._current_articles:
            if article.id in article_ids:
                if article.file_path is None:
                    articles_missing_filepath.append(article.id)
                    self._logger.error(f"Article ID {article.id} has a None file_path.")
                    continue

                openai_id = file_and_openai_id.get(str(article.id))
                if openai_id is None:
                    articles_missing_openai_id.append(article.id)
                    self._logger.error(
                        f"OpenAI ID not found for article ID {article.id}."
                    )
                    continue

                valid_file_paths.append(article.file_path)
                valid_openai_ids.append(openai_id)

        result = await self._uploader.update_files_batch(
            valid_file_paths,
            valid_openai_ids,
        )
        self._logger.info(
            f"Batch update completed. Successful updates: {len(result.successful_uploads)}, "
            f"Failed updates: {len(result.failed_uploads)}"
        )

        await self._save_article_openai_file_ids(result.successful_uploads)

    async def _save_article_openai_file_ids(
        self, successful_uploads: dict[str, OpenAIFileId]
    ):
        if not successful_uploads:
            return

        # Map file paths back to article IDs
        article_openai_id_map: dict[FileId, OpenAIFileId] = {}
        for article in self._current_articles:
            if article.file_path in successful_uploads:
                article_openai_id_map[article.id] = successful_uploads[article.file_path]

        self._logger.debug(
            f"Saving OpenAI file IDs: {article_openai_id_map}"
        )

        current_ids = await self._redis.hgetall(self.REDIS_KEY_ARTICLE_OPENAI_ID)  # type: ignore
        if current_ids:
            self._logger.debug(
                f"Old OpenAI IDs: {current_ids}, New OpenAI IDs: {article_openai_id_map}"
            )
        else:
            self._logger.debug("No previous OpenAI IDs found.")
        current_ids.update(article_openai_id_map)
        await self._redis.hset(
            self.REDIS_KEY_ARTICLE_OPENAI_ID, mapping=current_ids
        )  # type: ignore

    async def sync(self):
        self._current_articles = await self._scraper.get_articles()
        await self._save_articles(self._current_articles)

        file_hashes = self._generate_file_hashes(self._current_articles)
        remote_file_hashes = await self._remote_content_lock_store.get()
        differences = get_dict_differences(remote_file_hashes, file_hashes)
        self._logger.info(
            f"Found {len(differences.new_keys)} new articles, "
            f"{len(differences.updated_keys)} updated articles, "
            f"{len(differences.deleted_keys)} deleted articles."
        )
        self._logger.debug(
            f"New articles: {differences.new_keys}, "
            f"Updated articles: {differences.updated_keys}, "
            f"Deleted articles: {differences.deleted_keys}"
        )

        skipped = len(file_hashes.keys()) - len(differences.new_keys) - len(differences.updated_keys)
        self._logger.info(
            f"Skipping {skipped} articles that are already up-to-date."
        )


        self._logger.info(
            f"Creating {len(differences.new_keys)} new articles"
        )
        await self._create_new_articles(differences.new_keys)

        self._logger.info(
            f"Updating {len(differences.updated_keys)} existing articles"
        )
        await self._update_new_articles(differences.updated_keys)

        # Update the remote content lock store with new and updated files
        await self._remote_content_lock_store.update(file_hashes)
