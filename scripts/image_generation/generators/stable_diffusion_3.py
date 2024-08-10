import os
from pathlib import Path

from diffusers import AutoPipelineForText2Image
import torch

pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16")
pipe.to("cuda")


def generate_image(image_prompt):
    image = pipe(prompt=image_prompt, num_inference_steps=20, guidance_scale=0.0).images[0]
    return image


def generate_story_images(story_dir: Path):
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


if __name__ == '__main__':
    image = generate_image("funny dog")
    image.save("hello.png")