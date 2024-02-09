import random
import json
import re


def generate_random_filename(original_filename):
    extension = original_filename.split('.')[-1]
    random_filename = ''.join(random.choices('0123456789', k=16))
    return f"{random_filename}.{extension}"


def correct_qa_format(raw_str):
    formatted_str = raw_str.replace('[', '{').replace(']', '}').replace('\n', ', ')
    json_str = f"[{formatted_str}]"
    return transform_to_target_format(json_str)


def transform_to_target_format(json_str):
    data = json.loads(json_str)

    transformed_data = []

    for item in data:
        question_data = {"answers": {}}

        for key, value in item.items():
            # Ищем ключ вопроса
            if re.match(r'question\d+', key):
                question_data["question"] = value
            # Ищем ключи ответов
            elif re.match(r'answer\d+', key):
                question_data["answers"][key] = value
            # Обрабатываем ключ правильного ответа
            elif key == "right":
                question_data["right"] = f"answer{value}"

        transformed_data.append(question_data)

    return json.dumps(transformed_data, ensure_ascii=False, indent=2)
