"""Process settings. Data lives on disk; deals live in memory (RNF4)."""

from dataclasses import dataclass
from pathlib import Path

_SOLUTION_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    data_dir: Path = _SOLUTION_ROOT / "data"
    chance_bands: tuple[tuple[int, int], ...] = (
        (0, 29),
        (30, 59),
        (60, 89),
        (90, 10_000),
    )
    # None = derive the wall from the Won cohort at load. Set to pin a value.
    wall_override: int | None = None


def get_settings() -> Settings:
    return Settings()
