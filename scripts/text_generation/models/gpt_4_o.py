from openai import OpenAI

from misc import keys


def init_model():
    return


def generate_text(model, messages):
    client = OpenAI(api_key=keys.gpt_key)
    chat_completion = client.chat.completions.create(messages=messages, model="gpt-4o")
    chat_completion = chat_completion.choices[0].message.content
    return chat_completion.encode(encoding='UTF-8', errors='strict').decode()
