import asyncio

from scraper.optiapi.client import OptiSignsClient


async def main():
    print(await OptiSignsClient().get_categories())


if __name__ == "__main__":
    asyncio.run(main())
