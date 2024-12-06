import os
import json
from pathlib import Path

from scripts.text_generation.models.gpt_4_o import generate_text


def request_image_prompts(story_dir):
    print("creating image prompts")
    init_prompt = ((Path() / "scripts" / "text_generation" / "prompts" / "generate_images.txt").
                   read_text(encoding="utf-8", errors="replace"))
    characters = (story_dir / "characters.txt").read_text()
    story_json = (story_dir / "story.json").read_text()

    messages = [{"role": "user",
                 "content": init_prompt},
                {"role": "user",
                 "content": characters},
                {"role": "user",
                 "content": story_json}]

    image_prompts = generate_text(None, messages)
    image_prompts = image_prompts[image_prompts.index('{'):]
    image_prompts = image_prompts[:image_prompts.index('```')]
    (story_dir / "images.txt").write_text(image_prompts)
    (story_dir / "images.json").write_text(json.dumps(json.loads(image_prompts), indent=2))


def parse_image_prompts(story_dir: Path):
    image_prompts = json.loads((story_dir / "images.json").read_text())
    for line, image_prompt in image_prompts.items():
        (story_dir / line / "image.txt").write_text(image_prompt["prompt"])


def add_image_prompts(story_dir: Path):
    request_image_prompts(story_dir)
    parse_image_prompts(story_dir)


if __name__ == '__main__':
    os.chdir("../..")
    story_dirr = Path() / "stories" / "The Gallant Horse"
    # request_image_prompts(story_dirr)
    parse_image_prompts(story_dirr)