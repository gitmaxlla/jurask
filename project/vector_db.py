import json
from pymilvus import MilvusClient
from pymilvus import model
from sentence_transformers import SentenceTransformer


class SearchQuery:
    def __init__(self, user_input, picked_section):
        self.user_input = user_input
        self.picked_section = picked_section


class Dataframe:
    def __init__(self, name, embedding_function):
        self.name = name
        self.embed = embedding_function
        with open(f"data/{name}.json") as f: self.data = json.load(f)

    def get_index(self):
            return "\n".join(self.data.keys())

    def get_chunks(self):
        result = []

        for chapter in self.data.keys():                
            for article in self.data[chapter].keys():
                paragraphs = self.data[chapter][article]
                result.append({
                    "chapter": chapter,
                    "article": article,
                    "text": " ".join(paragraphs),
                })

        return result


    def build_embedding_table(self):
        chunks = self.get_chunks()
        vectors = self.embed([chunk["text"] for chunk in chunks])

        result = []
        id_counter = 0

        for chunk in chunks:
            result.append({
                "id": id_counter,
                "law": self.name,
                "chapter": chunk["chapter"],
                "article": chunk["article"],
                "text": chunk["text"],
                "vector": vectors[id_counter],
            })
            id_counter += 1
                   
        return result
    

model = SentenceTransformer("intfloat/multilingual-e5-large-instruct")
constitution = Dataframe("constitution", model.encode)
client = MilvusClient(f"data/constitution.db")


def search_database(client: MilvusClient, dataframe: Dataframe, query: SearchQuery):
    if not client.has_collection(collection_name="main"): 
        raise KeyError
    
    query_vector = dataframe.embed([query.user_input])

    result = client.search(
        collection_name="main",
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
    vector_table = dataframe.build_embedding_table()

    client = MilvusClient(f"data/{dataframe.name}.db")

    if client.has_collection(collection_name="main"):
         client.drop_collection(collection_name="main")
    
    client.create_collection(
        collection_name="main",
        dimension=1024
    )

    return client.insert(collection_name="main", data=vector_table)
    

if __name__ == "__main__":
    print(build_database(constitution))
