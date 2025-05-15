import cloudscraper
import time
from multiprocessing import Pool

from bs4 import BeautifulSoup as bs
from typing import List
import os
import json
from tqdm import tqdm
from datetime import datetime, timezone

# TODO: Refactor, parallelized output, optimize
# TODO: \xa unicode escaping

SAVE_PATH = None
SCRAPER = cloudscraper.create_scraper()
HEADERS = {'User-Agent': 
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}


def get_slices(arr_len, parts=1):
    parts = min(arr_len, parts)
    step = arr_len // parts
    result = []

    for i in range(parts - 1):
        result.append((step*i, step*i + step))
        
    result.append((step*(parts - 1), arr_len))
    return result

class TextWithUrl:
    def __init__(self, text, url):
        self.text = text
        self.url = url


def get_timestamp_str():
    utc = datetime.fromtimestamp(time.time())
    return str(utc.astimezone(timezone.utc))

def get_text_of_article(url: str, scraper) -> str:
    response = scraper.get(url, headers=HEADERS, stream=True, allow_redirects=True)
    parser = bs(response.text, "html.parser")
    text = parser.find("section", attrs={"class": "content"}).get_text(separator=' ', strip=True).strip()
    return text

def get_chapters_of_law(url: str, scraper) -> List[TextWithUrl]:
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

def get_header_text(url: str, scraper):
    response = scraper.get(url, headers=HEADERS, stream=True, allow_redirects=True)
    parser = bs(response.text, "html.parser")
    result = parser.find("h1").get_text().strip()
    return result

def get_articles_of_law(url: str, scraper) -> List[TextWithUrl]:
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

def get_chunks_from_article(url: str, scraper) -> str:
    response = scraper.get(url, headers=HEADERS, stream=True, allow_redirects=True)
    parser = bs(response.text, "html.parser")
    parapraphs = parser.find("div", attrs={"class": "block"}).find_all("p", {"class": "s_1"})
    result = []
    for paragraph in parapraphs:
        text = paragraph.get_text()
        result.append(text)
    return result

def save_dataset(id, obj):
    with open(f"{SAVE_PATH}{id}.json", "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def build_dataset(id, main_url, description=""):
    build_start_timestamp = get_timestamp_str()

    result = {}
    result["metadata"] = {}
    result["content"] = {}

    law_name = get_header_text(main_url, SCRAPER)
    chapters = get_chapters_of_law(main_url, SCRAPER)

    for i, chapter in enumerate(chapters):
        print(f"{law_name} [{i+1} / {len(chapters)}]")

        chapter_name = get_header_text(chapter.url, SCRAPER)
        result["content"][chapter_name] = {}

        for article in tqdm(get_articles_of_law(chapter.url, SCRAPER)):
            article_name = get_header_text(article.url, SCRAPER)
            result["content"][chapter_name][article_name] = \
                get_chunks_from_article(article.url, SCRAPER)

    result["metadata"]["id"] = id
    result["metadata"]["name"] = law_name
    result["metadata"]["description"] = description
    result["metadata"]["build_start_datetime"] = \
        build_start_timestamp
    result["metadata"]["build_end_datetime"] = \
        get_timestamp_str()
    
    save_dataset(id, result)

def build_datasets(documents):
    print(f"(PID: {os.getpid()}) Staring build for {[document["id"] for document in documents]}")
    for document in documents:
        build_dataset(
            document["id"], 
            document["url"], 
            document["description"]
        )

def main(documents, paths):
    global SAVE_PATH
    SAVE_PATH = paths['parsed-data-path']
    MAX_THREADS = 1
    pool_size = min(len(documents), MAX_THREADS)
    with Pool(pool_size) as pool:
        pool.map(build_datasets, 
                 [documents[range_[0]:range_[1]] for range_ 
                  in get_slices(len(documents), pool_size)])
