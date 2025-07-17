import asyncio
from typing import TypeVar

from markdownify import markdownify as md

from scraper.optiapi.client import OptiSignsClient

from .optiapi.models import Article

T = TypeVar("T")

# TODO: custom markdown conversion strategy for articles
class OptiSignsScraper:
    _client: OptiSignsClient

    def __init__(self):
        self._client = OptiSignsClient()

    def _convert_body_to_markdown(self, articles: list[Article]):
        for article in articles:
            if article.body:
                article.body = md(article.body)

    def _flatten(self, nested_list: list[list[T]]) -> list[T]:
        return [item for sublist in nested_list for item in sublist]

    async def get_articles(self) -> list[Article]:
        categories = await self._client.get_all_categories()

        sections = self._flatten(
            await asyncio.gather(
                *[
                    self._client.get_all_sections(category_id=category.id)
                    for category in categories
                ]
            )
        )
        articles = self._flatten(
            await asyncio.gather(
                *[
                    self._client.get_all_articles(section_id=section.id)
                    for section in sections
                ]
            )
        )

        self._convert_body_to_markdown(articles)

        return articles
