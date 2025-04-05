import requests
import json
import re

def get_tags_via_deepinfra(text: str, tags: list, api_key: str, max_tags: int = 3) -> list:
    """
    Возвращает топ-N тегов для текста через Mixtral-8x7B-Instruct
    
    :param text: Анализируемый текст
    :param tags: Список возможных тегов
    :param api_key: API-ключ DeepInfra
    :param max_tags: Сколько тегов вернуть
    :return: Список релевантных тегов
    """
    prompt = f"""Текст: {text}
Доступные теги: {", ".join(tags)}
Инструкция: Выбери {max_tags} самых релевантных тегов из списка. Ответь ТОЛЬКО JSON-массивом, например: ["тег1", "тег2"]"""

    response = requests.post(
        "https://api.deepinfra.com/v1/inference/mistralai/Mixtral-8x7B-Instruct-v0.1",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "input": prompt,
            "temperature": 0.1,
            "max_new_tokens": 100
        }
    )

    if response.status_code == 200:
        try:
            # Извлекаем текст ответа
            response_text = response.json()["results"][0]["generated_text"].strip()
            
            # Удаляем возможные Markdown-разметки и лишние символы
            cleaned_response = re.sub(r'[\`\n]', '', response_text)
            
            # Ищем JSON-массив в тексте
            json_match = re.search(r'\[.*?\]', cleaned_response)
            
            if json_match:
                json_str = json_match.group()
                # Заменяем одинарные кавычки на двойные
                json_str = json_str.replace("'", '"')
                return json.loads(json_str)[:max_tags]
            return []
            
        except Exception as e:
            print(f"Ошибка: {e}")
            print(f"Полученный ответ: {response_text}")
            return []
    else:
        print(f"API Error {response.status_code}: {response.text}")
        return []

# Пример использования (остается без изменений)
if __name__ == "__main__":
    DEEPINFRA_API_KEY = "v2LZibdTkgFYNktbHWhNC79ZeqIM6mDA"
    
    text_example = "Компания NVIDIA анонсировала новый процессор для обучения нейросетей с рекордной производительностью."
    tags_example = [
        "технологии", "спорт", "медицина", 
        "искусственный интеллект", "финансы", "железо"
    ]
    
    result_tags = get_tags_via_deepinfra(
        text_example, 
        tags_example,
        DEEPINFRA_API_KEY
    )
    
    print(f"Текст: {text_example}")
    print(f"Найденные теги: {result_tags}")