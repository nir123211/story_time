import json
import os
from pathlib import Path


from scripts.text_generation.models.gpt_4_o import generate_text


def request_characters(story_prompt, story):
    # load prompt
    init_prompt = Path('scripts/text_generation/prompts/generate_characters.txt').read_text()

    messages = [{"role": "system",
                 "content": init_prompt},
                {"role": "system",
                 "content": story_prompt},
                {"role": "system",
                 "content": story}
                ]
    characters = generate_text(None, messages)
    characters = characters[characters.index('{'):]
    characters = characters[:characters.index('```')]
    return characters


def add_characters(story_dir):
    print('creating characters')
    story = (story_dir / "story_lines.txt").read_text()
    story_prompt = (story_dir / "prompt.txt").read_text()
    characters = request_characters(story_prompt, story)
    (story_dir / "characters.txt").write_text(characters)
    (story_dir / "characters.json").write_text(json.dumps(json.loads(characters), indent=2))


if __name__ == '__main__':
    os.chdir("../..")
    story_dirr = Path() / "stories" / "The Gallant Horse"
    add_characters(story_dirr)
