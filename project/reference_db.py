import json
import os
import sqlite3


PARSED_PATH = None
connection = None

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


def search_database(path, table, name):
    connection = sqlite3.connect(f"{path}store.db")
    cursor = connection.cursor()
    res = cursor.execute(f"SELECT content FROM `{table}` WHERE name='{name}'")
    return res.fetchone()[0]

def build_database(dataframe: Dataframe):
    cursor = connection.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS `{dataframe.name}`")
    cursor.execute(f"CREATE TABLE `{dataframe.name}`(name, content)")
    for chapter_key in dataframe.data:
        for article_key in dataframe.data[chapter_key]:
            name = f"{chapter_key}. {article_key}"
            content = '\n'.join(dataframe.data[chapter_key][article_key])
            cursor.execute(f"INSERT INTO `{dataframe.name}` VALUES ('{name}', '{content}')")
    connection.commit()

def main(datasets, paths):
    global connection, PARSED_PATH
    connection = sqlite3.connect(f"{paths["database-path"]}store.db")
    PARSED_PATH = paths["parsed-data-path"]

    dataset_files = [item['id'] for item in datasets]

    for dataset_file in dataset_files:
        print(f'\nBuilding dataset (ID: {dataset_file})...')
        df = Dataframe(filename=dataset_file)
        build_database(df)

    connection.close()
