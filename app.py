import asyncio

from html_requests.requester import HTMLRequester


async def main():
    html_requester = HTMLRequester()
    endpoint = "ak-47-vulcan-field-tested"  # Пример endpoint
    await html_requester.fetch_page(endpoint)


if __name__ == "__main__":
    asyncio.run(main())
