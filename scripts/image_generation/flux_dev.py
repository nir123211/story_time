import os
from pathlib import Path
import torch
from diffusers import FluxTransformer2DModel, FluxPipeline
from transformers import T5EncoderModel, CLIPTextModel
from optimum.quanto import freeze, qfloat8, quantize




def generate_image(image_prompt, image_path, pipeline=None, pbar=None):
    if pipeline is None:
        pipe = FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-schnell", torch_dtype=torch.bfloat16)
        pipe.enable_model_cpu_offload()
    image = pipeline(
        image_prompt,
        height=1024,
        width=1024,
        guidance_scale=3.5,
        num_inference_steps=50,
        max_sequence_length=512,
        generator=torch.Generator("cpu").manual_seed(0)
    ).images[0]
    image.save(image_path)
    return image


def generate_story_images(story_dir):
    pipe = FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-schnell", torch_dtype=torch.bfloat16)
    pipe.enable_model_cpu_offload()
    lines = [line for line in os.listdir(story_dir) if (story_dir / line).is_dir() and 'line' in line]
    lines = sorted(lines, key=lambda folder: int(folder.replace('line', '')))
    line_folders: [Path] = [(story_dir / line) for line in lines if (story_dir / line).is_dir()]

    for index, line_folder in enumerate(line_folders):
        print("creating image", index+1)
        if (line_folder / 'image.png').exists():
            pass
        elif (line_folder / 'image.txt').exists():
            image_prompt = (line_folder / 'image.txt').read_text()
            generate_image(image_prompt, (line_folder / 'image.png'), pipeline)
        else:
            raise FileNotFoundError(f"no image prompt in {line_folder}")


if __name__ == '__main__':
    generate_image("a blue cat", "cat.png")