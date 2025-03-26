from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List
from .vector_db import constitution, client, search_database, SearchQuery, format_search_result
import json


class AugmentedLawQuery(BaseModel):
    """Выбор юридического документа, сгенерированные ключевые слова и формальная версия вопроса на основе запроса пользователя, для последующего поиска в базе данных."""

    choice: str = Field(description="Название раздела из переданного их списка.")
    keywords: List[str] = Field(description="Ключевые слова, на основе которых можно было бы найти юридические документы, в которых содержится ответ на вопрос пользователя.")
    question: str = Field(description="Запрос пользователя, переписанный в нейтрально-деловом, юридическом, официальном стиле.")


class AnswerQuery(BaseModel):
    """Рассмотрение предоставленных юридических документов и продуманный ответ на запрос пользователя."""
    answer: str = Field("Продуманный ответ пользователю.")
    articles: List[str] = Field(description="Выбранные и использованные для ответа пользователю статьи из данных")


load_dotenv()

simpler_llm = init_chat_model("llama-3.1-8b-instant", model_provider="groq")
augmentation_llm = simpler_llm.with_structured_output(AugmentedLawQuery)

heavier_llm = init_chat_model("llama-3.3-70b-versatile", model_provider="groq")
answering_llm = heavier_llm.with_structured_output(AnswerQuery)

sections = constitution.get_index()

prompts = []
with open("data/prompts.json") as f:
    prompts = json.load(f)


def answer(question):
    response = augmentation_llm.invoke(f"Ты - юридический консультант по Конституции Российской Федерации. Пользователь задаёт ВОПРОС: '{question}'. Выбери подходящий документ для поиска ответа на вопрос пользователя из списка и приведи СЕМЬ ключевых слов, которые могли бы помочь отыскать нужную информацию в базе данных. Кроме того, перепиши запрос пользователя в официально-деловом стиле, как если бы его передавали системе юридических знаний для консультации. Переписанный запрос НЕ ДОЛЖЕН включать вступления наподобие 'Вот запрос:' и других. СПИСОК ДОСТУПНЫХ ДОКУМЕНТОВ:\n{sections}\nЕсли вопрос совсем НЕ СВЯЗАН с этими документами, оставь ВСЕ ПОЛЯ своего ответа ПУСТЫМИ.")
    if not response.keywords or not response.choice: return "null"

    lookup_query = ", ".join(response.keywords)[:-2] + ". " + response.question
    relevant_chunks = format_search_result(search_database(client, constitution, SearchQuery(user_input=lookup_query, picked_section=response.choice)))
    
    complete_answer = answering_llm.invoke(f"Ты - профессиональный юридический консультант. Тебе задал вопрос один из клиентов, и ожидается, что ты НА ОСНОВЕ ПРЕДОСТАВЛЕННЫХ ЧАСТЕЙ ДОКУМЕНТОВ, ОСМЫСЛЕННО ответишь на его вопрос в официально-деловом стиле, с ссылками и, возможно, прямыми цитатами из ПРЕДЛАГАЕМЫХ документов.\n\nПРЕДЛАГАЕМЫЕ ЧАСТИ ДОКУМЕНТОВ:\n{relevant_chunks}\n\nВОПРОС ПОЛЬЗОВАТЕЛЯ: {response.question}. Помни, что ответ должен быть написан как профессиональная юридическая консультация, с ОПОРОЙ на предложенные фрагменты. ЕСЛИ ОТВЕТА В ЭТИХ ФРАГМЕНТАХ НЕТ, ОСТАВЬ ВСЕ ПОЛЯ ОТВЕТА ПУСТЫМИ.")

    return complete_answer


if __name__ == "__main__":
    while True:
        print('> ', end="")
        question = input()

        if question == "exit":
            break

        print(answer(question))