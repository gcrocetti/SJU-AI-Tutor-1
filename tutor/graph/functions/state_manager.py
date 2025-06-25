import json
import os
from typing import Any, Dict


def save_state(state: Dict[str, Any], file_path: str) -> None:
    """
    Saves the LangGraph conversation state to a file in JSON format.

    :param state: The LangGraph state dictionary to save.
    :param file_path: Path to the file where the state will be saved.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=4)


def load_state(file_path: str) -> Dict[str, Any]:
    """
    Loads a LangGraph conversation state from a file.

    :param file_path: Path to the file where the state is stored.
    :return: The loaded LangGraph state dictionary.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"State file not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
