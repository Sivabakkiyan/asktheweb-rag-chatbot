from urllib.parse import urlparse


class LinkFilter:
    """
    Determines whether a URL should be crawled.
    """

    EXCLUDED_KEYWORDS = [
        "login", "logout", "register", "signup",
        "privacy", "terms", "policy",
        "facebook", "twitter", "linkedin",
        "instagram", "youtube",
        "mailto", "tel",
        "special:", "wikipedia:", "help:",
        "talk:", "portal:", "action=edit",
        "action=history", "index.php",
        "file:", "template:", "category:",
        "main_page", "disambiguation",
        "cite_note", "cite_ref"
    ]

    def is_valid_link(self, url: str, base_domain: str) -> bool:
        """
        Returns True if the URL is suitable for crawling.
        """
        if not url:
            return False

        url = url.strip()

        if url.startswith("javascript:"):
            return False

        if "#" in url:
            return False

        parsed = urlparse(url)

        if parsed.netloc and parsed.netloc != base_domain:
            return False

        lower_url = url.lower()

        for keyword in self.EXCLUDED_KEYWORDS:
            if keyword.lower() in lower_url:
                return False

        return True