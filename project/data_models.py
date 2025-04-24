from pydantic import BaseModel, Field
from typing import List, Dict, Tuple


class SearchResponse(BaseModel):
    """Указание списка документов, к которым нужно обратиться для ответа пользователю, 
    и сами вопросы к базе данных этих документов"""

    thinking_process: str = \
        Field(description="Длинный развёрнутый пошаговый ход мыслей и рассуждения о задаче.")
    question_is_relevant: bool = \
        Field(description="Позволяют ли указанные документы ответить на запрос пользователя?")
    queries_to_make: List[Tuple[str, str]] = \
        Field(description="Список выбранных пар (Документ, Запрос).")

class AnswerResponse(BaseModel):
    """Ответ пользователю и список отсылок НА ПРЕДОСТАВЛЕННЫЕ ДОКУМЕНТЫ"""

    thinking_process: str = \
        Field(description="ДЛИННЫЙ РАЗВЁРНУТЫЙ ХОД РАССУЖДЕНИЯ НАД ЗАПРОСОМ, включая размышления о том, куда и какие отсылки поставить")
    final_answer: str = \
        Field(description="Ответ пользователю.")
    used_references: Dict[int, str] = \
        Field(description="Соотвествия номера отсылки и испольованного документа.")
    
class JudgeFormResponse(BaseModel):
    """Оценка ответа юридического консультанта по форме ответа"""

    criteria1_consideration: str = \
        Field(description="Рассуждения насчёт того, какую оценку поставить по первому критерию.")
    criteria1_score: int = \
        Field(description="Оценка 0-2.")

    
class JudgeContentResponse(BaseModel):
    """Ответ пользователю и список отсылок НА ПРЕДОСТАВЛЕННЫЕ ДОКУМЕНТЫ"""

    thinking_process: str = \
        Field(description="ДЛИННЫЙ РАЗВЁРНУТЫЙ ХОД РАССУЖДЕНИЯ НАД ЗАПРОСОМ, включая размышления о том, куда и какие отсылки поставить")
    final_answer: str = \
        Field(description="Ответ пользователю.")
    used_references: Dict[int, str] = \
        Field(description="Соотвествия номера отсылки и испольованного документа.")