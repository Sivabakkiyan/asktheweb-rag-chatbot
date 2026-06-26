from urllib.parse import urlparse


class LinkFilter:
    """
    Determines whether a URL should be crawled.
    """

    EXCLUDED_KEYWORDS = {
        "login",
        "logout",
        "register",
        "signup",
        "privacy",
        "terms",
        "policy",
        "facebook",
        "twitter",
        "linkedin",
        "instagram",
        "youtube",
        "mailto",
        "tel"
    }

    def is_valid_link(self, url: str, base_domain: str) -> bool:
        """
        Returns True if the URL is suitable for crawling.
        """

        if not url:
            return False

        url = url.strip()

        # Ignore JavaScript links
        if url.startswith("javascript:"):
            return False

        # Ignore page fragments
        if "#" in url:
            return False

        parsed = urlparse(url)

        # Ignore external websites
        if parsed.netloc and parsed.netloc != base_domain:
            return False

        lower_url = url.lower()

        # Ignore unwanted pages
        for keyword in self.EXCLUDED_KEYWORDS:
            if keyword in lower_url:
                return False

        return True