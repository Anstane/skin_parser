from requests_html import AsyncHTMLSession

from core import get_environment_variables

env = get_environment_variables()


class HTMLRequester:
    def __init__(self):
        self.base_url = env.LIS_URL
        self.session = AsyncHTMLSession()

    async def fetch_page(self, endpoint: str) -> str:
        """Fetches and returns the HTML content of the page."""
        url = f"{self.base_url}{endpoint}/?sort_by=float_asc"

        try:
            response = await self.session.get(url)
            await response.html.arender()  # Use arender() for asynchronous rendering

            if response.status_code == 200:
                return response.html.html
            else:
                print(f"Failed to fetch page, status code: {response.status_code}")
                return None

        except Exception as e:
            print(f"Error fetching page: {str(e)}")
            return None
