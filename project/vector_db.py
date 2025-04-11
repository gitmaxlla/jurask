import json
from pymilvus import MilvusClient
from pymilvus import model
from sentence_transformers import SentenceTransformer
import os
from .data_models import SearchQuery
from tqdm import tqdm
from dotenv import load_dotenv
import itertools


load_dotenv()


class Chunker:
    '''
    Empirical testing on top 1000 most common Russian words has
    shown that the large-e5-instruct 1024 input tokens limit
    maps to around 400 Russian words.

    Typical sentence should be somewhere around 20 words long,
    but laws generally have longer sentences, so 60 words overlap
    is assumed.
    '''

    def __init__(self, words_per_chunk=350, overlap_in_words=60):
        self.words_per_chunk = words_per_chunk
        self.overlap_in_words = overlap_in_words
    
    def __push_chunk(self, arr, buffer):
        arr.append(" ".join(buffer))

    def word_len(self, str):
        return len(str.split(" "))
    
    def too_big(self, str):
        return self.word_len(str) > self.words_per_chunk
    
    def break_apart(self, str):
        len_in_words = self.word_len(str)
        step = self.words_per_chunk - self.overlap_in_words
        words = str.split(" ")
        
        result = []

        for i in range(0, len_in_words, step):
            limit = min(len_in_words, i + self.words_per_chunk)
            result.append(" ".join(words[i:limit]))
        
        return result

    def granularize(self, arr):
        for str in arr:
            if self.too_big(str):
                location = arr.index(str)
                arr[location:location + 1] = \
                self.break_apart(str)
        
        return arr

    def assemble_granular(self, arr):
        chunks = []
        buffer = []
        word_counter = 0

        for i in range(len(arr)):
            next_len = self.word_len(arr[i])
            prospective_len = word_counter + next_len
            if prospective_len > self.words_per_chunk:
                self.__push_chunk(chunks, buffer)
                buffer = []
                word_counter = 0
            else:
                buffer.append(arr[i])
                word_counter += next_len

            remainder = buffer
            self.__push_chunk(chunks, remainder)

        print(chunks)
        print("-------------------")
        return chunks


class Dataframe:
    def __init__(self, id, name, schema_mode=False):
        self.id = id
        self.name = name
        self.data = None

        if not schema_mode:
            with open(f"data/parsed/{self.id}.json") as f: 
                self.data = json.load(f)

    def is_schema(self):
        return self.data is None

    def get_index(self):
            return "\n".join(self.data.keys())

    def get_chunks(self):
        result = []

        for chapter in self.data.keys():                
            for article in self.data[chapter].keys():
                paragraphs = self.data[chapter][article]

                chunker = Chunker()
                chunker.granularize(paragraphs)
                chunks = chunker.assemble_granular(paragraphs)

                for chunk in chunks:
                    result.append({
                        "id": self.id,
                        "document": self.name,
                        "chapter": chapter,
                        "article": article,
                        "text": chunk,
                    })

        return result


    def build_embedding_table(self, embed_fn):
        chunks = self.get_chunks()
        print(chunks)
        return

        vectors = embed_fn(sentences=[chunk["text"] for chunk in chunks],
                           show_progress_bar=True)

        result = []
        id_counter = 0

        for chunk in tqdm(chunks, 
                          desc="Adding entries to the vector database"):
            result.append({
                "id": id_counter,
                "law_id": self.id,
                "law_name": self.name,
                "chapter": chunk["chapter"],
                "article": chunk["article"],
                "text": chunk["text"],
                "vector": vectors[id_counter],
            })
            id_counter += 1
                   
        return result
    

model = SentenceTransformer("intfloat/multilingual-e5-large-instruct")
client = MilvusClient("data/vector/main.db")
#client = MilvusClient(uri=os.environ["ZILLIZ_CLUSTER_ENDPOINT"],
#                      token=os.environ["ZILLIZ_CLUSTER_TOKEN"])


def search_database(client: MilvusClient, dataframe: Dataframe, query: SearchQuery, embed_fn=model.encode):
    collection = dataframe.id
    if not client.has_collection(collection_name=collection): 
        raise KeyError
    
    query_vector = embed_fn([query.user_input])

    result = client.search(
        collection_name=collection,
        data=query_vector,
        filter=f"chapter == '{query.picked_section}'",
        output_fields=["chapter", "article", "text"],
        limit=10
    )

    return result[0]

def format_search_result(search_result):
    result = ""

    for item in search_result:
        entry = item["entity"]
        result += f"{entry["chapter"]}\n{entry["article"]}\n{entry["text"]}\n\n"
    
    return result

def build_database(dataframe: Dataframe):
    vector_table = \
        dataframe.build_embedding_table(model.encode)
    collection = dataframe.id

    if client.has_collection(collection_name=collection):
         client.drop_collection(collection_name=collection)
    
    client.create_collection(
        collection_name=collection,
        dimension=1024
    )

    return client.insert(collection_name=collection, 
                         data=vector_table)


if __name__ == "__main__":
    DATASET_IDS = ["constitution", 
                   "consumer_rights"
                  ]

    for dataset_id in DATASET_IDS:
        print(f'Building ID: {id}...')
        df = Dataframe(id=id)
        build_database(df)
