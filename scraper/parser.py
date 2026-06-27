from bs4 import BeautifulSoup
from urllib.parse import urljoin


class WebsiteParser:
    """
    Parses HTML content and extracts structured webpage information.
    """

    def parse(self, html, base_url):
        """
        Parse HTML and return structured webpage data.
        """

        soup = BeautifulSoup(html, "html.parser")

        # Extract page title
        title = (
            soup.title.get_text(strip=True)
            if soup.title
            else "No Title Found"
        )

        # Extract clean text
        text = soup.get_text(separator=" ", strip=True)

        # Extract links
        links = []

        for tag in soup.find_all("a", href=True):
            full_url = urljoin(base_url, tag["href"])
            links.append(full_url)

        # Return structured page
        return {
            "url": base_url,
            "title": title,
            "text": text,
            "links": links
        }