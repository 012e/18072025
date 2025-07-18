import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Optional

from openai import OpenAI
from openai.types import VectorStore
from openai.types.beta import Assistant

from config.config import load_config

type OpenAIFileId = str


@dataclass
class BatchUploadResult:
    """
    Represents the result of a batch file upload operation.
    """

    successful_uploads: dict[str, OpenAIFileId]
    failed_uploads: list[str]


class FileUploader:
    def __init__(self):
        config = load_config()
        self._openai_client = OpenAI(api_key=config.openai_api_key)
        self._vector_store = self._get_or_create_vector_store()
        self._assistant = self._get_or_create_assistant()
        self._logger = logging.getLogger(__name__)

    def _create_new_assistant(self) -> Assistant:
        """
        Create a new assistant for financial analysis.
        """
        try:
            return self._openai_client.beta.assistants.create(
                name="Financial Analyst Assistant",
                instructions="You are an expert financial analyst. Use your knowledge base to answer questions about audited financial statements.",
                model="gpt-4o",
                tools=[{"type": "file_search"}],
                tool_resources={
                    "file_search": {"vector_store_ids": [self._vector_store.id]}
                },
            )
        except Exception as e:
            self._logger.error(f"Error creating assistant: {e}")
            raise

    def _create_new_vector_store(self) -> VectorStore:
        """
        Create a new vector store for financial documents.
        """
        try:
            return self._openai_client.vector_stores.create(
                name="Financial Documents Store",
                expires_after={"anchor": "last_active_at", "days": 30},
            )
        except Exception as e:
            self._logger.error(f"Error creating vector store: {e}")
            raise

    def _get_or_create_assistant(self) -> Assistant:
        """
        Get existing assistant or create a new one for financial analysis.
        """
        try:
            # WARN: This is a paginated API
            assistants = self._openai_client.beta.assistants.list()
            for assistant in assistants.data:
                if assistant.name == "Financial Analyst Assistant":
                    # Update the assistant to ensure it has the latest vector store
                    return self._openai_client.beta.assistants.update(
                        assistant_id=assistant.id,
                        tool_resources={
                            "file_search": {"vector_store_ids": [self._vector_store.id]}
                        },
                    )

            # Create new assistant if none exists
            return self._create_new_assistant()
        except Exception as e:
            self._logger.error(f"Error creating/getting assistant: {e}")
            raise

    def _update_assitant_vector_store(self):
        self._assistant = self._openai_client.beta.assistants.update(
            assistant_id=self._assistant.id,
            tool_resources={
                "file_search": {"vector_store_ids": [self._vector_store.id]}
            },
        )

    def _get_or_create_vector_store(self) -> VectorStore:
        """
        Get existing vector store or create a new one for financial documents.
        """
        try:
            # WARN: This is a paginated API
            # Try to find existing vector store by name
            vector_stores = self._openai_client.vector_stores.list()
            for store in vector_stores.data:
                if store.name == "Financial Documents Store":
                    return store

            return self._create_new_vector_store()
        except Exception as e:
            self._logger.error(f"Error creating/getting vector store: {e}")
            raise

    def upload_file(self, file_path: str) -> Optional[str]:
        """
        Upload a file to the vector store for financial analysis.

        Args:
            file_path (str): Path to the file to upload

        Returns:
            Optional[str]: File ID if successful, None otherwise
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                self._logger.error(f"File not found: {file_path}")
                return None

            # Upload file to OpenAI
            with open(file_path, "rb") as file:
                uploaded_file = self._openai_client.files.create(
                    file=file, purpose="assistants"
                )

            # Add file to vector store
            self._openai_client.vector_stores.files.create(
                vector_store_id=self._vector_store.id, file_id=uploaded_file.id
            )

            self._logger.info(
                f"Successfully uploaded file: {file_path} (ID: {uploaded_file.id})"
            )
            self._update_assitant_vector_store()
            return uploaded_file.id

        except Exception as e:
            self._logger.info(f"Error uploading file {file_path}: {e}")
            return None

    async def _delete_file_async(self, file_id: str):
        loop = asyncio.get_event_loop()

        def _delete_sync():
            try:
                self._openai_client.vector_stores.files.delete(
                    vector_store_id=self._vector_store.id, file_id=file_id
                )
                self._openai_client.files.delete(file_id=file_id)
                self._logger.info(f"Successfully deleted file {file_id}.")
            except Exception as e:
                self._logger.error(
                    f"Failed to delete file {file_id}. It may have already been deleted. Error: {e}"
                )

        await loop.run_in_executor(None, _delete_sync)

    async def update_files_batch(
        self, file_paths: list[str], openai_ids: list[str]
    ) -> BatchUploadResult:
        """
        Deletes a batch of old files and uploads a new batch in their place.

        Args:
            file_paths (list[str]): List of new file paths to upload.
            openai_ids (list[str]): List of OpenAI file IDs to delete.

        Returns:
            BatchUploadResult: Result of the new upload operation.
        """
        delete_tasks = [self._delete_file_async(file_id) for file_id in openai_ids]
        if delete_tasks:
            await asyncio.gather(*delete_tasks)

        return await self.upload_files_batch(file_paths)

    async def upload_file_async(self, file_path: str) -> tuple[str, Optional[str]]:
        """
        Upload a file to the vector store for financial analysis (async version).

        Args:
            file_path (str): Path to the file to upload

        Returns:
            tuple[str, Optional[str]]: (file_path, file_id) if successful, (file_path, None) if failed
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                self._logger.error(f"File not found: {file_path}")
                return file_path, None

            # Run the file upload in a thread pool since OpenAI client is sync
            loop = asyncio.get_event_loop()

            def upload_file_sync():
                with open(file_path, "rb") as file:
                    uploaded_file = self._openai_client.files.create(
                        file=file, purpose="assistants"
                    )

                self._openai_client.vector_stores.files.create(
                    vector_store_id=self._vector_store.id, file_id=uploaded_file.id
                )
                return uploaded_file.id

            file_id = await loop.run_in_executor(None, upload_file_sync)

            self._logger.info(
                f"Successfully uploaded file: {file_path} (ID: {file_id})"
            )
            return file_path, file_id

        except Exception as e:
            self._logger.error(f"Error uploading file {file_path}: {e}")
            return file_path, None

    async def upload_files_batch(self, file_paths: list[str]) -> BatchUploadResult:
        """
        Upload multiple files to the vector store in parallel.

        Args:
            file_paths (List[str]): List of file paths to upload

        Returns:
            BatchUploadResult: Result containing successful and failed uploads
        """
        # Upload all files in parallel
        upload_tasks = [self.upload_file_async(file_path) for file_path in file_paths]
        results = await asyncio.gather(*upload_tasks, return_exceptions=True)

        successful_uploads = {}
        failed_uploads = []

        for result in results:
            if isinstance(result, Exception):
                failed_uploads.append(f"Unknown file ({result})")
            else:
                file_path, file_id = result
                if file_id:
                    successful_uploads[file_path] = file_id
                else:
                    failed_uploads.append(f"{file_path} (Upload failed)")

        # Update assistant vector store once after all uploads
        if successful_uploads:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self._update_assitant_vector_store)
            except Exception as e:
                self._logger.error(f"Error updating assistant vector store: {e}")

        return BatchUploadResult(
            successful_uploads=successful_uploads,
            failed_uploads=failed_uploads,
        )

    @property
    def assistant(self) -> Assistant:
        """Get the assistant instance."""
        return self._assistant

    @property
    def vector_store(self) -> VectorStore:
        """Get the vector store instance."""
        return self._vector_store

    def get_assistant_id(self) -> str:
        """Get the assistant ID for use in conversations."""
        return self._assistant.id

    def list_uploaded_files(self):
        """List all files in the vector store."""
        try:
            files = self._openai_client.vector_stores.files.list(
                vector_store_id=self._vector_store.id
            )
            return files.data
        except Exception as e:
            self._logger.error(f"Error listing files: {e}")
            return []
