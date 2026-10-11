# ADR-006: Score 100% aritmético; LLM fora do caminho crítico

- **Data**: 2026-10-08
- **Status**: Accepted
- **Deciders**: João Luiz
- **Tags**: scoring, llm, reproducibility

## Contexto e Problema

O motor é aritmética sobre CSV: alias, idade, `sales_price × urgência`, percentil. Um LLM no ranking (motivo gerado, “score inteligente”) adicionaria chave de API, ruído run-a-run e impediria reproduzir a mesma fila. A doc de uso de modelo também reserva LLM para o que o código **não** calcula de forma exata — datas e contas não são esse caso.

## Decision Drivers

- RNF2: mesma entrada, mesma saída; sem chamada externa no caminho crítico.
- Explicação tem de ser auditável (“US$ 4.821 · 40 dias”), não prosa variável.
- Time budget: não há ganho de produto em gerar texto se o template cobre RF3.

## Considered Options

- **A — Pandas/numpy para ingestão e score; textos de motivo/ação parametrizados em código; LLM proibido no ranking**
- **B — LLM gera motivo e/ou ajusta score**
- **C — LLM só na copy, score ainda aritmético**

## Por quê

| | Opção | Por quê (resumido) |
|---|--------|-------------------|
| **Tomada** | A — aritmética + template; LLM fora | O CSV já explica o deal (produto, lista, dias). Mesma entrada → mesma saída (RNF2); CA3 testa texto fixo. LLM só faria sentido em texto que o CSV **não** tem (Lost, nota) — fora do v1. |
| **Não tomada** | B — LLM no score | Demo de IA; o modelo chutaria o que pandas já calcula e a fila deixaria de ser reproduzível. |
| **Não tomada** | C — LLM só na copy | Score intacto, mas o motivo muda a cada run: quebra CA3 e `docker compose up` idêntico. |

## Decision Outcome

Opção escolhida: **"A"**. Uso futuro de modelo, se houver, fica para texto não estruturado (motivo de perda, nota de reunião) — fora do v1.

### Consequências Positivas

- Fila idêntica em qualquer máquina (`docker compose up`).
- Testes 1:1 com ACs (nós 57/106, percentil, aliases).

### Consequências Negativas

- Motivo é template, não narrativa rica.
- Quem espera “IA visível” no ranking precisa ler o ADR-001 (`p̂` testado e descartado) em vez de um LLM.

## Pros and Cons of the Options

### A ✅ Escolhida

- ✅ Determinístico, testável, alinhado a RNF2
- ❌ Copy rígida

### B — LLM no score

- ✅ Demo de IA
- ❌ Não reproduz; vaza o que o CSV já calcula

### C — LLM só no texto

- ✅ Score intacto
- ❌ Motivo muda a cada run; CA3 fica instável

## Links

- PRD §9 Fora de escopo; RNF2
- [ADR-001](001-priorizar-por-valor-em-risco.md), [ADR-002](002-fastapi-react-em-memoria.md)

## Nota posterior (2026-10-11)

A aritmética vigente é `sales_price × CHANCE(idade)` ([ADR-014](014-chance-por-idade-com-censura.md)). LLM continua fora do caminho crítico. Os nós 57/106 deixaram de ser a curva de ranking; o badge Esfriando ainda usa 106d como pista visual.
