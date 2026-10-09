# ADR-002: Stack FastAPI + React com dados em memória, sem login nem banco

- **Data**: 2026-10-08
- **Status**: Accepted
- **Deciders**: João Luiz
- **Tags**: architecture, stack, persistence

## Contexto e Problema

O challenge exige software que o vendedor **abra e use**, não um notebook. Time budget 4–6h, dataset público de demonstração (~8.800 linhas), avaliador precisa reproduzir com um comando. Persistência, auth e BI macro não resolvem o job da segunda de manhã.

## Decision Drivers

- Precisa **rodar** com dados reais (critério do challenge).
- Reproduzível: `docker compose up` e fallback local.
- Escopo v1: priorizar a fila, não operar um CRM.

## Considered Options

- **A — FastAPI + React, CSVs carregados uma vez em memória, sem login/banco; durável = export CSV**
- **B — Streamlit / Dash** (um processo, UI mais rápida de prototipar)
- **C — API + banco + login** (formato “produto”)

## Por quê

| | Opção | Por quê  |
|---|--------|-------------------|
| **Tomada** | A — FastAPI + React em memória | O challenge pede app que roda, não notebook; API testável à parte; sem auth/banco o v1 cabe em 4–6h; o durável é o export CSV. |
| **Não tomada** | B — Streamlit / Dash | Sobe mais rápido, mas mistura score e UI — pytest/e2e da API e UI Playwright ficam piores. |
| **Não tomada** | C — banco + login | Parece produto; não resolve “onde focar hoje” e come o time budget. |

## Decision Outcome

Opção escolhida: **"A"**. Backend calcula score determinístico sobre pandas; frontend escolhe papel/filtro e renderiza. Sem SSO, sem flag “já revisei”, sem Redistribuição de carteira.

### Consequências Positivas

- Um comando sobe API + UI; avaliador vê deals reais.
- Superfície mínima: leitura de CSV local, sem segredos.
- Separação API em inglês / rótulos PT na borda da UI (ADR-004).

### Consequências Negativas

- Recarregar o processo perde qualquer estado de sessão.
- Dois processos (API + front) em vez de um app Streamlit.

## Pros and Cons of the Options

### A — FastAPI + React em memória ✅ Escolhida

- ✅ Atende CA8/RNF1/RNF4; código mantível por outro dev
- ❌ Sem histórico server-side

### B — Streamlit / Dash

- ✅ Menos arquivos no time budget
- ❌ Mistura cálculo e UI; mais difícil de testar a API à parte

### C — Banco + login

- ✅ Parece produto
- ❌ Auth e schema não agregam ao v1; atrasam a fila

## Links

- PRD §4, §9; RNF1–RNF4
- [ADR-001](001-priorizar-por-valor-em-risco.md), [ADR-004](004-ui-portugues-codigo-ingles.md)
