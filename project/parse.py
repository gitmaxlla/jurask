import cloudscraper
import time

from bs4 import BeautifulSoup as bs
from bs4.element import Tag
from typing import List

import json
from tqdm import tqdm
from datetime import datetime, timezone

# TODO: Refactor, parallelize
HEADERS = {'User-Agent': 
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
DOCUMENTS = [
    {
        "id": "constitution",
        "url": "https://www.garant.ru/doc/constitution/",
        "description": ""
    },

    {
        "id": "consumer_rights",
        "url": "https://base.garant.ru/10106035/",
        "description": "",  
    }
]


class TextWithUrl:
    def __init__(self, text, url):
        self.text = text
        self.url = url


class ParserInstance:
    pass

def parse_job(documents, max_threads=5):
    pass

def get_timestamp_str():
    utc = datetime.fromtimestamp(time.time())
    return str(utc.astimezone(timezone.utc))

def get_text_of_article(url: str) -> str:
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, headers=HEADERS, stream=True, allow_redirects=True)
    parser = bs(response.text, "html.parser")
    text = parser.find("section", attrs={"class": "content"}).get_text(separator=' ', strip=True).strip()
    return text

def get_chapters_of_law(url: str) -> List[TextWithUrl]:
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, headers=HEADERS, stream=True, allow_redirects=True)
    parser = bs(response.text, "html.parser")
    chapter_wrappers = parser.find_all(class_="glava")
    ret = list()

    for chapter_wrapper in chapter_wrappers:
        links = chapter_wrapper.find_all("a")
        for link in links:
            if "Глава" in link.get_text():
                ret.append(
                    TextWithUrl(
                        text=link.get_text().replace('\xa0', ' '),
                        url=
                            'https://base.garant.ru' + link['href']
                            if 'http' not in link['href'] 
                            else link['href']
                    )
                )

    return ret

def get_header_text(url: str):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, headers=HEADERS, stream=True, allow_redirects=True)
    parser = bs(response.text, "html.parser")
    result = parser.find("h1").get_text().strip()
    return result

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

def get_chunks_from_article(url: str) -> str:
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, headers=HEADERS, stream=True, allow_redirects=True)
    parser = bs(response.text, "html.parser")
    parapraphs = parser.find("div", attrs={"class": "block"}).find_all("p", {"class": "s_1"})
    result = []
    for paragraph in parapraphs:
        text = paragraph.get_text()
        result.append(text)
    return result

def save_dataset(id, obj):
    with open(f"data/parsed/{id}.json", "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def build_dataset(id, main_url, description=""):
    build_start_timestamp = get_timestamp_str()

    result = {}
    result["metadata"] = {}
    result["content"] = {}

    law_name = get_header_text(main_url)
    chapters = get_chapters_of_law(main_url)

    for i, chapter in enumerate(chapters):
        print(f"{law_name} [{i+1} / {len(chapters)}]")

        chapter_name = get_header_text(chapter.url)
        result["content"][chapter_name] = {}

        for article in tqdm(get_articles_of_law(chapter.url)):
            article_name = get_header_text(article.url)
            result["content"][chapter_name][article_name] = \
                get_chunks_from_article(article.url)

    result["metadata"]["id"] = id
    result["metadata"]["name"] = law_name
    result["metadata"]["description"] = description
    result["metadata"]["build_start_datetime"] = \
        build_start_timestamp
    result["metadata"]["build_end_datetime"] = \
        get_timestamp_str()
    
    save_dataset(id, result)


if __name__ == "__main__":
    for document in DOCUMENTS[:1]:
        build_dataset(
            document["id"], 
            document["url"], 
            document["description"]
        )

    # build_dataset("consumer_rights")

# def get_titles_of_laws() -> List[TextWithUrl]:
#     titles_with_urls = list()
#     scraper = cloudscraper.create_scraper()
#     for url in LAW_INDEXES_URLS:
#         response = scraper.get(url, headers=HEADERS, stream=True, allow_redirects=True)
#         titles = get_titles_on_page(response.text)
#         if response.url in LAW_INDEXES_URLS[:2]:
#             titles = titles[1:]
#         titles_with_urls.extend(titles)
#     return titles_with_urls

# def get_titles_on_page(html_text: str) -> List[TextWithUrl]:
#     parser = bs(html_text, "html.parser")
#     content = parser.find("div", attrs={"class": "page-content"}).extract()
#     titles = content.find_all("a")
#     ret = list()
#     for title in titles:
#         if 'href' not in title.attrs:
#             continue
#         text_with_url = TextWithUrl(text=title.get_text().replace('\xa0', ' '), url=title['href'])
#         ret.append(text_with_url)
#     return ret

    #with open("/data/constitution.json", "w") as f:
    #    json.dump(get_constitution_data(), f, indent=2, ensure_ascii=False)

    # result = {}
    # for chapter in get_chapters_of_law(DOCUMENT_LOCATIONS["constitution"]):
    #    print(chapter.text, chapter.url)
    #    result[chapter.text] = {}

    #    for article in get_articles_of_law(DOCUMENT_LOCATIONS["constitution"]):
    #        print(article.text, article.url)

# def get_constitution_data() -> dict:
#     scraper = cloudscraper.create_scraper()
#     response = scraper.get(DOCUMENT_LOCATIONS["constitution"],
#                            headers=HEADERS, stream=True, allow_redirects=True)
#     parser = bs(response.text, "html.parser")
#     content = parser.find_all("a")
#     result = {}
#     for link in content:
#         if "Глава" in link.text:
#             result[link.text] = __get_constitution_chunks(link.get('href'))

# def __get_constitution_chunks(url: str) -> dict:
#     base_url = url.rsplit("/", 3)[0]
#     scraper = cloudscraper.create_scraper()
#     response = scraper.get(url, headers=HEADERS, stream=True, allow_redirects=True)
#     parser = bs(response.text, "html.parser")
#     result = {}
#     content = parser.find_all("li", {"class": "statya"})
#     for link in content:
#         result[link.find("a").text] = get_chunks_from_article(base_url + "/" + link.find("a").get("href"))

#     return result