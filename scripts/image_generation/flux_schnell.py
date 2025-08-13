from pathlib import Path
import os
from concurrent.futures import ThreadPoolExecutor

from tqdm import tqdm
import replicate
import cv2 as cv

from misc.keys import replicate_key

FLUX_WORKERS = 2

def generate_image_from_prompt(client: replicate.Client, image_prompt: str, output_path, pbar=None):
    output = client.run("black-forest-labs/flux-schnell", input={"prompt": image_prompt})
    with open(str(output_path).replace(".png", ".webp"), "wb") as file:
        file.write(output[0].read())
    image = cv.imread(str(output_path).replace(".png", ".webp"), -1)
    cv.imwrite(output_path, image)
    if pbar:
        pbar.update(1)


def generate_story_images(story_dir: Path, force=False):
    client = replicate.Client(replicate_key)

    lines = [line for line in os.listdir(story_dir) if (story_dir / line).is_dir() and 'line' in line]
    lines = sorted(lines, key=lambda folder: int(folder.replace('line', '')))
    line_folders: [Path] = [(story_dir / line) for line in lines if (story_dir / line).is_dir()]

    pbar = tqdm(total=len(line_folders), desc="generating images:")
    with ThreadPoolExecutor(max_workers=FLUX_WORKERS) as thread_pool:
        if FLUX_WORKERS > 1:
            processes = []
        for index, line_folder in enumerate(line_folders):
            if (line_folder / 'image.png').exists() and not force:
                pass
            elif (line_folder / 'image.txt').exists() or force:
                image_prompt = (line_folder / 'image.txt').read_text()
                # Use threads
                if FLUX_WORKERS > 1:
                    processes.append(thread_pool.submit(generate_image_from_prompt, client,
                                                        image_prompt, line_folder / 'image.png', pbar))
                else:
                    generate_image_from_prompt(client, image_prompt, line_folder / 'image.png', pbar)
            if FLUX_WORKERS > 1:
                processes = [process.result for process in processes]



if __name__ == '__main__':
    prompt = "a dog"
    generate_image_from_prompt(prompt, "david.png")

