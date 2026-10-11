# ADR-016: Backtest sem leakage é o gate de adoção do motor novo

- **Data**: 2026-10-11
- **Status**: Accepted
- **Deciders**: João Luiz
- **Tags**: scoring, verification, backtest

## Contexto e Problema

Trocar urgência por chance é opinião até provar que a **nova ordem captura mais receita** que ordenar só por preço. Sem o gate, a feature entra por narrativa.

## Decision Drivers

- Sem olhar o futuro: cada corte só usa o que era conhecido naquela data.
- Comparar contra o baseline trivial (preço) e contra aleatório.
- Se a nova ordem não bater o preço, **não adotar**.

## Considered Options

- **A — Backtest em ≥3 cortes: receita Won nos 90 dias seguintes no top‑N por vendedor; adota se mediana(nova − preço) > 0**
- **B — Adotar a chance sem evidência de captura**
- **C — Holdout de classificador (AUC) como gate**

## Por quê

| | Opção | Por quê |
|---|--------|-------------------|
| **Tomada** | A — captura vs. preço, sem leakage | É a pergunta de negócio: a fila pega mais receita fechada depois? |
| **Não tomada** | B — adotar no feeling | CHANCE-23 exige revert se não bater. |
| **Não tomada** | C — AUC | Já falhou (0,478); não mede a fila. |

## Decision Outcome

Opção escolhida: **A**. Comando: `python backtest.py` a partir de `solution/`. Cortes padrão: 2017-06-30, 2017-08-31, 2017-09-30. `adopted=true` só se a mediana dos deltas nova−preço for positiva. O motor v3 entra porque o script emite essa adoção; se um rerun virar `adopted=false`, a troca reverte para ADR-001.

### Consequências Positivas

- A fórmula não entra sem evidência reproduzível offline.

### Consequências Negativas

- O backtest é pesado (lê o CSV inteiro em cada corte). Não entra no caminho crítico da API.

## Links

- `solution/backtest.py`, `solution/backend/app/analysis/backtest.py`
- [ADR-014](014-chance-por-idade-com-censura.md)
