import json
from pathlib import Path
from collections import OrderedDict

from scripts.text_to_speech.voices import get_random_voice
from scripts.text_generation.models.gpt_4_o import generate_text


def request_story(prompt: str) -> str:
    """Load the generation prompt and call your LLM."""
    init_prompt_path = Path('scripts/text_generation/prompts/generate_story.txt')
    init_prompt = init_prompt_path.read_text(encoding="utf-8", errors="ignore")
    messages = [
        {"role": "user", "content": init_prompt},
        {"role": "user", "content": prompt},
    ]
    story_text = generate_text(None, messages)
    return story_text


def cut_story_to_lines(story_text: str) -> list[str]:
    """Split into lines, keep only meaningful ones, preserve order."""
    story_lines = story_text.split('\n')
    story_lines = [line.strip() for line in story_lines if len(line.strip()) > 4]
    return story_lines


def sanitize_title_for_fs(title: str) -> str:
    """Make a safe folder name (Windows/macOS/Linux friendly)."""
    forbidden = '<>:"/\\|?*'
    cleaned = ''.join('_' if ch in forbidden else ch for ch in title).strip()
    # Avoid empty names
    return cleaned if cleaned else "story"


def create_line_dirs(story_dir: Path) -> None:
    """Create per-line directories and write line.txt with UTF-8."""
    story_json_path = story_dir / "story.json"
    story_dict = json.loads(story_json_path.read_text(encoding="utf-8"))
    for line_key, line_txt in story_dict.items():
        line_dir = story_dir / line_key
        line_dir.mkdir(exist_ok=True)
        # IMPORTANT: write the line as-is; do NOT split by colon.
        (line_dir / "line.txt").write_text(line_txt, encoding="utf-8")


def create_story(prompt: str) -> Path:
    print('creating story')
    story_text = request_story(prompt)
    story_lines = cut_story_to_lines(story_text)

    # Title = first line, cleaned
    if not story_lines:
        raise ValueError("Story generation returned no usable lines.")
    raw_title = story_lines[0].replace('"', '').replace('*', '').split(': ')[-1]
    story_title = sanitize_title_for_fs(raw_title)

    story_dict = OrderedDict((f'line{index + 1}', line) for index, line in enumerate(story_lines))

    story_dir = Path('stories') / story_title
    story_dir.mkdir(parents=True, exist_ok=True)

    # Write all artifacts as UTF-8
    (story_dir / "story.txt").write_text(story_text, encoding="utf-8")
    (story_dir / "story_lines.txt").write_text("\n\n".join(story_lines), encoding="utf-8")
    (story_dir / "story.json").write_text(
        json.dumps(story_dict, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    (story_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    (story_dir / "voice.txt").write_text(get_random_voice(), encoding="utf-8")

    create_line_dirs(story_dir)
    return story_dir


def change_story(story_dir: Path, new_story: str) -> Path:
    """Rename folder to new title, rewrite artifacts, and rebuild line dirs."""
    new_lines = cut_story_to_lines(new_story)
    if not new_lines:
        raise ValueError("New story has no usable lines.")
    new_title_raw = new_lines[0].replace('"', '').replace('*', '').split(': ')[-1]
    new_title = sanitize_title_for_fs(new_title_raw)

    new_story_dir = story_dir.parent / new_title
    story_dir.rename(new_story_dir)
    story_dir = new_story_dir

    (story_dir / "story.txt").write_text(new_story, encoding="utf-8")
    (story_dir / "story_lines.txt").write_text("\n\n".join(new_lines), encoding="utf-8")

    story_dict = OrderedDict((f'line{index + 1}', line) for index, line in enumerate(new_lines))
    (story_dir / "story.json").write_text(
        json.dumps(story_dict, indent=2, ensure_ascii=False),
        encoding="utf-8")

    create_line_dirs(story_dir)
    return story_dir

