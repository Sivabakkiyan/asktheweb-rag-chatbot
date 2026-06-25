from bs4 import BeautifulSoup
from urllib.parse import urljoin


class WebsiteParser:
    """
    Parses HTML content and extracts structured webpage information.
    """

    def parse(self, html, base_url):
        """
        Parse the HTML and return structured webpage data.
        """

        soup = BeautifulSoup(html, "html.parser")

        # -------------------------
        # Extract Page Title
        # -------------------------
        if soup.title:
            title = soup.title.get_text(strip=True)
        else:
            title = "No Title Found"

        # -------------------------
        # Extract Clean Text
        # -------------------------
        text = soup.get_text(separator=" ", strip=True)

        # -------------------------
        # Extract Links
        # -------------------------
        links = []

        for link in soup.find_all("a", href=True):
            full_url = urljoin(base_url, link["href"])
            links.append(full_url)

        # -------------------------
        # Return Structured Data
        # -------------------------
        return {
            "title": title,
            "text": text,
            "links": links
        }