from project.llm import answer, load_index, judge
import sys
import time
import pytest


index_str = load_index()
test_timestamp = time.asctime(time.gmtime(time.time()))


def log_result(res):
     with open(f'logs/[LLM Test] {test_timestamp}.txt'.replace(' ', '_'), "a") as f:
          f.write(res + '\n')

def test_too_complex():
    assert judge(*answer(query="""
                         Права граждан РФ? 
                         Права Президента РФ? 
                         Права Федерального Собрания? 
                         Что такое АО? 
                         ООО? 
                         Беплатно ли образование в РФ для всех? 
                         Можно ли вообще рекламировать политические партии?""", 
                index_str=index_str)) == "TOO COMPLEX"

def test_irrelevant():
    assert judge(*answer(query="йцукенгшщ", 
            index_str=index_str)) == "IRRELEVANT"

def test_simple():
    score = judge(*answer(query="Какие права есть у граждан РФ?", 
                  index_str=index_str))
    assert len(score) == 2
    log_result(f"test_simple -> {score[0]}/{score[1]}")

def test_difficult():
    score = judge(*answer(query="Какие права есть у граждан РФ? А у Президента РФ?", 
                index_str=index_str))
    assert len(score) == 2
    log_result(f"test_difficult -> {score[0]}/{score[1]}")

def test_casual_style():
    score = judge(*answer(query="а всем же короче ьесплатное обучение дают", 
            index_str=index_str))
    assert len(score) == 2
    log_result(f"test_casual_style -> {score[0]}/{score[1]}")

def main(datasets, paths):
    pytest.main(["project/testing/llm_judge_test.py"])