from pathlib import Path
import os
from concurrent.futures import ThreadPoolExecutor

from tqdm import tqdm
import replicate


FLUX_WORKERS = 4


def generate_image_from_prompt(client: replicate.Client, image_prompt: str, output_path, pbar=None):
    output = client.run(
        "bytedance/seedream-3",
        input={
            "size": "regular",
            "width": 2048,
            "height": 2048,
            "prompt": image_prompt,
            "aspect_ratio": "16:9",
            "guidance_scale": 2.5
        }
    )
    with open(output_path, "wb") as file:
        file.write(output.read())
    if pbar:
        pbar.update(1)


def generate_story_images(story_dir: Path, force=False):
    client = replicate.Client(os.environ["REPLICATE_KEY"])

    lines = [line for line in os.listdir(story_dir) if (story_dir / line).is_dir() and 'line' in line]
    lines = sorted(lines, key=lambda folder: int(folder.replace('line', '')))
    line_folders: [Path] = [(story_dir / line) for line in lines if (story_dir / line).is_dir()]

    pbar = tqdm(total=len(line_folders), desc="generating images:")
    with ThreadPoolExecutor(max_workers=FLUX_WORKERS) as thread_pool:
        if FLUX_WORKERS > 1:
            processes = []
        for index, line_folder in enumerate(line_folders):
            if (line_folder / 'image.png').exists() and not force:
                pbar.update(1)
            elif (line_folder / 'image.txt').exists() or force:
                image_prompt = (line_folder / 'image.txt').read_text()
                # Use threads
                if FLUX_WORKERS > 1:
                    processes.append(thread_pool.submit(generate_image_from_prompt, client,
                                                        image_prompt, line_folder / 'image.png', pbar))
                else:
                    generate_image_from_prompt(client, image_prompt, line_folder / 'image.png', pbar)
        if FLUX_WORKERS > 1:
            processes = [process.result() for process in processes]


if __name__ == '__main__':
    prompt = "a dog"
    print(os.getenv("REPLICATE_KEY"))
    generate_image_from_prompt(replicate.Client(os.getenv("REPLICATE_KEY")), prompt, "david.png")

