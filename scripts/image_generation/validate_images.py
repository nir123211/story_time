from pathlib import Path
import os

import cv2 as cv


def validate_story_images(story_dir: Path):
    missing_lines = []
    corrupted_lines = []
    lines = [line for line in os.listdir(story_dir) if (story_dir / line).is_dir() and 'line' in line]
    lines = sorted(lines, key=lambda folder: int(folder.replace('line', '')))
    line_folders: [Path] = [(story_dir / line) for line in lines if (story_dir / line).is_dir()]

    for index, line_folder in enumerate(line_folders):
        if not (line_folder / 'image.png').exists():
            missing_lines.append(line_folder)
        if cv.imread("image.png") is None:
            corrupted_lines.append(line_folder)

    return missing_lines, corrupted_lines




