import os
from pathlib import Path

# Add parent directory to path, allows us to import the "project.py" file from the parent directory
# From: https://stackoverflow.com/a/30536516/13885200

from como import project


def test_config():
    configs = project.Config()
    current_dir = Path(__file__).parent

    assert configs.data_dir == current_dir / "data"
    assert configs.config_dir == current_dir / "data" / "config_sheets"
    assert configs.result_dir == current_dir / "data" / "results"
    assert configs.code_dir == current_dir / "como"
