# -*- coding: utf-8 -*-
from langchain_community.chat_models import GigaChat
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from api_getter import api_getter
from prompts import QA_CREATOR, WRONG_A_GENERTOR, REGENERATOR_1, MAP_SUM, COMBINE_SUM
from document_loaders import text_splitter, pre_processing
import ast


def regenerator(chunk, first_output):
    token = api_getter()["access_token"]
    print(f'\nНовый токен для регенирации:\n{token}')

    llm = GigaChat(access_token=token, verify_ssl_certs=False)
    regen_template = REGENERATOR_1
    regen_prompt = PromptTemplate.from_template(regen_template)

    regen_chain = LLMChain(llm=llm, prompt=regen_prompt)
    res = regen_chain.invoke({"chunk": chunk, "question": first_output})
    print(f"\nПосле регена:\n{res['text']}")

    return res['text']


def check_questions_and_answers(input_strings):
    questions_only = True
    for string in input_strings:
        if '?' not in string:
            questions_only = False
            break
    return not questions_only


def string_to_sets(string, chunk):
    final_qa_list = []
    if "\n" in string:
        substrings = string.split('\n')
        for substring in substrings:
            listed_string = ast.literal_eval(substring)
            if check_questions_and_answers(listed_string):
                final_qa_list.append(listed_string)
    else:
        listed_string = ast.literal_eval(string)
        if check_questions_and_answers(listed_string):
            final_qa_list.extend(listed_string)
        else:
            answers = regenerator(chunk, string)
            index = answers.find('[')
            subanswers = answers[index:]
            if "\n" in subanswers:
                listed_answers = ast.literal_eval(subanswers.replace("\n", ","))
                for i in range(len(listed_string)):
                    pair = [listed_string[i], listed_answers[i][0]]
                    final_qa_list.append(pair)
            else:
                listed_answers = ast.literal_eval(subanswers)

                for i in range(len(listed_string)):
                    pair = [listed_string[i], listed_answers[i]]
                    final_qa_list.append(pair)

    return final_qa_list


def string_to_sets_wa(string):
    pre_string = string.strip("[]")
    pre_string = pre_string.strip("''")
    if "','" in pre_string:
        segments = pre_string.split("','")
    elif "',\n'" in pre_string:
        segments = pre_string.split("',\n'")
    else:
        segments = pre_string.split("', '")
    return segments


def wa_validation(set_a, set_wa):
    new_set = []
    count = 0
    for segments_wa, segments_a in zip(set_wa, set_a):
        count += 1
        valid_segment = {f"question{count}": segments_a[0], "answer1": segments_a[1], "answer2": segments_wa[0],
                         "answer3": segments_wa[1], "answer4": segments_wa[2], "right": '1'}
        new_set.append(valid_segment)

    valid_set = []
    for segm in new_set:
        if segm["answer1"] != segm["answer2"] != segm["answer3"]:
            valid_set.append(segm)

    return valid_set


def qa_generator(document):
    # Получаем контент документа
    document_content = pre_processing(document)
    # Делим на чанки
    chunks = text_splitter(document_content)

    token = api_getter()["access_token"]
    print(f'Новый токен:\n{token}')
    llm = GigaChat(access_token=token, verify_ssl_certs=False)

    qa_creator_template = QA_CREATOR
    qa_creator_prompt = PromptTemplate.from_template(qa_creator_template)
    # Сет с вопросами и ответами для всех чанков
    qa_sets = []
    for chunk in chunks:
        qa_chain = LLMChain(llm=llm, prompt=qa_creator_prompt)
        answers = qa_chain.invoke({"chunk": chunk})

        print(f"\nВходной чанк:\n{answers['chunk']}\nОтвет llm:\n{answers['text']}\n")

        qa_sets.extend(string_to_sets(answers['text'], chunk))

    print(f"Отформатированное множество:\n{qa_sets}\n")
    wrong_answers_template = WRONG_A_GENERTOR
    wrong_answers_prompt = PromptTemplate.from_template(wrong_answers_template)

    worng_a_chain = LLMChain(llm=llm, prompt=wrong_answers_prompt)
    # Сет с неверными ответами
    wa_sets = []
    for qa in qa_sets:
        q = qa[0]
        a = qa[1]
        variant = worng_a_chain.invoke({"question": q, "answer": a})
        print(f"Входной вопрос:\n{variant['question']}\nОтвет: {variant['answer']}\nОтвет llm:\n{variant['text']}\n")
        wa = string_to_sets_wa(variant['text'])
        wa_sets.append(wa)
    print(f"Множество ответов:\n{wa_sets}")

    validated_test = wa_validation(qa_sets, wa_sets)
    print(validated_test)
    return str(validated_test)


def summary(document, facts_num):
    # Получаем контент документа
    document_content = pre_processing(document)
    # Делим на чанки
    chunks = text_splitter(document_content)

    token = api_getter()["access_token"]
    print(f'Новый токен:\n{token}')
    llm = GigaChat(access_token=token, verify_ssl_certs=False)

    map_sum = MAP_SUM
    map_sum_prompt = PromptTemplate.from_template(map_sum)

    map_chain = LLMChain(llm=llm, prompt=map_sum_prompt)
    # Результат по чанкам
    map_sums_chunks = ""
    for chunk in chunks:
        sum_part = map_chain.invoke({"chunk": chunk})
        map_sums_chunks += f"{sum_part['text']}\n\n"

    print(map_sums_chunks)
    combine_sum = COMBINE_SUM
    combime_sum_prompt = PromptTemplate.from_template(combine_sum)
    combine_chain = LLMChain(llm=llm, prompt=combime_sum_prompt)
    res = combine_chain.invoke({"map_sums": map_sums_chunks, "facts_num": facts_num})

    return res['text']
