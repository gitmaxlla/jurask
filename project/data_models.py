from pydantic import BaseModel, Field
from typing import List, Dict, Tuple


class SearchResponse(BaseModel):
    """Указание списка документов, к которым нужно обратиться для ответа пользователю, 
    и вопросы к базе данных этих документов."""

    thinking_process: str = \
        Field(description="Тщательный пошаговый ход мыслей для подбора самых точных и подходящих документов и запросов к ним.")
    question_is_relevant: bool = \
        Field(description="Позволяют ли указанные документы ответить на запрос пользователя?")
    queries_to_make: List[Tuple[str, str]] = \
        Field(description="Список выбранных пар в виде списка кортежей: (Документ, Запрос).")

class AnswerResponse(BaseModel):
    """Ответ пользователю и словарь отсылок на предоставленные документы."""

    thinking_process: str = \
        Field(description="Развёрнутый ход рассуждения над вопросом пользователя, включая размышления о том, какие ссылки и куда поставить.")
    final_answer: str = \
        Field(description="Готовый ответ пользователю на основе размышлений и предоставленных документов.")
    used_references: Dict[int, int] = \
        Field(description="Соотвествия номера отсылки и номера использованного фрагмента.")
    
class JudgeFormResponse(BaseModel):
    """Оценка ответа юридического консультанта по заданным критериям."""

    criteria1_consideration: str = \
        Field(description="Рассуждение: Формат отсылок в ответе соответствует приведенному образцу?")
    criteria1_score: int = \
        Field(description="Оценка: Формат отсылок в ответе соответствует приведенному образцу (0-2).")
    
    criteria2_consideration: str = \
        Field(description="Рассуждение: Предложения не слишком длинные и нагруженные, лаконичные?")
    criteria2_score: int = \
        Field(description="Оценка: Предложения не слишком длинные и нагруженные, лаконичные (0-2).")
    
    criteria3_consideration: str = \
        Field(description="Рассуждение: Использован официально-деловой стиль?")
    criteria3_score: int = \
        Field(description="Оценка: Использован официально-деловой стиль (0-2).")
    
    criteria4_consideration: str = \
        Field(description="Рассуждение: Нет просторечий и неуместных знаков пунктуации?")
    criteria4_score: int = \
        Field(description="Оценка: Нет просторечий и неуместных знаков пунктуации (0-2).")
    
    criteria5_consideration: str = \
        Field(description="Рассуждение: Все ссылки на документы вынесены в отдельное поле (used_references) корректно?")
    criteria5_score: int = \
        Field(description="Оценка: Все ссылки на документы вынесены в отдельное поле (used_references) корректно (0-2).")

    
class JudgeContentResponse(BaseModel):
    """Оценка ответа юридического консультанта по заданным критериям."""

    criteria1_consideration: str = \
        Field(description="Рассуждение:  Рассуждения модели опираются на предоставленный контекст, а не её собственные догадки?")
    criteria1_score: int = \
        Field(description="Оценка: Рассуждения модели опираются на предоставленный контекст, а не её собственные догадки (0-2).")
    
    criteria2_consideration: str = \
        Field(description="Рассуждение:  Смысл не избыточен, не дублируется от предложения к предложению?")
    criteria2_score: int = \
        Field(description="Оценка: Смысл не избыточен, не дублируется от предложения к предложению (0-2).")
    
    criteria3_consideration: str = \
        Field(description="Рассуждение:  Прослеживается логическая связь от запроса пользователя к ответу, внутри самого ответа?")
    criteria3_score: int = \
        Field(description="Оценка: Прослеживается логическая связь от запроса пользователя к ответу, внутри самого ответа (0-2).")
    
    criteria4_consideration: str = \
        Field(description="Рассуждение:  Сложность терминов и пояснений ответа соотносится с профессиональностью запроса пользователя?")
    criteria4_score: int = \
        Field(description="Оценка: Сложность терминов и пояснений ответа соотносится с профессиональностью запроса пользователя (0-2).")
    
    criteria5_consideration: str = \
        Field(description="Рассуждение:  Ответ модели действительно может быть полезен пользователю и отвечает на его запрос?")
    criteria5_score: int = \
        Field(description="Ответ модели действительно может быть полезен пользователю и отвечает на его запрос (0-2).")


class ReferenceSearch(BaseModel):
    document: str
    name: str


class UserQuestion(BaseModel):
    contents: str
