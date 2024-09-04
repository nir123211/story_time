import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from openai import OpenAI
import requests
from tqdm import tqdm

from misc import keys
client = OpenAI(api_key=keys.gpt_key)


def generate_image(prompt, file_path, pbar, init=False):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    image_content = requests.get(image_url).content
    with open(file_path, mode="wb") as file:
        file.write(image_content)

    if pbar:
        pbar.update(1)


def generate_story_images(story_dir):
    lines = [line for line in os.listdir(story_dir) if (story_dir / line).is_dir()]
    lines = sorted(lines, key=lambda folder: int(folder.replace('line', '')))
    line_folders: [Path] = [(story_dir / line) for line in lines if (story_dir / line).is_dir()]

    processes = []
    with ThreadPoolExecutor() as thread_pool:
        pbar = tqdm(desc='Creating images', total=len(line_folders))
        for line_folder in line_folders:
            if (line_folder / 'image.png').exists():
                pbar.update(1)
            elif (line_folder / 'image.txt').exists():
                image_prompt = (line_folder / 'image.txt').read_text()
                processes.append(thread_pool.submit(generate_image, image_prompt, (line_folder / 'image.png'), pbar))
            else:
                raise FileNotFoundError(f"no image prompt in {line_folder}")
    processes = [process.result() for process in processes]


if __name__ == '__main__':
    generate_image('a happy farmer wearing overalls and a wide brimmed hat, holding a torch high while running. '
                   'grayscale sketch.', 'dog.png', None)