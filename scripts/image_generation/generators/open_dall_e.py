import os
from pathlib import Path
import torch
from diffusers import AutoPipelineForText2Image
from tqdm import tqdm

pipeline = AutoPipelineForText2Image.from_pretrained('dataautogpt3/OpenDalleV1.1', torch_dtype=torch.float16).to('cuda')


def generate_image(image_prompt):
    image = pipeline(image_prompt, num_inference_steps=10)["images"][0]
    return image


def generate_story_images(story_dir):
    lines = [line for line in os.listdir(story_dir) if (story_dir / line).is_dir() and 'line' in line]
    lines = sorted(lines, key=lambda folder: int(folder.replace('line', '')))
    line_folders: [Path] = [(story_dir / line) for line in lines if (story_dir / line).is_dir()]

    for index, line_folder in enumerate(line_folders):
        print("creating image", index+1)
        if (line_folder / 'image.png').exists():
            pass
        elif (line_folder / 'image.txt').exists():
            image_prompt = (line_folder / 'image.txt').read_text()
            image = generate_image(image_prompt)
            image.save(line_folder / 'image.png')
        else:
            raise FileNotFoundError(f"no image prompt in {line_folder}")
