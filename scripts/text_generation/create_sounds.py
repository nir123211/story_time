import os
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from misc import keys
from openai import OpenAI
from collections import OrderedDict
from itertools import chain
client = OpenAI(api_key=keys.gpt_key)


def request_sounds(story_dir):
    print("creating sounds")
    init_prompt = (Path() / "scripts" / "text_generation" / "prompts" / "generate_sounds.txt").read_text()
    story_json = (story_dir / "story.json").read_text()

    messages = [{"role": "user",
                 "content": init_prompt},
                {"role": "user",
                 "content": story_json}]

    chat_completion = client.chat.completions.create(messages=messages, model="gpt-4o-mini")
    chat_completion = chat_completion.choices[0].message.content
    image_prompts = chat_completion.encode(encoding='UTF-8', errors='strict').decode()
    image_prompts = image_prompts[image_prompts.index('{'):]
    image_prompts = image_prompts[:image_prompts.index('```')]
    (story_dir / "sounds.txt").write_text(image_prompts)
    (story_dir / "sounds.json").write_text(json.dumps(json.loads(image_prompts), indent=2))


def parse_sounds(story_dir: Path):
    sounds_prompts = json.loads((story_dir / "sounds.json").read_text())
    for line, sounds in sounds_prompts.items():
        if 'music' in sounds.keys():
            (story_dir / line / "music.txt").write_text(sounds["music"])
        if 'sound' in sounds.keys():
            (story_dir / line / "sound.txt").write_text(sounds["sound"])


def add_sounds(story_dir: Path):
    request_sounds(story_dir)
    parse_sounds(story_dir)


if __name__ == '__main__':
    os.chdir("../..")
    story_dirr = Path() / "stories" / "The Gallant Horse"
    request_sounds(story_dirr)
    parse_sounds(story_dirr)