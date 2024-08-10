import os
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from misc import keys
from openai import OpenAI
from collections import OrderedDict
from itertools import chain
client = OpenAI(api_key=keys.gpt_key)


def request_image_prompts(story_dir):
    print("creating image prompts")
    init_prompt = (Path() / "scripts" / "text_generation" / "prompts" / "generate_images.txt").read_text()
    characters = (story_dir / "characters.txt").read_text()
    story_json = (story_dir / "story.json").read_text()

    messages = [{"role": "user",
                 "content": init_prompt},
                {"role": "user",
                 "content": characters},
                {"role": "user",
                 "content": story_json}]

    chat_completion = client.chat.completions.create(messages=messages, model="gpt-4o-mini")
    chat_completion = chat_completion.choices[0].message.content
    image_prompts = chat_completion.encode(encoding='UTF-8', errors='strict').decode()
    image_prompts = image_prompts[image_prompts.index('{'):]
    image_prompts = image_prompts[:image_prompts.index('```')]
    (story_dir / "images.txt").write_text(image_prompts)
    (story_dir / "images.json").write_text(json.dumps(json.loads(image_prompts), indent=2))


def parse_image_prompts(story_dir: Path):
    prompt_start = "An illustration in the style of a classic book drawing, with clean lines"
    image_prompts = json.loads((story_dir / "images.json").read_text())
    for line, image_prompt in image_prompts.items():
        (story_dir / line / "image.txt").write_text(prompt_start + image_prompt["prompt"])


def add_image_prompts(story_dir: Path):
    request_image_prompts(story_dir)
    parse_image_prompts(story_dir)


if __name__ == '__main__':
    os.chdir("../..")
    story_dirr = Path() / "stories" / "The Gallant Horse"
    # request_image_prompts(story_dirr)
    parse_image_prompts(story_dirr)