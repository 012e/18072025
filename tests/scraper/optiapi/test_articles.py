from scraper.optiapi.client import OptiSignsClient


async def test_articles():
    """Test the articles API functionality."""
    async with OptiSignsClient() as client:
        # Using the section ID from the URL you provided
        section_id = 26324076807315
        
        print(f"Testing get_articles for section {section_id}...")
        articles_response = await client.get_articles(
            section_id=section_id,
            sort_by="position",
            sort_order="desc",
            per_page=100
        )
        
        print(f"Got {len(articles_response.articles)} articles")
        print(f"Page info: {articles_response.page}/{articles_response.page_count}")
        print(f"Total count: {articles_response.count}")
        
        if articles_response.articles:
            first_article = articles_response.articles[0]
            print(f"First article: {first_article.title} (ID: {first_article.id})")
            print(f"Position: {first_article.position}")
            print(f"Section ID: {first_article.section_id}")
            print(f"Vote sum: {first_article.vote_sum}")
            print(f"Vote count: {first_article.vote_count}")
            print(f"URL: {first_article.html_url}")
        
        print("\nTesting get_all_articles...")
        all_articles = await client.get_all_articles(
            section_id=section_id,
            sort_by="position",
            sort_order="desc"
        )
        
        print(f"Got {len(all_articles)} articles")

        # Test with ascending order
        print("\nTesting get_articles with ascending order...")
        articles_asc = await client.get_articles(
            section_id=section_id,
            sort_by="position",
            sort_order="asc",
            per_page=5
        )
        
        if articles_asc.articles:
            print(f"First article (asc): {articles_asc.articles[0].title} (Position: {articles_asc.articles[0].position})")
