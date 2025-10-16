import os
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from tqdm import tqdm
from scripts.text_generation.models.gpt_4_o import generate_text


def request_image_prompts(story_dir):
    print("creating image prompts")
    if (story_dir / "images_before.json").exists():
        return
    init_prompt = ((Path() / "scripts" / "text_generation" / "prompts" / "generate_images.txt").
                   read_text(encoding="utf-8", errors="replace"))
    characters_prompt = (story_dir / "characters.txt").read_text(encoding="utf-8")
    story_json = (story_dir / "story.json").read_text(encoding="utf-8")

    messages = [{"role": "system",
                 "content": init_prompt},
                {"role": "user",
                 "content": characters_prompt},
                {"role": "user",
                 "content": story_json}]

    image_prompts = generate_text(None, messages)
    (story_dir / "images_before.txt").write_text(image_prompts)
    image_prompts = image_prompts[image_prompts.index('{'):]
    if '```' in image_prompts:
        image_prompts = image_prompts[:image_prompts.index('```')]
    (story_dir / "images_before.json").write_text(json.dumps(json.loads(image_prompts), indent=2))


def enrich_prompts(story_dir):
    if (story_dir / "images.json").exists():
        return
    image_prompts = json.loads((story_dir / "images_before.json").read_text(encoding="utf-8"))
    translation_prompt = ((Path() / "scripts" / "text_generation" / "prompts" / "enhance_prompts.txt").
                          read_text(encoding="utf-8", errors="replace"))
    characters = (story_dir / "characters.json").read_text(encoding="utf-8")

    pbar = tqdm(total=len(image_prompts), desc="Enriching image prompts:")
    processes = []
    with ThreadPoolExecutor(max_workers=4) as thread_pool:
        for line, prompt in image_prompts.items():
            processes.append(thread_pool.submit(enrich_prompt, translation_prompt,
                                                characters, image_prompts, line, pbar))
            time.sleep(3)
    processes = [process.result() for process in processes]
    (story_dir / "images.txt").write_text(str(image_prompts))
    (story_dir / "images.json").write_text(json.dumps(image_prompts, indent=2))


def enrich_prompt(init_prompt, characters_dict, image_prompts, line, pbar=None):
    messages = [{"role": "system",
                 "content": init_prompt},
                {"role": "user",
                 "content": characters_dict},
                {"role": "user",
                 "content": image_prompts[line]["prompt"]}]
    image_prompts[line]["prompt"] = generate_text(None, messages)
    if pbar:
        pbar.update(1)
    return


def parse_image_prompts(story_dir: Path):
    image_prompts = json.loads((story_dir / "images.json").read_text())
    for line, image_prompt in image_prompts.items():
        (story_dir / line / "image.txt").write_text(image_prompt["prompt"])


def add_image_prompts(story_dir: Path, force=False):
    if (not (story_dir / "images.json").exists()) or force:
        request_image_prompts(story_dir)
        enrich_prompts(story_dir)
        parse_image_prompts(story_dir)


if __name__ == '__main__':
    os.chdir("../..")
    story_dirr = Path() / "stories" / "The Gallant Horse"
    # request_image_prompts(story_dirr)
    parse_image_prompts(story_dirr)