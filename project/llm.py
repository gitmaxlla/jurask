from langchain.chat_models import init_chat_model
from .vector_db import client, search_database
from groq import APIStatusError
from .prompts import *
from dotenv import load_dotenv
from .data_models import *
from string import Template
import json
import pprint


load_dotenv()


AVAILABLE_MODELS = {
    "light": "llama-3.1-8b-instant",
    "heavy": "deepseek-r1-distill-llama-70b",
    "heavy1": "llama-3.3-70b-versatile"
}

def load_index():
    index = {}
    name_to_id = {}

    with open("data/augment/index.json") as f:
        index = json.load(f)
        name_to_id = index["map"]
        index = index["content"]

    index_str = "\n"

    for document in index.keys():
        index_str += f"Документ: '{name_to_id[document]}'\n"
        index_str += f"Охватываемые темы:\n"
        for chapter in index[document]:
            to_add = f"{".".join(chapter.split('.')[1:])}"
            to_add = to_add.split('(')[0] + "\n"
            index_str += to_add
        index_str += '\n'

    return index_str

index_str = load_index()

# Low temperature value is recommended for more precise tasks
search_llm = init_chat_model(
    AVAILABLE_MODELS["heavy"], model_provider="groq", temperature=0.0
    ).with_structured_output(SearchResponse)

answer_llm = init_chat_model(
    AVAILABLE_MODELS["heavy"], model_provider="groq", temperature=0.1
    ).with_structured_output(AnswerResponse)

judge_form_llm = init_chat_model(
    AVAILABLE_MODELS["heavy"], model_provider="groq", temperature=0.05
    ).with_structured_output(JudgeFormResponse)

judge_content_llm = init_chat_model(
    AVAILABLE_MODELS["heavy"], model_provider="groq", temperature=0.05
    ).with_structured_output(JudgeContentResponse)

search_template = Template(SEARCH_PROMPT)
answer_template = Template(ANSWER_PROMPT)

form_test_template = Template(LLM_JUDGE_TEST_PROMPT_FORM)
content_test_template = Template(LLM_JUDGE_TEST_PROMPT_CONTENT)

def answer(query, index_str):
    try:
        response = search_llm.invoke(
            search_template.substitute(
                query=query,
                index=index_str,
            )
        )

        if not response.question_is_relevant or not response.queries_to_make:
            return ("IRRELEVANT", None, query)

        MAX_QUERIES = 3
        if len(response.queries_to_make) > MAX_QUERIES:
            return ("TOO COMPLEX", None, query)

        sections = {}
        fragment_ids_used = set()
        id_to_data = {}

        for dataset_id, subquery in response.queries_to_make:
            search_result = search_database(client, 
                                  dataset_id, subquery)

            for result in search_result:
                result = result['entity']
                key = f'{result['law_name']} / {result['chapter']}'
                if key not in sections:
                    sections[key] = []

                if result['id'] not in fragment_ids_used:
                    sections[key].append((result['id'], result['text']))
                    id_to_data[result['id']] = {'law': result['law_name'],
                                           'chapter': result['chapter'],
                                           'article': result['article']}

        context = ""

        for section, fragments in sections.items():
            context += f"Раздел документа: '{section}'\n"

            for id, fragment in fragments:
                context += f"НОМЕР ФРАГМЕНТА: {id}\n" + \
                           f"{fragment}\n\n"

        response = answer_llm.invoke(
            answer_template.substitute(
                context=context,
                query=query
            )
        )

        references = {}

        for reference_id, fragment_id in response.used_references.items():
            references[reference_id] = id_to_data[fragment_id]

        response.used_references = references
        return ("OK", response, query)
    except Exception as err:
        print(err)
        return ("ERROR", None, query)

def judge(status, response, query):
    if status != "OK":
        return status

    score = 0
    max_score = (5 + 5) * 2

    try:
        f_response = judge_form_llm.invoke(
            form_test_template.substitute(
                query = query,
                answer = response.final_answer
            )
        )

        score += f_response.criteria1_score + f_response.criteria2_score + \
                 f_response.criteria3_score + f_response.criteria4_score + \
                 f_response.criteria5_score

        c_response = judge_content_llm.invoke(
            content_test_template.substitute(
                query=query,
                answer = response.final_answer,
                context = "098"
            )
        )

        score += c_response.criteria1_score + c_response.criteria2_score + \
                 c_response.criteria3_score + c_response.criteria4_score + \
                 c_response.criteria5_score

        return (score, max_score)
    except Exception as err:
        print(err)
        return -1


def main(datasets, paths):
    print("Jurask CLI loading...\n")

    while True:
        print('jurask ---^*> ', end="")
        question = input()
        
        if question == "exit":
            print("\nExiting...")
            break

        pprint.pprint(f"\n{answer(question, index_str)}\n")