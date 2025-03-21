import grequests
import cloudscraper

from bs4 import BeautifulSoup as bs
from bs4.element import Tag
from typing import List
DOCUMENTS_URLS = [
        "https://www.garant.ru/doc/main/",
        "https://www.garant.ru/doc/law/",
        # "https://www.garant.ru/doc/forms/",
        # "https://www.garant.ru/doc/busref/"
    ]
CONSTITUTION_URL = "https://www.garant.ru/doc/constitution/"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}


class TextWithUrl:
    def __init__(self, text, url):
        self.text = text
        self.url = url


def get_titles_on_page(html_text: str) -> List[TextWithUrl]:
    parser = bs(html_text, "html.parser")
    content = parser.find("div", attrs={"class": "page-content"}).extract()
    titles = content.find_all("a")
    ret = list()
    for title in titles:
        if 'href' not in title.attrs:
            continue
        text_with_url = TextWithUrl(text=title.get_text().replace('\xa0', ' '), url=title['href'])
        ret.append(text_with_url)
    return ret


def get_titles_of_laws() -> List[TextWithUrl]:
    titles_with_urls = list()
    scraper = cloudscraper.create_scraper()
    for url in DOCUMENTS_URLS:
        response = scraper.get(url, headers=HEADERS, stream=True, allow_redirects=True)
        titles = get_titles_on_page(response.text)
        if response.url in DOCUMENTS_URLS[:2]:
            titles = titles[1:]
        titles_with_urls.extend(titles)
    return titles_with_urls

    # documents_requests = (grequests.get(url) for url in DOCUMENTS_URLS)
    # for response in grequests.map(documents_requests):  # grequests.imap
    #     titles = get_titles_on_page(response.text)
    #     if response.url in DOCUMENTS_URLS[:2]:
    #         titles = titles[1:]
    #     titles_on_page_text = [title.get_text().strip() for title in titles]
    #     titles_on_page_text = list(map(lambda x: x.replace('\xa0', ' '), titles_on_page_text))
    #     titles_texts.extend(titles_on_page_text)
    # return titles_texts


def get_articles_of_law(url: str) -> List[TextWithUrl]:
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, headers=HEADERS, stream=True, allow_redirects=True)
    parser = bs(response.text, "html.parser")
    content = parser.find("ul", attrs={"id": "ul_num1"}).extract()
    articles = content.find_all("a")
    ret = list()
    for article in articles:
        if 'href' not in article.attrs:
            continue
        text_with_url = TextWithUrl(text=article.get_text().replace('\xa0', ' '),
                                    url='https://base.garant.ru' + article['href'])
        ret.append(text_with_url)
    return ret


def get_text_of_article(url: str) -> str:
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, headers=HEADERS, stream=True, allow_redirects=True)
    parser = bs(response.text, "html.parser")
    text = parser.find("section", attrs={"class": "content"}).get_text(separator=' ', strip=True).strip()
    return text


if __name__ == "__main__":
    to_find = [
        'Статья 14.2. Незаконная продажа товаров (иных вещей), свободная реализация которых запрещена или ограничена',
        'Статья 14.15. Нарушение правил продажи отдельных видов товаров',
        'Статья 14.16. Нарушение правил продажи этилового спирта, алкогольной и спиртосодержащей продукции',
        'Статья 14.17. Нарушение требований к производству или обороту этилового спирта, алкогольной и спиртосодержащей продукции',
        'Статья 14.17.1. Незаконная розничная продажа алкогольной и спиртосодержащей пищевой продукции физическими лицами',
        'Статья 14.53. Несоблюдение ограничений и (или) нарушение запретов в сфере торговли табачными изделиями, табачной продукцией, никотинсодержащей продукцией и сырьем для их производства, кальянами, устройствами для потребления никотинсодержащей продукции',
        'Статья 14.67. Нарушение требований к производству или обороту табачных изделий, табачной продукции, никотинсодержащей продукции и (или) сырья для их производства'
    ]
    # get_titles_of_laws()
    for article in get_articles_of_law('https://base.garant.ru/12125267/'):
        if article.text in to_find:
            print(get_text_of_article(article.url))
            print(article.url)
            # break
