# ADR-014: Priorizar por valor × chance de fechar por idade (tábua com censura)

- **Data**: 2026-10-11
- **Status**: Accepted
- **Deciders**: João Luiz, a partir da EDA e do backtest (`python backtest.py`)
- **Tags**: scoring, survival, product
- **Supersedes**: [ADR-001](001-priorizar-por-valor-em-risco.md)

## Contexto e Problema

A ADR-001 ordenava por `sales_price × urgência(idade)` com um piso que **mantinha o deal velho na fila de trabalho**. A Head pediu para parar de gastar tempo em deal que não fecha. A EDA já mostrava que a chance de fechar cai com a idade e que nenhum Won converteu depois da idade máxima observada (a parede).

Urgência com piso trata o deal parado como trabalho. A chance, contada com os ainda abertos (censura), trata o deal além da parede como chance 0.

## Decision Drivers

- A curva tem de ser auditável (sem ML no ranking, ADR-006).
- Sem censura, só entram fechados e a chance **cresce** com a idade (viés de sobrevivência).
- A parede não é um literal: é a maior idade de um Won na coorte, parametrizável em config.

## Considered Options

- **A — PRIORIDADE = lista × CHANCE(idade)**; CHANCE = Won ÷ deals da faixa, censurados como não-Won; 0 acima da parede
- **B — Manter lista × urgência com piso** (ADR-001)
- **C — Classificador de conversão no ranking**

## Por quê

| | Opção | Por quê |
|---|--------|-------------------|
| **Tomada** | A — valor × chance com censura | A chance declina com a idade; acima da parede é 0. Degraus em config. Backtest é o gate (ADR-016). |
| **Não tomada** | B — urgência com piso | O piso sustenta deal morto no topo da fila de trabalho. |
| **Não tomada** | C — ML no ranking | Sem sinal (AUC 0,478) e fora de RNF2. |

## Decision Outcome

Opção escolhida: **A**. Faixas padrão: 0–29, 30–59, 60–89, 90+. Parede derivada no load (`derive_wall`); `Settings.wall_override` pina o valor se preciso. `p̂` continua fora do ranking.

### Consequências Positivas

- Fila de trabalho ordenada por valor esperado de fechar, não por urgência com piso.
- Números da frase de chance vêm da tábua, não de literal.

### Consequências Negativas

- A maior parte do Engaging aberto do snapshot cai além da parede (efeito de corte da base) — isso vira decisão (ADR-015), não some do produto.

## Links

- [ADR-001](001-priorizar-por-valor-em-risco.md) (texto original intacto), [ADR-015](015-fila-decidir-alem-da-parede.md), [ADR-016](016-backtest-como-gate-do-motor.md)
- Spec `.specs/features/chance-por-idade/spec.md`
