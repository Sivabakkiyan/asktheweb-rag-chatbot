import requests
from urllib.parse import urlparse
from scraper.parser import WebsiteParser
from scraper.filters import LinkFilter


class WebsiteCrawler:
    """
    Handles downloading webpages and recursively crawling linked pages.
    Stays focused on relevant pages only.
    """

    def __init__(self, timeout=15, max_pages=10):
        self.timeout = timeout
        self.max_pages = max_pages
        self.visited = set()

    def fetch_page(self, url):
        """
        Download HTML content from a webpage.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0"
        }
        response = requests.get(url, timeout=self.timeout, headers=headers)
        response.raise_for_status()
        return response.text

    def crawl(self, start_url, depth=2, progress_callback=None):
        """
        Recursively crawl pages starting from start_url.
        Returns list of all crawled pages.
        """
        self.visited = set()
        all_pages = []
        self._crawl_recursive(start_url, depth, all_pages, progress_callback)
        return all_pages

    def _crawl_recursive(self, url, depth, all_pages, progress_callback=None):
        """
        Internal recursive function to crawl pages one by one.
        """
        # Stop conditions
        if url in self.visited:
            return
        if len(all_pages) >= self.max_pages:
            return
        if depth < 0:
            return

        self.visited.add(url)

        try:
            if progress_callback:
                progress_callback(f"Scraping page {len(all_pages) + 1}: {url}")
            else:
                print(f"Scraping page {len(all_pages) + 1}: {url}")

            html = self.fetch_page(url)
            parser = WebsiteParser()
            page = parser.parse(html, url)

            base_domain = urlparse(url).netloc
            link_filter = LinkFilter()

            valid_links = []
            for link in page["links"]:
                if link_filter.is_valid_link(link, base_domain):
                    valid_links.append(link)

            # Only keep first 5 links to stay focused
            page["links"] = valid_links[:10]
            all_pages.append(page)

            # Follow links one by one
            for link in page["links"]:
                if len(all_pages) >= self.max_pages:
                    break
                self._crawl_recursive(
                    link, depth - 1, all_pages, progress_callback
                )

        except Exception as e:
            print(f"Could not scrape {url}: {e}")