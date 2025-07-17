import asyncio
import logging as log

from scraper.scraper import OptiSignsScraper
from utils.path import slugify


async def main():
    scraper = OptiSignsScraper()
    articles = await scraper.get_articles()

    # write articles to file at ./tmp/[slug].md
    for article in articles:
        slug = slugify(article.name, allow_unicode=True)
        file_path = f"./tmp/{slug}.md"
        with open(file_path, "w+", encoding="utf-8") as file:
            file.write(article.body)
        log.info(f"Article '{article.name}' saved to {file_path}")


if __name__ == "__main__":
    asyncio.run(main())
