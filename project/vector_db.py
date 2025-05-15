import json
from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
from .prompts import VECTOR_SEARCH_TASK


load_dotenv()


DATABASE_PATH = None
INDEX_PATH = None
PARSED_PATH = None

model = SentenceTransformer("intfloat/multilingual-e5-large-instruct")
client = None

if "MILVUS_URI" not in os.environ:
    client = MilvusClient("../data/vector/main.db")
else:
    client = MilvusClient(uri=os.environ["MILVUS_URI"],
                            token=os.environ["MILVUS_TOKEN"])

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
            if limit == len_in_words: break
        
        return result

    def granularize(self, arr):
        for str in arr:
            if self.too_big(str):
                location = arr.index(str)
                replace_with = self.break_apart(str)
                arr = arr[:location] + replace_with + arr[location+1:]

        return arr

    def assemble_granular(self, arr):
        chunks = []
        buffer = []
        word_counter = 0

        for i in range(len(arr)):
            next_word_len = self.word_len(arr[i])

            prospective_len = word_counter + next_word_len

            if prospective_len > self.words_per_chunk:
                self.__push_chunk(chunks, buffer)
                buffer = []
                word_counter = 0

            buffer.append(arr[i])
            word_counter += next_word_len

        remainder = buffer
        self.__push_chunk(chunks, remainder)
        return chunks


class Dataframe:
    def __init__(self, filename):
        self.data = None

        with open(f"{PARSED_PATH}{filename}.json") as f: 
            self.data = json.load(f)

        metadata = self.data["metadata"]

        self.id = metadata["id"]
        self.name = metadata["name"]

        print(f"-> {self.name}\n")

        self.data = self.data["content"]
        index_entry = list(self.data.keys())

        with open(f"{INDEX_PATH}index.json") as f:
            current_index = json.load(f)

        current_index["content"][self.name] = \
            index_entry

        current_index["map"][self.name] = \
            self.id

        with open(f"{INDEX_PATH}index.json", "w") as f: 
            json.dump(current_index, f, indent=2, ensure_ascii=False)

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
                chunks = chunker.assemble_granular(
                    chunker.granularize(paragraphs)
                )

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

        vectors = embed_fn(sentences=[chunk["text"] for chunk in chunks],
                           show_progress_bar=True)

        result = []
        id_counter = 0

        for chunk in chunks:
            result.append({
                "id": id_counter,
                "law_name": self.name,
                "chapter": chunk["chapter"],
                "article": chunk["article"],
                "text": chunk["text"],
                "vector": vectors[id_counter],
            })
            id_counter += 1
                   
        return result

def search_database(client: MilvusClient, dataset_id: str, query: str, limit=2, embed_fn=model.encode):
    collection = dataset_id
    if not client.has_collection(collection_name=collection): 
        raise KeyError
    
    query_vector = embed_fn([
        f'Instruct: {VECTOR_SEARCH_TASK}\nQuery: {query}'
    ])

    result = client.search(
        collection_name=collection,
        data=query_vector,
        output_fields=["law_name", "chapter", "article", "text", "id"],
        limit=limit
    )

    return result[0]

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

    print("Adding entries to the vector database...")
    return client.insert(collection_name=collection, 
                         data=vector_table)

def clean_index():
    with open(f"{INDEX_PATH}index.json", "w") as f:
        f.write('{"map":{}, "content":{}}')

def main(datasets, paths):
    global INDEX_PATH, PARSED_PATH, DATABASE_PATH
    clean_index()

    INDEX_PATH = paths["dataset-index-path"]
    PARSED_PATH = paths["parsed-data-path"]
    DATABASE_PATH = paths["database-path"]

    dataset_files = [item['id'] for item in datasets]

    for dataset_file in dataset_files:
        print(f'\nBuilding dataset (ID: {dataset_file})...')
        df = Dataframe(filename=dataset_file)
        build_database(df)
