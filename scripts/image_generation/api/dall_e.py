from openai import OpenAI
import requests

from misc import keys


def init_model():
    return OpenAI(api_key=keys.gpt_key)


def generate_image(model, prompt, file_path, pbar):
    response = model.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1)

    image_url = response.data[0].url
    image_content = requests.get(image_url).content
    with open(file_path, mode="wb") as file:
        file.write(image_content)

    if pbar:
        pbar.update(1)


if __name__ == '__main__':
    generate_image('a happy farmer wearing overalls and a wide brimmed hat, holding a torch high while running. '
                   'grayscale sketch.', 'dog.png', None)