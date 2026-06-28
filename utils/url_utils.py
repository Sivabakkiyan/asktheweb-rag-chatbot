import re

def normalize_url(url: str) -> str:
    """
    Normalize and validate a user-provided URL.
    Raises ValueError for invalid URLs.
    """
    url = url.strip()

    # Check empty
    if not url:
        raise ValueError("Please enter a URL before clicking Load.")

    # Add https if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Check if URL has a valid domain
    pattern = r'https?://[a-zA-Z0-9]+([\-\.]{1}[a-zA-Z0-9]+)*\.[a-zA-Z]{2,}'
    if not re.match(pattern, url):
        raise ValueError(
            "Invalid URL! Please enter a valid URL like https://example.com"
        )

    return url