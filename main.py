import asyncio
import logging
import os
import sys

import logging_loki

from config.config import load_config
from scraper.scraper import OptiSignsScraper
from utils.path import slugify


async def main():
    config = load_config()

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # this library is blocking :(
    handler = logging_loki.LokiHandler(
        url=str(config.grafana_loki_url),
        version="2",
        auth=(config.grafana_loki_user, config.grafana_loki_password),
    )
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    scraper = OptiSignsScraper()
    articles = await scraper.get_articles()

    if not os.path.exists(config.scrape_output_path):
        os.makedirs(config.scrape_output_path)

    # write articles to file at ./tmp/[slug].md
    for article in articles:
        slug = slugify(article.name, allow_unicode=True)
        file_path = os.path.join(config.scrape_output_path, f"{slug}.md")
        with open(file_path, "w+", encoding="utf-8") as file:
            file.write(article.body)
        logger.info(f"Article '{article.name}' saved to {file_path}")


if __name__ == "__main__":
    asyncio.run(main())
