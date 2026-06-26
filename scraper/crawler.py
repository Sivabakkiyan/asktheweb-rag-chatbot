import requests
from urllib.parse import urlparse

from scraper.parser import WebsiteParser
from scraper.filters import LinkFilter


class WebsiteCrawler:
    """
    Handles downloading webpages and preparing structured page data.
    """

    def __init__(self, timeout=10):
        self.timeout = timeout

    def fetch_page(self, url):
        """
        Download HTML content from a webpage.
        """

        response = requests.get(url, timeout=self.timeout)

        response.raise_for_status()

        return response.text

    def crawl(self, url):
        """
        Crawl a single webpage and return structured page data.
        """

        # Download webpage
        html = self.fetch_page(url)

        # Parse webpage
        parser = WebsiteParser()

        page = parser.parse(html, url)

        # Get base domain
        base_domain = urlparse(url).netloc

        # Filter links
        link_filter = LinkFilter()

        valid_links = []

        for link in page["links"]:

            if link_filter.is_valid_link(link, base_domain):
                valid_links.append(link)

        # Keep only valid links
        page["links"] = valid_links

        return [page]