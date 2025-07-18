"""OptiSigns API client implementation."""
from typing import Optional
from urllib.parse import urljoin

import httpx
import logging

from .models import CategoriesResponse, SectionsResponse, ArticlesResponse, Category, Section, Article

logger = logging.getLogger(__name__)


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
        logger.debug("OptiSignsClient initialized with locale: %s, timeout: %s", locale, timeout)

    @property
    def session(self) -> httpx.AsyncClient:
        """Get or create an HTTP session."""
        if self._session is None:
            headers = {}
            self._session = httpx.AsyncClient(
                timeout=self.timeout,
                headers=headers,
                follow_redirects=True,
            )
            logger.debug("HTTPX AsyncClient session created.")
        return self._session

    async def close(self):
        """Close the HTTP session."""
        if self._session:
            await self._session.aclose()
            self._session = None
            logger.debug("HTTPX AsyncClient session closed.")

    async def __aenter__(self):
        """Async context manager entry."""
        logger.debug("Entering async context for OptiSignsClient.")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        logger.debug("Exiting async context for OptiSignsClient.")
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
        logger.debug("Attempting to get categories with params: %s", params)

        url = urljoin(self.BASE_URL, f"{self.locale}/categories.json")
        logger.debug("Request URL: %s", url)

        response = await self.session.get(url, params=params)
        logger.debug("Response status code: %s", response.status_code)
        response.raise_for_status()
        logger.debug("Successfully fetched categories.")

        data = response.json()
        return CategoriesResponse.model_validate(data)

    async def get_all_categories(
        self,
        sort_by: str = "position",
        sort_order: str = "asc",
        per_page: int = 100,
    ) -> list[Category]:
        """Get all categories across all pages.

        Args:
            sort_by: Field to sort by (default: "position")
            sort_order: Sort order "asc" or "desc" (default: "asc")
            per_page: Number of items per page (default: 100)

        Returns:
            list[Category]: All categories
        """
        categories = []
        page = 1
        logger.debug("Fetching all categories.")

        while True:
            response = await self.get_categories(
                sort_by=sort_by,
                sort_order=sort_order,
                per_page=per_page,
                page=page,
            )
            categories.extend(response.categories)
            logger.debug("Fetched page %d of categories. Next page: %s", page, response.next_page)

            if response.next_page is None:
                logger.debug("No more category pages to fetch.")
                break
            page += 1

        logger.debug("Finished fetching all categories. Total categories: %d", len(categories))
        return categories

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
        logger.debug("Attempting to get sections for category_id: %s with params: %s", category_id, params)

        url = urljoin(self.BASE_URL, f"{self.locale}/categories/{category_id}/sections.json")
        logger.debug("Request URL: %s", url)

        response = await self.session.get(url, params=params)
        logger.debug("Response status code: %s", response.status_code)
        response.raise_for_status()
        logger.debug("Successfully fetched sections for category_id: %s.", category_id)

        data = response.json()
        return SectionsResponse.model_validate(data)

    async def get_all_sections(
        self,
        category_id: int,
        sort_by: str = "position",
        sort_order: str = "asc",
        per_page: int = 100,
    ) -> list[Section]:
        """Get all sections for a specific category across all pages.

        Args:
            category_id: The ID of the category to get sections for
            sort_by: Field to sort by (default: "position")
            sort_order: Sort order "asc" or "desc" (default: "asc")
            per_page: Number of items per page (default: 100)

        Returns:
            list[Section]: All sections
        """
        sections = []
        page = 1
        logger.debug("Fetching all sections for category_id: %s.", category_id)

        while True:
            response = await self.get_sections(
                category_id=category_id,
                sort_by=sort_by,
                sort_order=sort_order,
                per_page=per_page,
                page=page,
            )
            sections.extend(response.sections)
            logger.debug("Fetched page %d of sections for category_id %s. Next page: %s", page, category_id, response.next_page)

            if response.next_page is None:
                logger.debug("No more section pages to fetch for category_id: %s.", category_id)
                break
            page += 1

        logger.debug("Finished fetching all sections for category_id: %s. Total sections: %d", category_id, len(sections))
        return sections

    async def get_article_by_id(self, article_id: int) -> Article:
        """Get a specific article by its ID.

        Args:
            article_id: The ID of the article to retrieve

        Returns:
            Article: The article object

        Raises:
            httpx.HTTPStatusError: If the request fails
            ValidationError: If the response cannot be parsed
        """
        url = urljoin(self.BASE_URL, f"{self.locale}/articles/{article_id}.json")
        logger.debug("Request URL: %s", url)

        response = await self.session.get(url)
        logger.debug("Response status code: %s", response.status_code)
        response.raise_for_status()
        logger.debug("Successfully fetched article with ID: %s.", article_id)

        data = response.json()
        return Article.model_validate(data)

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
        logger.debug("Attempting to get articles for section_id: %s with params: %s", section_id, params)

        url = urljoin(self.BASE_URL, f"{self.locale}/sections/{section_id}/articles.json")
        logger.debug("Request URL: %s", url)

        response = await self.session.get(url, params=params)
        logger.debug("Response status code: %s", response.status_code)
        response.raise_for_status()
        logger.debug("Successfully fetched articles for section_id: %s.", section_id)

        data = response.json()
        return ArticlesResponse.model_validate(data)

    async def get_all_articles(
        self,
        section_id: int,
        sort_by: str = "position",
        sort_order: str = "asc",
        per_page: int = 100,
    ) -> list[Article]:
        """Get all articles for a specific section across all pages.

        Args:
            section_id: The ID of the section to get articles for
            sort_by: Field to sort by (default: "position")
            sort_order: Sort order "asc" or "desc" (default: "asc")
            per_page: Number of items per page (default: 100)

        Returns:
            list[Article]: All articles
        """
        articles = []
        page = 1
        logger.debug("Fetching all articles for section_id: %s.", section_id)

        while True:
            response = await self.get_articles(
                section_id=section_id,
                sort_by=sort_by,
                sort_order=sort_order,
                per_page=per_page,
                page=page,
            )
            articles.extend(response.articles)
            logger.debug("Fetched page %d of articles for section_id %s. Next page: %s", page, section_id, response.next_page)

            if response.next_page is None:
                logger.debug("No more article pages to fetch for section_id: %s.", section_id)
                break
            page += 1

        logger.debug("Finished fetching all articles for section_id: %s. Total articles: %d", section_id, len(articles))
        return articles
