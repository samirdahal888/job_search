from bs4 import BeautifulSoup


def remove_html_tags(description):
    soup = BeautifulSoup(description, "html.parser")
    text = soup.get_text(separator=" ")

    return text
