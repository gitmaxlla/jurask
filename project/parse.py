import cloudscraper

from bs4 import BeautifulSoup as bs
from bs4.element import Tag
from typing import List

import json

LAW_INDEXES_URLS = [
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
    for url in LAW_INDEXES_URLS:
        response = scraper.get(url, headers=HEADERS, stream=True, allow_redirects=True)
        titles = get_titles_on_page(response.text)
        if response.url in LAW_INDEXES_URLS[:2]:
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

def get_text_of_article(url: str) -> str:
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, headers=HEADERS, stream=True, allow_redirects=True)
    parser = bs(response.text, "html.parser")
    text = parser.find("section", attrs={"class": "content"}).get_text(separator=' ', strip=True).strip()
    return text

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


def get_constitution_data() -> dict:
    scraper = cloudscraper.create_scraper()
    response = scraper.get(CONSTITUTION_URL, headers=HEADERS, stream=True, allow_redirects=True)
    parser = bs(response.text, "html.parser")
    content = parser.find_all("a")
    result = {}
    for link in content:
        if "Глава" in link.text:
            result[link.text] = __get_constitution_chunks(link.get('href'))


def __get_constitution_chunks(url: str) -> dict:
    base_url = url.rsplit("/", 3)[0]
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, headers=HEADERS, stream=True, allow_redirects=True)
    parser = bs(response.text, "html.parser")
    result = {}
    content = parser.find_all("li", {"class": "statya"})
    for link in content:
        result[link.find("a").text] = __get_chunks_from_article(base_url + "/" + link.find("a").get("href"))

    return result


def __get_chunks_from_article(url: str) -> str:
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, headers=HEADERS, stream=True, allow_redirects=True)
    parser = bs(response.text, "html.parser")
    parapraphs = parser.find("div", attrs={"class": "block"}).find_all("p", {"class": "s_1"})
    result = []
    for paragraph in parapraphs:
        text = paragraph.get_text()
        result.append(text)
    return result

if __name__ == "__main__":
    with open("/data/constitution.json", "w") as f:
        json.dump(get_constitution_data(), f, indent=2, ensure_ascii=False)

    # for article in get_articles_of_law('https://base.garant.ru/12125267/'):
    #     if article.text in to_find:
    #         print(get_text_of_article(article.url))
    #         print(article.url)
    #         # break

