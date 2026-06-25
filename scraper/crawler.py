import requests


class WebsiteCrawler:
    """
    Handles downloading webpage HTML content.
    """

    def __init__(self, timeout=10):
        self.timeout = timeout

    def fetch_page(self, url):
        """
        Fetch HTML content from the given URL.
        """

        response = requests.get(url, timeout=self.timeout)

        response.raise_for_status()

        return response.text