from bs4 import BeautifulSoup


def clean_html(description):
    soup = BeautifulSoup(description, "html.parser")
    text = soup.get_text(separator=" ")

    return text
