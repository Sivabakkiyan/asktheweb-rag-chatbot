import requests
from urllib.parse import urlparse
from scraper.parser import WebsiteParser
from scraper.filters import LinkFilter


class WebsiteCrawler:
    """
    Handles downloading webpages and recursively crawling linked pages.
    """

    def __init__(self, timeout=10, max_pages=15):
        self.timeout = timeout
        self.max_pages = max_pages
        self.visited = set()

    def fetch_page(self, url):
        """
        Download HTML content from a webpage.
        """
        # Fake browser headers so websites don't block us
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0"
        }
        response = requests.get(url, timeout=self.timeout, headers=headers)
        response.raise_for_status()
        return response.text

    def crawl(self, start_url, depth=2):
        """
        Recursively crawl pages starting from start_url.
        Returns list of all crawled pages.
        """
        # Reset visited pages for each new crawl
        self.visited = set()
        all_pages = []

        # Start recursive crawling
        self._crawl_recursive(start_url, depth, all_pages)

        return all_pages

    def _crawl_recursive(self, url, depth, all_pages):
        """
        Internal recursive function to crawl pages.
        """
        # Stop if we already visited this page
        if url in self.visited:
            return

        # Stop if we reached max pages limit
        if len(all_pages) >= self.max_pages:
            return

        # Stop if we reached max depth
        if depth < 0:
            return

        # Mark this page as visited
        self.visited.add(url)

        try:
            print(f"Scraping page {len(all_pages) + 1}: {url}")

            # Download and parse page
            html = self.fetch_page(url)
            parser = WebsiteParser()
            page = parser.parse(html, url)

            # Get base domain to stay on same website
            base_domain = urlparse(url).netloc

            # Filter links
            link_filter = LinkFilter()
            valid_links = []

            for link in page["links"]:
                if link_filter.is_valid_link(link, base_domain):
                    valid_links.append(link)

            page["links"] = valid_links

            # Add page to results
            all_pages.append(page)

            # Follow links recursively
            for link in valid_links:
                if len(all_pages) >= self.max_pages:
                    break
                self._crawl_recursive(link, depth - 1, all_pages)

        except Exception as e:
            print(f"Could not scrape {url}: {e}")