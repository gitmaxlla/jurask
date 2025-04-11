from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import json

from .data_models import AugmentedLawQuery, AnswerQuery, GeneratedResponse
from .vector_db import client, search_database, SearchQuery, format_search_result
from string import Template

from .vector_db import Dataframe
from groq import APIStatusError

load_dotenv()

# Low temperature value is recommended for more precise tasks
simpler_llm = init_chat_model("llama-3.1-8b-instant", model_provider="groq", temperature=0.1)
augmentation_llm = simpler_llm.with_structured_output(AugmentedLawQuery)

heavier_llm = init_chat_model("llama-3.3-70b-versatile", model_provider="groq")
answering_llm = heavier_llm.with_structured_output(AnswerQuery)

constitution = Dataframe(id="constitution",
                         name="Конституция РФ")
sections = constitution.get_index()

prompts = []
with open("data/config/prompts.json") as f:
    prompts = json.load(f)


complete_answer_template = Template(prompts["complete_answer"])

def answer(question):
    try:
        response = augmentation_llm.invoke("example " * 10000)
    except APIStatusError as err:
        info = err.response.json()['error']
        status_code = err.response.status_code

        if "too large" in info['message'] \
        and status_code == 413:
            reduce_token_len()

    response = augmentation_llm.invoke(f"Ты - юридический консультант по Конституции Российской Федерации. Пользователь задаёт ВОПРОС: '{question}'. Выбери подходящий документ для поиска ответа на вопрос пользователя из списка и приведи СЕМЬ ключевых слов, которые могли бы помочь отыскать нужную информацию в базе данных. Кроме того, перепиши запрос пользователя в официально-деловом стиле, как если бы его передавали системе юридических знаний для консультации. Переписанный запрос НЕ ДОЛЖЕН включать вступления наподобие 'Вот запрос:' и других. СПИСОК ДОСТУПНЫХ ДОКУМЕНТОВ:\n{sections}\nЕсли вопрос совсем НЕ СВЯЗАН с этими документами, оставь ВСЕ ПОЛЯ своего ответа ПУСТЫМИ.")
    if not response.keywords or not response.choice: return "null"

    lookup_query = ", ".join(response.keywords)[:-2] + ". " + response.question
    relevant_chunks = search_database(client, constitution, SearchQuery(user_input=lookup_query, picked_section=response.choice))
    llm_context = format_search_result(relevant_chunks)

    content_by_article = {}

    for entry in relevant_chunks:
        content_by_article[entry["entity"]["article"]] = entry["entity"]["text"]
    
    llm_response = answering_llm.invoke(complete_answer_template.substitute(llm_context=llm_context, user_question=response.question))
    references = {}

    for article in llm_response.articles:
        references[response.choice + ". " + article] = content_by_article[article]

    return {"answer": llm_response.answer, "articles": references}

def reduce_token_len():
    pass

if __name__ == "__main__":
    print("Jurask CLI loading...\n")

    while True:
        print('jurask ---^*> ', end="")
        question = input()
        
        if question == "exit":
            print("\nExiting...")
            break

        print(f"\n{answer(question)}\n")