def normalize_url(url: str) -> str:
    """
    Normalize a user-provided URL.

    Examples:
        python.org              -> https://python.org
        www.python.org          -> https://www.python.org
        https://python.org      -> https://python.org
        http://python.org       -> http://python.org
    """

    url = url.strip()

    if not url:
        raise ValueError("URL cannot be empty.")

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url