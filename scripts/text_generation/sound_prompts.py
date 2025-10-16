import os
import json
from pathlib import Path

from scripts.text_generation.models.gpt_4_o import generate_text


def request_sounds(story_dir):
    print("creating sounds")
    init_prompt = (Path() / "scripts" / "text_generation" / "prompts" / "generate_sounds.txt").read_text(errors="ignore")
    story_json = (story_dir / "story.json").read_text(encoding="utf-8")

    messages = [{"role": "system",
                 "content": init_prompt},
                {"role": "user",
                 "content": story_json}]

    sound_prompts = generate_text(None, messages)
    sound_prompts = sound_prompts[sound_prompts.index('{'):]
    sound_prompts = sound_prompts[:sound_prompts.index('```')]
    (story_dir / "sounds.txt").write_text(sound_prompts)
    (story_dir / "sounds.json").write_text(json.dumps(json.loads(sound_prompts), indent=2))


def parse_sounds(story_dir: Path):
    sounds_prompts = json.loads((story_dir / "sounds.json").read_text())
    for line, sounds in sounds_prompts.items():
        if 'music' in sounds.keys():
            (story_dir / line / "music.txt").write_text(sounds["music"])
        if 'sound' in sounds.keys():
            (story_dir / line / "sound.txt").write_text(sounds["sound"])


def add_sound_prompts(story_dir: Path, force=False):
    if (not (story_dir / "sounds.txt").exists()) or force:
        request_sounds(story_dir)
        parse_sounds(story_dir)


if __name__ == '__main__':
    os.chdir("../..")
    story_dirr = Path() / "stories" / "The Gallant Horse"
    request_sounds(story_dirr)
    parse_sounds(story_dirr)