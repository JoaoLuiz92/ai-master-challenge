"""Load the four CRM CSVs into memory. No aliasing or joins."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

REQUIRED_CSVS = (
    "accounts.csv",
    "products.csv",
    "sales_teams.csv",
    "sales_pipeline.csv",
)


class DatasetLoadError(Exception):
    """Raised when a required CRM CSV is missing or unreadable."""


@dataclass(frozen=True)
class RawDataset:
    accounts: pd.DataFrame
    products: pd.DataFrame
    sales_teams: pd.DataFrame
    sales_pipeline: pd.DataFrame


def load_dataset(data_dir: Path) -> RawDataset:
    data_dir = Path(data_dir)
    paths = {name: data_dir / name for name in REQUIRED_CSVS}
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing:
        raise DatasetLoadError(
            "Required CRM CSV missing or not a file: " + ", ".join(missing)
        )

    frames: dict[str, pd.DataFrame] = {}
    for name, path in paths.items():
        try:
            frames[name] = pd.read_csv(path)
        except (OSError, ValueError, UnicodeError, pd.errors.ParserError) as exc:
            raise DatasetLoadError(f"Required CRM CSV unreadable: {name}") from exc

    return RawDataset(
        accounts=frames["accounts.csv"],
        products=frames["products.csv"],
        sales_teams=frames["sales_teams.csv"],
        sales_pipeline=frames["sales_pipeline.csv"],
    )
