# ADR-005: Âncora temporal “hoje” = 2017-12-31

- **Data**: 2026-10-08
- **Status**: Accepted
- **Deciders**: João Luiz, a partir da EDA §2.3
- **Tags**: scoring, time, data

## Contexto e Problema

Idade do deal = diferença entre “hoje” e `engage_date`. O snapshot do CRM termina em 2017 (máxima `close_date` / `engage_date`). Usar a data de calendário de 2026 faria **todo** deal ter ~9 anos — urgência no piso, badge Esfriando em massa, ranking inútil.

## Decision Drivers

- Idade tem de refletir o mundo do dataset, não o relógio da máquina de quem sobe o app.
- Reprodutibilidade: a mesma entrada produz a mesma idade em qualquer dia.

## Considered Options

- **A — Constante congelada `TODAY = 2017-12-31`**
- **B — `date.today()` do runtime**
- **C — Máxima data por linha (último evento do próprio deal)**

## Por quê

| | Opção | Por quê (resumido) |
|---|--------|-------------------|
| **Tomada** | A — `TODAY = 2017-12-31` | O snapshot acaba nessa data; idade fica igual à EDA e igual em qualquer dia de avaliação. |
| **Não tomada** | B — `date.today()` | Zero constante, mas em 2026 todo deal tem ~9 anos — urgência no piso, ranking inútil. |
| **Não tomada** | C — último evento da linha | Aberto sem `close_date` teria idade 0: o contrário do problema. |

## Decision Outcome

Opção escolhida: **"A"**. Um único âncora global, documentado e testado (LEAD-08). Se o dataset mudar, a constante muda com ele.

### Consequências Positivas

- Idades batem com a EDA (mediana Engaging 165d, nós 57/106).
- Testes não dependem do dia do CI.

### Consequências Negativas

- Valor mágico em código; precisa de comentário + teste.
- Não modela “hoje verdadeiro da empresa” (a EDA admite que isso não existe no snapshot).

## Pros and Cons of the Options

### A ✅ Escolhida

- ✅ Determinístico e alinhado aos dados
- ❌ Constante para lembrar de atualizar

### B — Data real

- ✅ Zero constante
- ❌ Fila inteira “morta” em 2026

### C — Último evento da linha

- ✅ Sem âncora global
- ❌ Aberto sem `close_date` ficaria com idade 0 — o oposto do problema

## Links

- EDA §2.3; PRD §5
- [ADR-001](001-priorizar-por-valor-em-risco.md), [ADR-003](003-idade-nao-exclui-da-fila.md)
