"""OptiSigns API client implementation."""
from typing import Optional
from urllib.parse import urljoin

import httpx
from logging import log

from .models import CategoriesResponse, SectionsResponse, ArticlesResponse


class OptiSignsClient:
    """Client for accessing the OptiSigns help center API."""

    BASE_URL = "https://support.optisigns.com/api/v2/help_center/"

    def __init__(self, locale: str = "en-us", timeout: int = 30):
        """Initialize the client.

        Args:
            locale: Language locale for the API requests (default: "en-us")
            timeout: Request timeout in seconds (default: 30)
        """
        self.locale = locale
        self.timeout = timeout
        self._session: Optional[httpx.AsyncClient] = None

    @property
    def session(self) -> httpx.AsyncClient:
        """Get or create an HTTP session."""
        if self._session is None:
            headers = {
            }
            self._session = httpx.AsyncClient(
                timeout=self.timeout,
                headers=headers,
                follow_redirects=True,
            )
        return self._session

    async def close(self):
        """Close the HTTP session."""
        if self._session:
            await self._session.aclose()
            self._session = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def get_categories(
        self,
        sort_by: str = "position",
        sort_order: str = "asc",
        per_page: int = 100,
        page: int = 1,
    ) -> CategoriesResponse:
        """Get help center categories.

        Args:
            sort_by: Field to sort by (default: "position")
            sort_order: Sort order "asc" or "desc" (default: "asc")
            per_page: Number of items per page (default: 100)
            page: Page number (default: 1)

        Returns:
            CategoriesResponse: The categories response

        Raises:
            httpx.HTTPStatusError: If the request fails
            ValidationError: If the response cannot be parsed
        """
        params = {
            "sort_by": sort_by,
            "sort_order": sort_order,
            "per_page": per_page,
            "page": page,
        }

        url = urljoin(self.BASE_URL, f"{self.locale}/categories.json")

        response = await self.session.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        return CategoriesResponse.model_validate(data)

    async def get_all_categories(
        self,
        sort_by: str = "position",
        sort_order: str = "asc",
        per_page: int = 100,
    ) -> list[CategoriesResponse]:
        """Get all categories across all pages.

        Args:
            sort_by: Field to sort by (default: "position")
            sort_order: Sort order "asc" or "desc" (default: "asc")
            per_page: Number of items per page (default: 100)

        Returns:
            list[CategoriesResponse]: All category responses
        """
        responses = []
        page = 1

        while True:
            response = await self.get_categories(
                sort_by=sort_by,
                sort_order=sort_order,
                per_page=per_page,
                page=page,
            )
            responses.append(response)

            if response.next_page is None:
                break
            page += 1

        return responses

    async def get_sections(
        self,
        category_id: int,
        sort_by: str = "position",
        sort_order: str = "asc",
        per_page: int = 100,
        page: int = 1,
    ) -> SectionsResponse:
        """Get sections for a specific category.

        Args:
            category_id: The ID of the category to get sections for
            sort_by: Field to sort by (default: "position")
            sort_order: Sort order "asc" or "desc" (default: "asc")
            per_page: Number of items per page (default: 100)
            page: Page number (default: 1)

        Returns:
            SectionsResponse: The sections response

        Raises:
            httpx.HTTPStatusError: If the request fails
            ValidationError: If the response cannot be parsed
        """
        params = {
            "sort_by": sort_by,
            "sort_order": sort_order,
            "per_page": per_page,
            "page": page,
        }

        url = urljoin(self.BASE_URL, f"{self.locale}/categories/{category_id}/sections.json")

        response = await self.session.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        return SectionsResponse.model_validate(data)

    async def get_all_sections(
        self,
        category_id: int,
        sort_by: str = "position",
        sort_order: str = "asc",
        per_page: int = 100,
    ) -> list[SectionsResponse]:
        """Get all sections for a specific category across all pages.

        Args:
            category_id: The ID of the category to get sections for
            sort_by: Field to sort by (default: "position")
            sort_order: Sort order "asc" or "desc" (default: "asc")
            per_page: Number of items per page (default: 100)

        Returns:
            list[SectionsResponse]: All section responses
        """
        responses = []
        page = 1

        while True:
            response = await self.get_sections(
                category_id=category_id,
                sort_by=sort_by,
                sort_order=sort_order,
                per_page=per_page,
                page=page,
            )
            responses.append(response)

            if response.next_page is None:
                break
            page += 1

        return responses

    async def get_articles(
        self,
        section_id: int,
        sort_by: str = "position",
        sort_order: str = "asc",
        per_page: int = 100,
        page: int = 1,
    ) -> ArticlesResponse:
        """Get articles for a specific section.

        Args:
            section_id: The ID of the section to get articles for
            sort_by: Field to sort by (default: "position")
            sort_order: Sort order "asc" or "desc" (default: "asc")
            per_page: Number of items per page (default: 100)
            page: Page number (default: 1)

        Returns:
            ArticlesResponse: The articles response

        Raises:
            httpx.HTTPStatusError: If the request fails
            ValidationError: If the response cannot be parsed
        """
        params = {
            "sort_by": sort_by,
            "sort_order": sort_order,
            "per_page": per_page,
            "page": page,
        }

        url = urljoin(self.BASE_URL, f"{self.locale}/sections/{section_id}/articles.json")

        response = await self.session.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        return ArticlesResponse.model_validate(data)

    async def get_all_articles(
        self,
        section_id: int,
        sort_by: str = "position",
        sort_order: str = "asc",
        per_page: int = 100,
    ) -> list[ArticlesResponse]:
        """Get all articles for a specific section across all pages.

        Args:
            section_id: The ID of the section to get articles for
            sort_by: Field to sort by (default: "position")
            sort_order: Sort order "asc" or "desc" (default: "asc")
            per_page: Number of items per page (default: 100)

        Returns:
            list[ArticlesResponse]: All article responses
        """
        responses = []
        page = 1

        while True:
            response = await self.get_articles(
                section_id=section_id,
                sort_by=sort_by,
                sort_order=sort_order,
                per_page=per_page,
                page=page,
            )
            responses.append(response)

            if response.next_page is None:
                break
            page += 1

        return responses
