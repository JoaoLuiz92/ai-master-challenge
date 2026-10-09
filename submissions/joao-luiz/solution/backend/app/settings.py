"""Process settings. Data lives on disk; deals live in memory (RNF4)."""

from dataclasses import dataclass
from pathlib import Path

_SOLUTION_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    data_dir: Path = _SOLUTION_ROOT / "data"


def get_settings() -> Settings:
    return Settings()
