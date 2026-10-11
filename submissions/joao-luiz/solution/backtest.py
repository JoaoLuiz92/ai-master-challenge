"""Reproducible backtest: python backtest.py"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

from app.analysis.backtest import run_backtest
from app.ingestion.loader import load_dataset
from app.ingestion.quality import normalize
from app.ingestion.repository import build_deals
from app.settings import get_settings


def main() -> None:
    raw = load_dataset(get_settings().data_dir)
    deals = build_deals(normalize(raw)[0])
    report = run_backtest(deals)
    print("cutoff\tnova\tpreco\taleatorio")
    for row in report.cutoffs:
        print(f"{row.cutoff.isoformat()}\t{row.nova:.0f}\t{row.preco:.0f}\t{row.aleatorio:.0f}")
    print(f"nova_vs_preco_delta\t{report.nova_vs_preco_delta:.0f}")
    print(f"dispersion\t{report.dispersion:.0f}")
    print(f"adopted\t{report.adopted}")
    if not report.adopted:
        print("CHANCE-23: nova nao supera preco; a troca nao entra.")


if __name__ == "__main__":
    main()
