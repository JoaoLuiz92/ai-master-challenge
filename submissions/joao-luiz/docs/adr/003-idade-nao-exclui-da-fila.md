# ADR-003: Idade nunca exclui da fila; Revisar é só dado ruim

- **Data**: 2026-10-08
- **Status**: Accepted
- **Deciders**: João Luiz, a partir da EDA (`docs/analise-exploratoria.md` §4)
- **Tags**: product, scoring, estado

## Contexto e Problema

No briefing, “deals bons esfriam”. A intuição é tirar da fila quem passou do ciclo histórico de Won. Os números do **próprio snapshot** vetam isso:

- Won: mediana 57d, p90 106d, máximo **138d**.
- Engaging abertos: mediana **165d**; 1.301 já têm idade ≥ 138d.

O funil “aberto” é mais velho que qualquer Won da história porque a base **termina** e o deal nunca recebeu `close_date` — artefato de snapshot, não cadáver.

Se Revisar = dado ruim **ou** idade >> ciclo de Won, caem **1.869 / 2.089** (89%) e sobram ~220. A ferramenta morre.

## Decision Drivers

- A fila precisa ter com o que trabalhar na segunda de manhã.
- Idade ainda importa: a EDA mostrou que urgência **reordena** (overlap top-20 vs. só valor = 7/20).
- Prospecting e Engaging sem conta não são trabalháveis (sem join, sem idade).

## Considered Options

- **A — Fila = Engaging com conta; idade só modula urgência e badge “Esfriando” (>106d); Revisar = sem `account` e/ou sem `engage_date`**
- **B — Excluir da fila quem passou do p90/máximo de Won**
- **C — Incluir Prospecting na fila com urgência chutada**

## Por quê

| | Opção | Por quê |
|---|--------|-------------------|
| **Tomada** | A — idade só urgência/badge; Revisar = dado ruim | Mediana Engaging 165d > máx Won 138d: é snapshot, não cadáver. Excluir esvazia 89%. Idade ainda entra na urgência (reordena 7/20). Sem conta/data não dá para trabalhar. |
| **Não tomada** | B — cutoff de idade tira da fila | Fila “limpa” com ~220 deals; a ferramenta some. |
| **Não tomada** | C — Prospecting na fila com urgência chutada | 500 linhas sem `engage_date`: o ranking passaria a inventar número. |

## Decision Outcome

Opção escolhida: **"A"**. ESTADO: Revisar (~1.425) | Focar (top 20% da visão, ADR-007) | Acompanhar (resto). Badge Esfriando não remove.

### Consequências Positivas

- ~664 deals trabalháveis em vez de ~220.
- Deal caro e velho continua visível, só perde urgência (piso > 0).
- Revisar fica honesto: “qualificar conta/dados”, não “arquivo morto”.

### Consequências Negativas

- A fila contém deals de centenas de dias; o vendedor precisa do badge e da urgência para não tratar tudo igual.
- Um leitor pode achar que ignoramos “esfriar”; a EDA §4 é a prova de que excluir esvazia o produto.

## Pros and Cons of the Options

### A ✅ Escolhida

- ✅ Sustentada pelo snapshot; alinhada a “não deixar deal bom sumir”
- ❌ Fila visualmente “velha”

### B — Cutoff de idade como exclusão

- ✅ Fila curta
- ❌ 89% fora; a ferramenta não tem uso

### C — Chutar urgência de Prospecting

- ✅ Ninguém some
- ❌ 500 linhas sem data: número inventado no ranking

## Links

- EDA §4; PRD §5 restrição crítica; CA4, CA5
- [ADR-001](001-priorizar-por-valor-em-risco.md), [ADR-005](005-ancora-temporal-2017-12-31.md), [ADR-007](007-score-percentil-por-visao.md)
