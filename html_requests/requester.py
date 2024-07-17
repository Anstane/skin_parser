from core import get_environment_variables

env = get_environment_variables()


class HTMLRequester:
    def __init__(self):
        self.base_url = env.LIS_URL

    async def fetch_page(self, endpoint: str) -> str:
        """Fetches and returns the HTML content of the page."""
        url = f"{self.base_url}{endpoint}/?sort_by=float_asc"

        return url  # Заглушка.
