import logging
import os
from typing import List, Optional

from openai import OpenAI
from openai.types import VectorStore
from openai.types.beta import Assistant
from openai.types.vector_stores.vector_store_file_batch import VectorStoreFileBatch

from config.config import load_config


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

    def upload_files_batch(self, file_paths: List[str]) -> VectorStoreFileBatch:
        file_streams = [open(path, "rb") for path in file_paths]
        file_batch = self._openai_client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=self._vector_store.id,
            files=file_streams,
            max_concurrency=20,
        )
        self._update_assitant_vector_store()

        return file_batch

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
