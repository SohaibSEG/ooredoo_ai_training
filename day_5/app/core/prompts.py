from pathlib import Path


PROMPT_PATH = Path(__file__).with_name("system_prompt.txt")


def load_prompt_template() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")
