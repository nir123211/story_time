import json
import os
from pathlib import Path
from misc import keys
from openai import OpenAI
from collections import OrderedDict
from itertools import chain
client = OpenAI(api_key=keys.gpt_key)


def request_characters(story):
    # load prompt
    init_prompt = Path('scripts/text_generation/prompts/generate_characters.txt').read_text()

    messages = [{"role": "user",
                 "content": story},
                {"role": "user",
                 "content": init_prompt}
                ]
    chat_completion = client.chat.completions.create(messages=messages, model="gpt-4o-mini")
    chat_completion = chat_completion.choices[0].message.content
    characters = chat_completion.encode(encoding='UTF-8', errors='strict').decode()
    characters = characters[characters.index('{'):]
    characters = characters[:characters.index('```')]
    return characters


def create_characters(story_dir):
    print('creating characters')
    story = (story_dir / "story_lines.txt").read_text()
    characters = request_characters(story)
    (story_dir / "characters.txt").write_text(characters)
    (story_dir / "characters.json").write_text(json.dumps(json.loads(characters), indent=2))


if __name__ == '__main__':
    os.chdir("../..")
    story_dirr = Path() / "stories" / "The Gallant Horse"
    create_characters(story_dirr)
