import os
from pathlib import Path


def add_story_images(story_dir: Path, mode='stable_diffusion'):
    if mode == 'open_dall_e':
        from scripts.image_generation.generators.open_dall_e import generate_story_images
    elif mode == 'dall_e':
        from scripts.image_generation.generators.dall_e import generate_story_images
    elif mode == 'stable_diffusion':
        from scripts.image_generation.generators.stable_diffusion_3 import generate_story_images
    else:
        raise ValueError("mode not recognized")

    generate_story_images(story_dir)


if __name__ == '__main__':
    os.chdir("../..")
    story_dirr = Path() / "stories" / "The Brave Pig"
    add_story_images(story_dirr)