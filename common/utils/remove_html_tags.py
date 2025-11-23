from bs4 import BeautifulSoup


def remove_html_tags(description: str) -> str:
    """Remove HTML tags from text using BeautifulSoup

    Args:
        description: HTML text to clean

    Returns:
        Cleaned text without HTML tags
    """
    soup = BeautifulSoup(description, "html.parser")
    text = soup.get_text(separator=" ")
    return text
