import os
from pathlib import Path

from scripts.image_generation.local import open_dall_e
from scripts.image_generation.local import sdxl_turbo
from scripts.image_generation.local import stable_diffusion_3_5

from scripts.image_generation.api import dall_e

local_models = {"sdxl": sdxl_turbo, 'open_dall_e': open_dall_e, "stable_diffusion_3_5": stable_diffusion_3_5}
api_models = {"dall_e": dall_e}
all_models = {'local': local_models, "api": api_models}


def generate_story_images(story_dir: Path, model_name, mode="local"):
    model_script = all_models[mode][model_name]
    model = model_script.init_model()

    lines = [line for line in os.listdir(story_dir) if (story_dir / line).is_dir() and 'line' in line]
    lines = sorted(lines, key=lambda folder: int(folder.replace('line', '')))
    line_folders: [Path] = [(story_dir / line) for line in lines if (story_dir / line).is_dir()]

    for index, line_folder in enumerate(line_folders):
        print("creating image", index + 1)
        if (line_folder / 'image.png').exists():
            pass
        elif (line_folder / 'image.txt').exists():
            image_prompt = (line_folder / 'image.txt').read_text()
            model_script.generate_image(model, image_prompt, line_folder / 'image.png')
        else:
            raise FileNotFoundError(f"no image prompt in {line_folder}")