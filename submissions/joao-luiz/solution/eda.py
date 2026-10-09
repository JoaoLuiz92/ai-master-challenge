"""EDA do CRM — caça pega-ratão antes da spec.

Rode a partir de solution/:
    .venv/Scripts/python eda.py
"""

from __future__ import annotations

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DATA = Path(__file__).resolve().parent / "data"
OUT = Path(__file__).resolve().parent.parent / "docs"
OUT.mkdir(exist_ok=True)

PRODUCT_ALIASES = {
    "GTXPro": "GTX Pro",
}

SECTOR_ALIASES = {
    "technolgy": "technology",
}

LOCATION_ALIASES = {
    "Philipines": "Philippines",
}


def hr(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def load() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    accounts = pd.read_csv(DATA / "accounts.csv")
    products = pd.read_csv(DATA / "products.csv")
    teams = pd.read_csv(DATA / "sales_teams.csv")
    pipe = pd.read_csv(DATA / "sales_pipeline.csv")
    return accounts, products, teams, pipe


def main() -> None:
    accounts, products, teams, pipe = load()

    hr("0. SHAPES E COLUNAS")
    for name, df in [
        ("accounts", accounts),
        ("products", products),
        ("sales_teams", teams),
        ("sales_pipeline", pipe),
    ]:
        print(f"\n{name}: {len(df)} linhas, {df.columns.tolist()}")
        print(df.dtypes.to_string())

    hr("1. QUALIDADE CRUA DO PIPELINE")
    print("\nNulos por coluna:")
    print(pipe.isna().sum().to_string())
    print("\nEstágios:")
    print(pipe["deal_stage"].value_counts(dropna=False).to_string())
    print("\nProdutos no pipeline (antes de alias):")
    print(pipe["product"].value_counts(dropna=False).to_string())
    print("\nCatálogo de produtos:")
    print(products.to_string(index=False))

    catalog = set(products["product"])
    pipeline_products = set(pipe["product"].dropna())
    print(f"\nNo pipeline, fora do catálogo: {sorted(pipeline_products - catalog)}")
    print(f"No catálogo, ausentes no pipeline: {sorted(catalog - pipeline_products)}")

    unmatched_product = pipe[~pipe["product"].isin(catalog)]
    print(f"Linhas com produto sem match: {len(unmatched_product)}")

    hr("1b. CONTAS E TIMES")
    print("\nNulos accounts:")
    print(accounts.isna().sum().to_string())
    print("\nSetores (typos):")
    print(accounts["sector"].value_counts(dropna=False).to_string())
    print("\nLocalizações:")
    print(accounts["office_location"].value_counts(dropna=False).to_string())
    print("\nsubsidiary_of preenchido:", accounts["subsidiary_of"].notna().sum())

    acc_names = set(accounts["account"])
    pipe_acc = set(pipe["account"].dropna())
    print(f"\nContas no pipeline sem match: {sorted(pipe_acc - acc_names)[:20]}")
    print(f"N contas pipeline sem match: {len(pipe_acc - acc_names)}")
    print(f"Linhas pipeline sem account:", pipe["account"].isna().sum())
    print(f"Linhas pipeline com account órfã:", pipe["account"].notna().sum() and len(pipe[pipe["account"].notna() & ~pipe["account"].isin(acc_names)]))

    team_names = set(teams["sales_agent"])
    pipe_agents = set(pipe["sales_agent"].dropna())
    print(f"\nAgentes no pipeline sem match: {sorted(pipe_agents - team_names)}")
    print(f"Agentes no time sem deals: {sorted(team_names - pipe_agents)}")
    print(teams["regional_office"].value_counts().to_string())
    print("\nManagers:")
    print(teams.groupby(["regional_office", "manager"]).size().to_string())

    hr("2. DATAS E 'HOJE'")
    pipe["engage_date"] = pd.to_datetime(pipe["engage_date"], errors="coerce")
    pipe["close_date"] = pd.to_datetime(pipe["close_date"], errors="coerce")
    today = max(
        d
        for d in [
            pipe["engage_date"].max(),
            pipe["close_date"].max(),
        ]
        if pd.notna(d)
    )
    print(f"engage_date min/max: {pipe['engage_date'].min()} / {pipe['engage_date'].max()}")
    print(f"close_date min/max:  {pipe['close_date'].min()} / {pipe['close_date'].max()}")
    print(f"HOJE (âncora) = {today.date()}")
    print("\nNulos de data por estágio:")
    print(
        pipe.groupby("deal_stage")
        .agg(
            n=("opportunity_id", "count"),
            engage_nulos=("engage_date", lambda s: s.isna().sum()),
            close_nulos=("close_date", lambda s: s.isna().sum()),
        )
        .to_string()
    )

    hr("3. NORMALIZAÇÃO")
    pipe["product_raw"] = pipe["product"]
    pipe["product"] = pipe["product"].replace(PRODUCT_ALIASES)
    accounts["sector_raw"] = accounts["sector"]
    accounts["sector"] = accounts["sector"].replace(SECTOR_ALIASES)
    accounts["office_location_raw"] = accounts["office_location"]
    accounts["office_location"] = accounts["office_location"].replace(LOCATION_ALIASES)
    n_alias = (pipe["product_raw"] != pipe["product"]).sum()
    print(f"Produtos alias corrigidos: {n_alias}")
    print(f"Setores unique depois: {sorted(accounts['sector'].unique())}")
    print(f"Locations unique depois: {sorted(accounts['office_location'].unique())}")

    hr("4. JOIN COMPLETO")
    df = pipe.merge(products, on="product", how="left")
    df = df.merge(accounts, on="account", how="left")
    df = df.merge(teams, on="sales_agent", how="left")
    df["list_price"] = df["sales_price"]
    df["won"] = df["deal_stage"] == "Won"
    df["lost"] = df["deal_stage"] == "Lost"
    df["open"] = df["deal_stage"].isin(["Prospecting", "Engaging"])
    df["closed"] = df["deal_stage"].isin(["Won", "Lost"])
    df["cycle_days"] = (df["close_date"] - df["engage_date"]).dt.days
    df["age_days"] = np.where(
        df["open"],
        (today - df["engage_date"]).dt.days,
        df["cycle_days"],
    )
    # Prospecting sem engage_date: idade indefinida
    df["has_account"] = df["account"].notna() & df["sector"].notna()
    df["has_price"] = df["list_price"].notna()
    df["has_age"] = df["engage_date"].notna()

    print(f"Após join, list_price nulo: {df['list_price'].isna().sum()}")
    print(f"Após join, sector nulo: {df['sector'].isna().sum()}")
    print(f"Após join, manager nulo: {df['manager'].isna().sum()}")

    hr("5. WIN RATE × RECEITA × VOLUME POR PRODUTO (fechados)")
    closed = df[df["closed"]].copy()
    by_prod = (
        closed.groupby("product")
        .agg(
            n=("opportunity_id", "count"),
            won=("won", "sum"),
            lost=("lost", "sum"),
            revenue=("close_value", lambda s: s[closed.loc[s.index, "won"]].sum() if False else np.nan),
        )
        .reset_index()
    )
    # receita só de Won
    won_rev = closed[closed["won"]].groupby("product")["close_value"].sum()
    list_price = products.set_index("product")["sales_price"]
    by_prod = (
        closed.groupby("product")
        .agg(n=("opportunity_id", "count"), won=("won", "sum"), lost=("lost", "sum"))
        .reset_index()
    )
    by_prod["win_rate"] = by_prod["won"] / (by_prod["won"] + by_prod["lost"])
    by_prod["revenue_won"] = by_prod["product"].map(won_rev).fillna(0)
    by_prod["list_price"] = by_prod["product"].map(list_price)
    by_prod["effort_share"] = by_prod["n"] / by_prod["n"].sum()
    by_prod["revenue_share"] = by_prod["revenue_won"] / by_prod["revenue_won"].sum()
    by_prod["rev_per_deal"] = by_prod["revenue_won"] / by_prod["n"]
    by_prod = by_prod.sort_values("revenue_won", ascending=False)
    print(by_prod.to_string(index=False, float_format=lambda x: f"{x:,.3f}"))
    print(f"\nReceita total Won: {closed.loc[closed['won'], 'close_value'].sum():,.0f}")
    print(f"Win rate geral: {closed['won'].mean():.3f}  n={len(closed)}")

    cheap = ["MG Special", "GTX Basic"]
    cheap_rows = by_prod[by_prod["product"].isin(cheap)]
    print("\nArmadilha barato (MG Special + GTX Basic):")
    print(
        f"  esforço {cheap_rows['effort_share'].sum():.1%}  "
        f"receita {cheap_rows['revenue_share'].sum():.1%}"
    )

    hr("6. SETOR E PORTE DA CONTA (fechados com conta)")
    closed_acc = closed[closed["has_account"]].copy()
    by_sec = (
        closed_acc.groupby("sector")
        .agg(n=("opportunity_id", "count"), won=("won", "sum"), revenue_won=("close_value", lambda s: s[closed_acc.loc[s.index, "won"]].sum()))
    )
    # cleaner
    by_sec = closed_acc.groupby("sector").agg(n=("opportunity_id", "count"), won=("won", "sum"))
    rev_sec = closed_acc[closed_acc["won"]].groupby("sector")["close_value"].sum()
    by_sec["win_rate"] = by_sec["won"] / by_sec["n"]
    by_sec["revenue_won"] = rev_sec
    by_sec["effort_share"] = by_sec["n"] / by_sec["n"].sum()
    by_sec["revenue_share"] = by_sec["revenue_won"] / by_sec["revenue_won"].sum()
    print("\nPor setor:")
    print(by_sec.sort_values("revenue_won", ascending=False).to_string(float_format=lambda x: f"{x:,.3f}"))

    closed_acc["emp_bin"] = pd.qcut(closed_acc["employees"], 4, duplicates="drop")
    closed_acc["rev_bin"] = pd.qcut(closed_acc["revenue"], 4, duplicates="drop")
    print("\nPor quartil de employees:")
    emp = closed_acc.groupby("emp_bin", observed=True).agg(n=("opportunity_id", "count"), win_rate=("won", "mean"))
    print(emp.to_string(float_format=lambda x: f"{x:,.3f}"))
    print("\nPor quartil de revenue da conta:")
    rv = closed_acc.groupby("rev_bin", observed=True).agg(n=("opportunity_id", "count"), win_rate=("won", "mean"))
    print(rv.to_string(float_format=lambda x: f"{x:,.3f}"))

    print("\nFechados SEM conta (não entram em setor/porte):", (~closed["has_account"]).sum())

    hr("7. CICLO DE VIDA (dias engage->close)")
    won = closed[closed["won"] & closed["cycle_days"].notna()]
    lost = closed[closed["lost"] & closed["cycle_days"].notna()]
    print("Won cycle_days:")
    print(won["cycle_days"].describe(percentiles=[0.25, 0.5, 0.75, 0.9, 0.95]).to_string())
    print("\nLost cycle_days:")
    print(lost["cycle_days"].describe(percentiles=[0.25, 0.5, 0.75, 0.9, 0.95]).to_string())
    print(f"\nWon sem engage_date: {closed[closed['won']]['engage_date'].isna().sum()}")
    print(f"Lost sem engage_date: {closed[closed['lost']]['engage_date'].isna().sum()}")
    print(f"Won max cycle: {won['cycle_days'].max()}")
    print(f"Lost max cycle: {lost['cycle_days'].max()}")

    hr("8. ABERTOS — IDADE RELATIVA AO HOJE")
    opened = df[df["open"]].copy()
    print(opened["deal_stage"].value_counts().to_string())
    print(f"\nAbertos sem engage_date (idade indefinida): {opened['engage_date'].isna().sum()}")
    print("  disso, Prospecting:", ((opened["deal_stage"] == "Prospecting") & opened["engage_date"].isna()).sum())
    print("  disso, Engaging:", ((opened["deal_stage"] == "Engaging") & opened["engage_date"].isna()).sum())
    aged = opened[opened["age_days"].notna()]
    print("\nIdade (dias) dos abertos COM engage_date:")
    print(aged["age_days"].describe(percentiles=[0.25, 0.5, 0.75, 0.9, 0.95]).to_string())
    print("\nIdade por estágio:")
    print(aged.groupby("deal_stage")["age_days"].describe(percentiles=[0.5, 0.9]).to_string())

    won_p90 = won["cycle_days"].quantile(0.90)
    won_p95 = won["cycle_days"].quantile(0.95)
    won_max = won["cycle_days"].max()
    print(f"\nWon p90={won_p90:.0f} p95={won_p95:.0f} max={won_max:.0f}")
    for thresh in [won_p90, won_p95, won_max, 200]:
        n = (aged["age_days"] >= thresh).sum()
        print(f"  abertos com idade >= {thresh:.0f}d: {n}")

    print("\nAbertos sem conta:", (~opened["has_account"]).sum())
    print("Abertos sem preço:", (~opened["has_price"]).sum())

    hr("9. DESCONTO close_value vs lista (Won)")
    w = df[df["won"] & df["list_price"].notna()].copy()
    w["ratio"] = w["close_value"] / w["list_price"]
    print(w.groupby("product")["ratio"].describe(percentiles=[0.1, 0.5, 0.9]).to_string())

    hr("10. MODELO p̂ — HOLDOUT TEMPORAL")
    model_df = closed[closed["has_account"] & closed["has_price"]].copy()
    model_df = model_df[model_df["close_date"].notna()]
    model_df["log_emp"] = np.log1p(model_df["employees"])
    model_df["log_rev"] = np.log1p(model_df["revenue"])
    model_df["has_parent"] = model_df["subsidiary_of"].notna().astype(int)
    model_df["y"] = model_df["won"].astype(int)

    cutoff = model_df["close_date"].quantile(0.70)
    train = model_df[model_df["close_date"] <= cutoff]
    test = model_df[model_df["close_date"] > cutoff]
    print(f"Cutoff temporal 70%: {cutoff.date()}  train={len(train)}  test={len(test)}")
    print(f"Win rate train={train['y'].mean():.3f}  test={test['y'].mean():.3f}")

    cat_cols = ["product", "sector"]
    num_cols = ["log_emp", "log_rev", "has_parent"]

    def fit_auc(train_x, test_x, cats, nums) -> tuple[float, Pipeline]:
        pre = ColumnTransformer(
            [
                ("cat", OneHotEncoder(handle_unknown="ignore"), cats),
                ("num", StandardScaler(), nums),
            ]
        )
        clf = Pipeline(
            [
                ("pre", pre),
                (
                    "lr",
                    LogisticRegression(max_iter=1000, class_weight=None),
                ),
            ]
        )
        clf.fit(train_x[cats + nums], train_x["y"])
        proba = clf.predict_proba(test_x[cats + nums])[:, 1]
        auc = roc_auc_score(test_x["y"], proba)
        return auc, clf

    auc_base, clf_base = fit_auc(train, test, cat_cols, num_cols)
    print(f"AUC produto+setor+porte (holdout temporal): {auc_base:.3f}")

    # produto só
    auc_prod, _ = fit_auc(train, test, ["product"], [])
    print(f"AUC só produto: {auc_prod:.3f}")
    auc_sec, _ = fit_auc(train, test, ["sector"], [])
    print(f"AUC só setor: {auc_sec:.3f}")

    # vendedor — para mostrar que NÃO devemos usar
    auc_agent, _ = fit_auc(train, test, ["product", "sector", "sales_agent"], num_cols)
    print(f"AUC + vendedor (proibido no p̂): {auc_agent:.3f}")

    # faixa de p̂ no teste
    p_test = clf_base.predict_proba(test[cat_cols + num_cols])[:, 1]
    print(f"p̂ teste min/mediana/max: {p_test.min():.3f} / {np.median(p_test):.3f} / {p_test.max():.3f}")
    print(f"p̂ teste p10/p90: {np.quantile(p_test, 0.1):.3f} / {np.quantile(p_test, 0.9):.3f}")

    hr("11. PLANO B — Spearman da fila aberta")
    # p̂ no aberto com conta+preço
    scored = opened[opened["has_account"] & opened["has_price"]].copy()
    scored["log_emp"] = np.log1p(scored["employees"].fillna(scored["employees"].median()))
    scored["log_rev"] = np.log1p(scored["revenue"].fillna(scored["revenue"].median()))
    scored["has_parent"] = scored["subsidiary_of"].notna().astype(int)
    scored["p_hat"] = clf_base.predict_proba(scored[cat_cols + num_cols])[:, 1]
    print(f"p̂ abertos min/mediana/max: {scored['p_hat'].min():.3f} / {scored['p_hat'].median():.3f} / {scored['p_hat'].max():.3f}")

    # urgência simples para o teste: pico perto da mediana de Won, decai depois do p90
    med = won["cycle_days"].median()
    p90 = won_p90

    def urgency(age: float) -> float:
        if pd.isna(age):
            return 0.5  # prospecting sem data: neutro, confiança baixa
        if age <= 0:
            return 0.4
        if age <= med:
            return 0.5 + 0.5 * (age / med)
        if age <= p90:
            return 1.0
        # decai até 0.2 depois de 2 * p90
        return float(max(0.2, 1.0 - 0.8 * (age - p90) / max(p90, 1)))

    scored["urgency"] = scored["age_days"].map(urgency)
    scored["ev"] = scored["p_hat"] * scored["list_price"] * scored["urgency"]
    scored["vu"] = scored["list_price"] * scored["urgency"]
    scored["value_only"] = scored["list_price"]

    spear_ev_vu = scored["ev"].corr(scored["vu"], method="spearman")
    spear_ev_val = scored["ev"].corr(scored["value_only"], method="spearman")
    print(f"Spearman EV vs VALOR x URGENCIA: {spear_ev_vu:.3f}")
    print(f"Spearman EV vs so VALOR: {spear_ev_val:.3f}")

    # top 20 overlap
    def top_ids(series, n=20):
        return set(scored.nlargest(n, series)["opportunity_id"])

    t_ev, t_vu, t_val = top_ids("ev"), top_ids("vu"), top_ids("value_only")
    print(f"Overlap top-20 EV ∩ VALOR×URG: {len(t_ev & t_vu)}/20")
    print(f"Overlap top-20 EV ∩ só VALOR: {len(t_ev & t_val)}/20")

    hr("12. WIN RATE POR AGENTE (não entra no p̂, só diagnóstico gestor)")
    agent = (
        closed.groupby("sales_agent")
        .agg(n=("opportunity_id", "count"), win_rate=("won", "mean"))
        .query("n >= 30")
        .sort_values("win_rate", ascending=False)
    )
    print(agent.head(8).to_string(float_format=lambda x: f"{x:,.3f}"))
    print("...")
    print(agent.tail(5).to_string(float_format=lambda x: f"{x:,.3f}"))
    print(f"Win rate agentes n>=30: min={agent['win_rate'].min():.3f} max={agent['win_rate'].max():.3f}")

    hr("13. PROPOSTA DE CORTES (a spec congela depois)")
    # Revisar: sem conta OU sem preço OU (com idade e idade > won_p95)
    revisar_mask = (
        ~opened["has_account"]
        | ~opened["has_price"]
        | (opened["has_age"] & (opened["age_days"] > won_p95))
    )
    print(f"Abertos totais: {len(opened)}")
    print(f"Revisar (sem conta OU sem preço OU idade>p95 Won={won_p95:.0f}d): {revisar_mask.sum()}")
    print(f"  sem conta: {(~opened['has_account']).sum()}")
    print(f"  sem preço: {(~opened['has_price']).sum()}")
    print(f"  idade>p95: {(opened['has_age'] & (opened['age_days'] > won_p95)).sum()}")
    print(f"  Prospecting sem engage (idade indefinida, NÃO vai a Revisar só por isso): {((opened['deal_stage']=='Prospecting') & ~opened['has_age']).sum()}")

    workable = scored.copy()  # tem conta e preço
    workable["revisar_idade"] = workable["has_age"] & (workable["age_days"] > won_p95)
    fila = workable[~workable["revisar_idade"]]
    print(f"Fila trabalhável (conta+preço, idade não zumbi): {len(fila)}")
    # percentis da EV na fila
    for p in [0.80, 0.85, 0.90]:
        print(f"  EV percentil {p:.0%} da fila: {fila['ev'].quantile(p):,.0f}")
    print("Sugestão de trabalho: Focar = top 20% da fila da visão; Acompanhar = resto da fila; Revisar = fora.")

    hr("14. RESUMO EXECUTIVO")
    print(
        f"""
hoje={today.date()}
pipeline={len(df)}  won={df['won'].sum()} lost={df['lost'].sum()} open={df['open'].sum()}
win_rate_closed={closed['won'].mean():.3f}
produto_alias={n_alias}
auc_temporal={auc_base:.3f}  (piso 0.55: {'PASSA' if auc_base > 0.55 else 'FALHA → plano B'})
p_hat_range_open={scored['p_hat'].min():.3f}–{scored['p_hat'].max():.3f}
spearman_ev_vs_vu={spear_ev_vu:.3f}
won_cycle_median={won['cycle_days'].median():.0f}  p90={won_p90:.0f}  p95={won_p95:.0f}  max={won_max:.0f}
"""
    )


if __name__ == "__main__":
    main()
