from pydantic import BaseModel, Field
from typing import List, Optional


class AugmentedLawQuery(BaseModel):
    """Выбор юридического документа, сгенерированные ключевые слова и формальная версия вопроса на основе запроса пользователя, для последующего поиска в базе данных."""

    choice: str = Field(description="Название раздела из переданного их списка.")
    keywords: List[str] = Field(description="Ключевые слова, на основе которых можно было бы найти юридические документы, в которых содержится ответ на вопрос пользователя.")
    question: str = Field(description="Запрос пользователя, переписанный в нейтрально-деловом, юридическом, официальном стиле.")


class AnswerQuery(BaseModel):
    """Рассмотрение предоставленных юридических документов и продуманный ответ на запрос пользователя."""
    answer: str = Field("Продуманный ответ пользователю.")
    articles: List[str] = Field(description="Выбранные и использованные для ответа пользователю статьи из данных")


class UserQuestion(BaseModel):
    contents: str


class GeneratedResponse(BaseModel):
    answer: str
    articles: List[Optional[str]]


class SearchQuery:
    def __init__(self, user_input, picked_section):
        self.user_input = user_input
        self.picked_section = picked_section
