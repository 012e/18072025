"""Comprehensive tests for OptiSignsScraper class."""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from scraper.optiapi.client import OptiSignsClient
from scraper.optiapi.models import Article, Category, Section
from scraper.scraper import OptiSignsScraper


class TestOptiSignsScraper:
    """Test suite for OptiSignsScraper class."""

    def _is_likely_markdown(self, text: str | None) -> bool:
        """A simple heuristic to check if text is likely markdown."""
        if text is None or text == "":
            return True  # None or empty body is considered valid.

        # Check for the absence of common HTML tags from the source data.
        html_tags = ["<h1>", "<h2>", "<p>", "<strong>", "<em>", "<div>", "<ul>", "<li>"]
        if any(tag in text for tag in html_tags):
            return False

        # Check for the presence of common markdown syntax.
        markdown_syntax_chars = ["#", "*", "_", "`", "[", ">", "-"]
        if any(char in text for char in markdown_syntax_chars):
            return True

        # If no specific markdown syntax is found, it might just be plain text.
        # A good indicator is the absence of any angle brackets from tags.
        return "<" not in text and ">" not in text

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing."""
        return OptiSignsScraper()

    @pytest.fixture
    def mock_categories(self):
        """Mock category data."""
        return [
            Category(
                id=1,
                url="https://example.com/api/categories/1",
                html_url="https://example.com/categories/1",
                position=1,
                created_at=datetime(2023, 1, 1),
                updated_at=datetime(2023, 1, 1),
                name="Category 1",
                description="Test category 1",
                locale="en-us",
                source_locale="en-us",
                outdated=False,
            ),
            Category(
                id=2,
                url="https://example.com/api/categories/2",
                html_url="https://example.com/categories/2",
                position=2,
                created_at=datetime(2023, 1, 2),
                updated_at=datetime(2023, 1, 2),
                name="Category 2",
                description="Test category 2",
                locale="en-us",
                source_locale="en-us",
                outdated=False,
            ),
        ]

    @pytest.fixture
    def mock_sections(self):
        """Mock section data."""
        return [
            Section(
                id=1,
                url="https://example.com/api/sections/1",
                html_url="https://example.com/sections/1",
                category_id=1,
                position=1,
                sorting="manual",
                created_at=datetime(2023, 1, 1),
                updated_at=datetime(2023, 1, 1),
                name="Section 1",
                description="Test section 1",
                locale="en-us",
                source_locale="en-us",
                outdated=False,
                parent_section_id=None,
                theme_template="default",
            ),
            Section(
                id=2,
                url="https://example.com/api/sections/2",
                html_url="https://example.com/sections/2",
                category_id=1,
                position=2,
                sorting="manual",
                created_at=datetime(2023, 1, 2),
                updated_at=datetime(2023, 1, 2),
                name="Section 2",
                description="Test section 2",
                locale="en-us",
                source_locale="en-us",
                outdated=False,
                parent_section_id=None,
                theme_template="default",
            ),
            Section(
                id=3,
                url="https://example.com/api/sections/3",
                html_url="https://example.com/sections/3",
                category_id=2,
                position=1,
                sorting="manual",
                created_at=datetime(2023, 1, 3),
                updated_at=datetime(2023, 1, 3),
                name="Section 3",
                description="Test section 3",
                locale="en-us",
                source_locale="en-us",
                outdated=False,
                parent_section_id=None,
                theme_template="default",
            ),
        ]

    @pytest.fixture
    def mock_articles(self):
        """Mock article data with HTML content."""
        return [
            Article(
                id=1,
                url="https://example.com/api/articles/1",
                html_url="https://example.com/articles/1",
                author_id=1,
                comments_disabled=False,
                draft=False,
                promoted=False,
                position=1,
                vote_sum=5,
                vote_count=10,
                section_id=1,
                created_at=datetime(2023, 1, 1),
                updated_at=datetime(2023, 1, 1),
                name="article-1",
                title="Article 1",
                source_locale="en-us",
                locale="en-us",
                outdated=False,
                outdated_locales=[],
                edited_at=datetime(2023, 1, 1),
                user_segment_id=None,
                permission_group_id=1,
                content_tag_ids=[],
                label_names=[],
                body="<h1>Test Article</h1><p>This is a <strong>test</strong> article with <em>HTML</em> content.</p>",
            ),
            Article(
                id=2,
                url="https://example.com/api/articles/2",
                html_url="https://example.com/articles/2",
                author_id=1,
                comments_disabled=False,
                draft=False,
                promoted=True,
                position=2,
                vote_sum=10,
                vote_count=15,
                section_id=2,
                created_at=datetime(2023, 1, 2),
                updated_at=datetime(2023, 1, 2),
                name="article-2",
                title="Article 2",
                source_locale="en-us",
                locale="en-us",
                outdated=False,
                outdated_locales=[],
                edited_at=datetime(2023, 1, 2),
                user_segment_id=None,
                permission_group_id=1,
                content_tag_ids=["yebro", "somerandomstASDFASDF"],
                label_names=["important"],
                body="<div><h2>Another Test</h2><ul><li>Item 1</li><li>Item 2</li></ul></div>",
            ),
            Article(
                id=3,
                url="https://example.com/api/articles/3",
                html_url="https://example.com/articles/3",
                author_id=2,
                comments_disabled=True,
                draft=False,
                promoted=False,
                position=1,
                vote_sum=0,
                vote_count=0,
                section_id=3,
                created_at=datetime(2023, 1, 3),
                updated_at=datetime(2023, 1, 3),
                name="article-3",
                title="Article 3",
                source_locale="en-us",
                locale="en-us",
                outdated=False,
                outdated_locales=[],
                edited_at=datetime(2023, 1, 3),
                user_segment_id=None,
                permission_group_id=1,
                content_tag_ids=[],
                label_names=[],
                body="",  # Empty body to test None/empty handling
            ),
        ]

    def test_init(self, scraper):
        """Test scraper initialization."""
        assert isinstance(scraper._client, OptiSignsClient)
        assert scraper._client.locale == "en-us"
        assert scraper._client.timeout == 30

    def test_flatten_method(self, scraper):
        """Test the _flatten method with various input types."""
        nested_list = [[1, 2], [3, 4], [5]]
        assert scraper._flatten(nested_list) == [1, 2, 3, 4, 5]

        empty_nested = [[], [], []]
        assert scraper._flatten(empty_nested) == []

        mixed_nested = [["a", "b"], ["c"], ["d", "e", "f"]]
        assert scraper._flatten(mixed_nested) == ["a", "b", "c", "d", "e", "f"]

        assert scraper._flatten([]) == []

    def test_convert_body_to_markdown(self, scraper, mock_articles):
        """Test HTML to Markdown conversion."""
        articles = [Article(**article.model_dump()) for article in mock_articles]
        scraper._convert_body_to_markdown(articles)

        # Check first article conversion using the heuristic
        assert self._is_likely_markdown(articles[0].body)
        assert "Test Article" in articles[0].body
        assert "test" in articles[0].body

        # Check second article conversion
        assert self._is_likely_markdown(articles[1].body)
        assert "Another Test" in articles[1].body
        assert "Item 1" in articles[1].body

        # Check third article (empty body)
        assert articles[2].body == ""
        assert self._is_likely_markdown(articles[2].body)

    def test_convert_body_to_markdown_complex_html(self, scraper):
        """Test conversion with complex HTML structures."""
        complex_article = Article(
            id=100,
            url="https://example.com/api/articles/100",
            html_url="https://example.com/articles/100",
            author_id=1,
            comments_disabled=False,
            draft=False,
            promoted=False,
            position=1,
            vote_sum=0,
            vote_count=0,
            section_id=1,
            created_at=datetime(2023, 1, 1),
            updated_at=datetime(2023, 1, 1),
            name="complex-article",
            title="Complex Article",
            source_locale="en-us",
            locale="en-us",
            outdated=False,
            outdated_locales=[],
            edited_at=datetime(2023, 1, 1),
            user_segment_id=None,
            permission_group_id=1,
            content_tag_ids=[],
            label_names=[],
            body="""
            <div>
                <h1>Main Title</h1>
                <p>Paragraph with <a href="https://example.com">link</a></p>
                <blockquote>This is a quote</blockquote>
                <pre><code>code block</code></pre>
            </div>
            """,
        )

        scraper._convert_body_to_markdown([complex_article])

        assert self._is_likely_markdown(complex_article.body)
        assert "Main Title" in complex_article.body
        assert "[link](https://example.com)" in complex_article.body
        assert "code block" in complex_article.body

    @patch("scraper.scraper.OptiSignsClient")
    async def test_get_articles_success(
        self, mock_client_class, scraper, mock_categories, mock_sections, mock_articles
    ):
        """Test successful article retrieval."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        scraper._client = mock_client

        mock_client.get_all_categories.return_value = mock_categories
        mock_client.get_all_sections.side_effect = [
            [mock_sections[0], mock_sections[1]],
            [mock_sections[2]],
        ]
        mock_client.get_all_articles.side_effect = [
            [mock_articles[0]],
            [mock_articles[1]],
            [mock_articles[2]],
        ]

        result = await scraper.get_articles()

        assert len(result) == 3
        assert all(isinstance(article, Article) for article in result)
        mock_client.get_all_categories.assert_called_once()
        assert mock_client.get_all_sections.call_count == 2
        assert mock_client.get_all_articles.call_count == 3

        # Check that HTML was converted to markdown
        assert all(self._is_likely_markdown(article.body) for article in result)
        assert "Test Article" in result[0].body
        assert "Another Test" in result[1].body

    @patch("scraper.scraper.OptiSignsClient")
    async def test_get_articles_empty_categories(self, mock_client_class, scraper):
        """Test handling of empty categories."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        scraper._client = mock_client

        mock_client.get_all_categories.return_value = []

        result = await scraper.get_articles()

        assert result == []
        mock_client.get_all_categories.assert_called_once()
        mock_client.get_all_sections.assert_not_called()
        mock_client.get_all_articles.assert_not_called()

    @patch("scraper.scraper.OptiSignsClient")
    async def test_get_articles_empty_sections(
        self, mock_client_class, scraper, mock_categories
    ):
        """Test handling of empty sections."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        scraper._client = mock_client

        mock_client.get_all_categories.return_value = mock_categories
        mock_client.get_all_sections.return_value = []

        result = await scraper.get_articles()

        assert result == []
        mock_client.get_all_categories.assert_called_once()
        assert mock_client.get_all_sections.call_count == 2
        mock_client.get_all_articles.assert_not_called()

    @patch("scraper.scraper.OptiSignsClient")
    async def test_get_articles_partial_failure(
        self, mock_client_class, scraper, mock_categories
    ):
        """Test handling of partial failures in concurrent operations."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        scraper._client = mock_client

        mock_client.get_all_categories.return_value = mock_categories
        mock_client.get_all_sections.side_effect = [
            Exception("Section fetch failed"),
            [],  # Provide a return value for the other call
        ]

        with pytest.raises(Exception, match="Section fetch failed"):
            await scraper.get_articles()

    @patch("scraper.scraper.OptiSignsClient")
    async def test_get_articles_large_dataset(self, mock_client_class, scraper):
        """Test handling of large datasets."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        scraper._client = mock_client

        # Create large mock datasets
        large_categories = [
            Category(
                id=i,
                name=f"Category {i}",
                html_url="",
                url="",
                position=i,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                description="",
                locale="",
                source_locale="",
                outdated=False,
            )
            for i in range(10)
        ]
        large_sections = [
            Section(
                id=i,
                name=f"Section {i}",
                category_id=i % 10,
                html_url="",
                url="",
                position=i,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                description="",
                locale="",
                source_locale="",
                outdated=False,
                parent_section_id=None,
                theme_template="",
                sorting="",
            )
            for i in range(50)
        ]
        large_articles = [
            Article(
                id=i,
                name=f"article-{i}",
                title=f"Article {i}",
                section_id=i % 50,
                body=f"<h1>Article {i}</h1><p>Content for article {i}</p>",
                author_id=1,
                comments_disabled=False,
                draft=False,
                promoted=False,
                position=i,
                vote_sum=0,
                vote_count=0,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                html_url="",
                url="",
                source_locale="",
                locale="",
                outdated=False,
                outdated_locales=[],
                edited_at=datetime.now(),
                user_segment_id=None,
                permission_group_id=1,
                content_tag_ids=[],
                label_names=[],
            )
            for i in range(200)
        ]

        mock_client.get_all_categories.return_value = large_categories
        mock_client.get_all_sections.side_effect = lambda category_id: [
            s for s in large_sections if s.category_id == category_id
        ]
        mock_client.get_all_articles.side_effect = lambda section_id: [
            a for a in large_articles if a.section_id == section_id
        ]

        result = await scraper.get_articles()

        assert len(result) == 200
        assert all(isinstance(article, Article) for article in result)

        # Verify all articles were processed for markdown conversion
        for article in result:
            assert self._is_likely_markdown(article.body)
            assert f"Article {article.id}" in article.body

    @patch("scraper.scraper.OptiSignsClient")
    async def test_get_articles_memory_efficiency(
        self, mock_client_class, scraper, mock_articles, mock_categories, mock_sections
    ):
        """Test memory efficiency by ensuring objects are properly handled."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        scraper._client = mock_client

        mock_client.get_all_categories.return_value = mock_categories
        mock_client.get_all_sections.side_effect = [
            [mock_sections[0], mock_sections[1]],
            [mock_sections[2]],
        ]
        # Return copies to simulate fresh API responses
        mock_client.get_all_articles.side_effect = [
            [Article(**mock_articles[0].model_dump())],
            [Article(**mock_articles[1].model_dump())],
            [Article(**mock_articles[2].model_dump())],
        ]

        result = await scraper.get_articles()

        # Verify that the original mock_articles weren't modified
        assert "<h1>Test Article</h1>" in mock_articles[0].body
        assert not self._is_likely_markdown(mock_articles[0].body)

        # But the result should have markdown
        assert self._is_likely_markdown(result[0].body)
        assert "Test Article" in result[0].body
