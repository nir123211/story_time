import json
import os
from pathlib import Path
from misc import keys
from openai import OpenAI
from collections import OrderedDict
from itertools import chain
client = OpenAI(api_key=keys.gpt_key)


def request_story(prompt):
    # load prompt
    init_prompt = Path('scripts/text_generation/prompts/generate_story.txt').read_text()

    messages = [{"role": "user",
                 "content": init_prompt},
                {"role": "user",
                 "content": prompt}
                ]
    chat_completion = client.chat.completions.create(messages=messages, model="gpt-4o-mini")
    chat_completion = chat_completion.choices[0].message.content
    story_text = chat_completion.encode(encoding='UTF-8', errors='strict').decode()

    return story_text


def cut_story_to_lines(story_text):
    story_lines = story_text.split('\n')
    story_lines = [line.split('.') for line in story_lines]
    story_lines = [*chain.from_iterable(story_lines)]
    story_lines = [*filter(lambda line: len(line) > 4, story_lines)]
    story_lines = [line.strip(" ") for line in story_lines]
    return story_lines


def create_line_dirs(story_dir: Path):
    story_dict = json.loads((story_dir / "story.json").read_text())
    for line, line_txt in story_dict.items():
        line_dir = story_dir / line
        line_dir.mkdir(exist_ok=True)
        with (line_dir / "line.txt").open('w') as f:
            f.write(line_txt.split(': ')[-1])


def create_story(prompt):
    print('creating story')
    story_text = request_story(prompt)
    story_lines = cut_story_to_lines(story_text)
    # fix title
    story_lines[0] = story_lines[0].replace('"', '').replace('*', '').split(': ')[-1]
    story_title = story_lines[0]

    story_dict = OrderedDict([(f'line{index+1}', line) for index, line in enumerate(story_lines)])

    story_dir = Path() / 'stories' / story_title
    story_dir.mkdir(parents=True, exist_ok=True)
    (story_dir / "story.txt").write_text(story_text)
    (story_dir / "story_lines.txt").write_text("\n\n".join(story_lines))
    (story_dir / "story.json").write_text(json.dumps(story_dict, indent=2))

    create_line_dirs(story_dir)
    return story_dir


def change_story(story_dir, new_story):
    new_story_dir = (story_dir.parent / new_story.split('\n')[0])
    story_dir.rename(new_story_dir)
    story_dir = new_story_dir
    (story_dir / "story.txt").write_text(new_story)
    story_lines = cut_story_to_lines(new_story)
    (story_dir / "story_lines.txt").write_text("\n\n".join(story_lines))
    story_dict = OrderedDict([(f'line{index+1}', line) for index, line in enumerate(story_lines)])
    (story_dir / "story.json").write_text(json.dumps(story_dict, indent=2))
    create_line_dirs(story_dir)
    return story_dir



if __name__ == '__main__':
    os.chdir("../..")
    story_dirr = Path() / "stories" / "Nir the King and the Mysterious Cabbage"
    change_story(story_dirr, "hellooooooo")