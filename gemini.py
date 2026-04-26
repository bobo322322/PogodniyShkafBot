from google import genai
from daily_weather import ai_weather
from google.genai import types as genai_types
from main import GEMINI_KEY

import asyncio
import json

async def ai_recommend(wardrobe_list):
    client = genai.Client(api_key=GEMINI_KEY)
    ai_weather()
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash", contents=f"""
            Ты — стилист во Владивостоке, помогаешь человеку одеться стильно и по погоде. Анализируй его гардероб и стиль. 
            Общайся легко, с юмором, используй эмодзи, но будь краток. Без лишнего форматирования (НЕ ИСПОЛЬЗУЙ ** // <>) 
            Я хочу, чтобы ответ был КРАТКИМ. Учитывай, что сейчас в моде
            
            Погода сегодня:
            {ai_weather()}
            
            Гардероб:
            {wardrobe_list}
            
            Если вещей нет или не хватает, предложи нужные с [+] и поясни, зачем. Смело упоминай актуальные бренды, 
            если уместно. Учитывай цвета, стили, сезонность.
            
            Напиши 2-3 предложения с советом, а в конце добавь список «Коротко:», где только названия нужных вещей
            ЧЕРЕЗ ДЕФИС (добавленные помечай [+]). Без абзацев внутри списка. Главное — живо, по делу и с улыбкой.
        """
    )
    # print(response)
    return response.text
# gemini()


async def image_description(path):
    model_id = 'gemini-2.5-flash'

    client = genai.Client(api_key=GEMINI_KEY)

    with open(path, 'rb') as f:
        image_bytes = f.read()

    response = await asyncio.to_thread(
        client.models.generate_content,
        model=model_id,
    contents=[
            genai_types.Part.from_bytes(
                data=image_bytes,
                mime_type='image/jpeg',
            ),
            '''
            Ты — эксперт по гардеробу и моде. Детально проанализируй фото и верни СТРОГО JSON-объект с описанием вещей.
            Если ты можешь однозначно определить бренд одежды, то добавь его в название
            Если на фото НЕТ одежды, обуви или аксессуаров, верни:
            {"is_clothing": False}

            Если на фото одежда:
            {
              "is_clothing": True,
              "item_name": "КОРОТКОЕ название на русском языке. Если можешь определить, то бренд и модель",
              "category": "верхняя одежда/Верх(База)/Низ/Обувь/Аксессуар/Головной убор",
              "material": "основной материал, если можешь распознать или null",
              "color": "основной цвет",
              "style": "к какому стилю относится вещь"
            }

            JSON!!! Всегда возвращай JSON с ключом "items", который содержит массив найденных значимых
            предметов одежды (даже если предмет один), строго
            в формате: {"items": [{"is_clothing": "...", "item_name": "...", "category": "...",
            "material": "...", "color": "...", "style": "..."}, ...]}
            '''
        ],
        config=genai.types.GenerateContentConfig(
            response_mime_type='application/json'
        )
    )
    data = json.loads(response.text)
    # print(data)
    return data




