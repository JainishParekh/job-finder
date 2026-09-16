import asyncio

from .xing import scrape_xing


async def main():
    print("🚀 Starting job scraping pipeline...")

    await scrape_xing()

    print("🏁 Job scraping pipeline finished.")


if __name__ == "__main__":
    asyncio.run(main())