"""OptiSigns API client implementation."""
from typing import Optional
from urllib.parse import urljoin

import httpx

from .models import CategoriesResponse


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
            page = response.next_page

        return responses
