from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# Загрузка переменных окружения из .env файла
load_dotenv()

# Установите ваш API ключ OpenAI
OpenAI.api_key = os.environ.get("OPENAI_API_KEY")

# JSON-шаблон
PROMPT_TEMPLATE_JSON = '''
{
    "context": "Message from user {text}.",
    "question": "List of categories: Shopping, Groceries, Restaurants and eating out, Transportation, Entertainment, Health, Housing. What category does the user's purchase most likely fall into and how much was spent and with what currency? Use only English to answer",
    "response_format": {
        "purchase_type": "",
        "amount spent": "",
        "currency in standard form of the word": ""
    }
}
'''

# Загрузка шаблона из JSON
prompt_template = json.loads(PROMPT_TEMPLATE_JSON)

def get_response(text):

    # Форматирование шаблона
    formatted_prompt = prompt_template["context"].format(text=text) + "\n\n" + prompt_template["question"] + "\n\n" + "Please respond in the following JSON format:\n" + json.dumps(prompt_template["response_format"], indent=4)

    client = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. When providing numerical values, please ensure that: Numbers are formatted without commas. Use a period (.) only if there is a fractional part. For example, '5,000' should be formatted as '5000' and '5,000.50' should be formatted as '5000.50'. Do not use commas in any numerical values."},
            {"role": "user", "content": formatted_prompt}
                  ]
        )
    
    response = response.choices[0].message.content.strip()
    print(response)
    return json.loads(response)

