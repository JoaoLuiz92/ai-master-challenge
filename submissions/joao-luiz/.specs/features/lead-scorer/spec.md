# Lead Scorer ("Foco da Semana") Specification

## Problem Statement

35 vendedores em escritórios regionais trabalham ~8.800 oportunidades e priorizam "no feeling", gastando tempo em deals que não fecham e deixando oportunidades boas esfriar. Não existe uma visão única de **onde focar hoje**, com o motivo em português e uma ação. Esta feature entrega uma ferramenta FastAPI + React que ordena os deals abertos por **valor em risco** (preço de lista × urgência) e explica cada prioridade, para o vendedor (primário) e o gestor (secundário).

## Goals

- [ ] O vendedor identifica seus ~8 deals prioritários da semana sem ler planilha, cada um com motivo em português e ação sugerida.
- [ ] A fila é ordenada de forma 100% determinística e auditável por PRIORIDADE = VALOR × URGÊNCIA (sem `p̂` no ranking), reproduzível com `docker compose up`.
- [ ] O gestor vê, por vendedor, quanto valor está na fila e quanto está esfriando.
- [ ] Zero deal some em silêncio: toda normalização de dados é logada; nenhum deal é removido por idade.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
| ------- | ------ |
| Probabilidade de conversão / ML no ranking | EDA provou ausência de sinal (AUC temporal 0,478; Spearman 0,999 da fila com/sem `p̂`) — ADR-001. Fica como experimento no process log, não no produto. |
| LLM no caminho crítico | Score é 100% aritmético sobre CSV (ADR-006); chamada externa adicionaria ruído run-a-run e quebraria RNF2. |
| Redistribuição de carteira entre vendedores | Problema de gestor que infla o v1. |
| Login / SSO / RBAC | Dataset público de demonstração; sem autenticação no v1. |
| Persistência / banco / flag "já revisei" | Dados só em memória; o export CSV cobre o durável. |

---

## Assumptions & Open Questions

Every ambiguity is resolved or recorded here - nothing is left silently unclear. As decisões de produto (gray areas) já foram congeladas em `docs/prd.md`, `docs/adr/` (001–007) e `docs/analise-exploratoria.md`; as linhas abaixo registram apenas o que esses documentos deixaram em aberto para a spec resolver.

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| Forma exata da curva de urgência (EDA fixa só os nós 57d e 106d) | Rampa linear 0–57d de 0,5→1,0; platô 1,0 entre 57–106d; decaimento linear após 106d até um piso de 0,35 (atingido em ~212d) e mantido no piso | EDA fixa a mediana (57) e o p90 (106) de Won, mas não a magnitude; o piso > 0 garante que a idade nunca zera o valor (restrição crítica ADR/EDA) e é parametrizável em código | y (frozen via EDA + ADR-001) |
| Definição do percentil do SCORE e empates | SCORE = 100 × (nº de deals da fila na visão com PRIORIDADE ≤ a deste deal) ÷ N; empates compartilham o mesmo percentil; visão com N=1 → SCORE 100 | Determinístico e estável; corresponde a "percentil 0–100 na visão atual" do PRD | y |
| Mapeamento de CONFIANÇA (Alta/Média/Baixa) a partir de min(completude, suporte) | Baixa se falta `account` e/ou `engage_date`; Média se completo mas produto com suporte histórico baixo (fechados < 100, ex.: GTK 500 n=25); Alta caso contrário | EDA sinaliza GTK 500 como suporte frágil sem rebaixar o valor; separa qualidade do dado do tamanho do valor | y |
| Texto da ação sugerida (PRD exige ação, não o texto) | Dentro do ciclo (idade ≤ 106d) → "Avançar proposta"; esfriando (idade > 106d) → "Reengajar antes de esfriar"; Revisar → "Qualificar conta/dados" | PRD/RF3 exige uma ação acionável em português; texto é detalhe de UI parametrizável | y |
| Valor exibido e "valor esperado" do rollup do gestor | VALOR = `sales_price` do catálogo (lista, em USD); rollup soma VALOR dos deals na fila do agente (sem multiplicar por probabilidade) | ADR-001: razão close/lista ≈ 1,0 e `p̂` sem sinal; lista é proxy honesto | y |
| Arredondamento do corte "Focar" (top 20%) | `ceil(0,20 × N)` deals, no mínimo 1 quando a fila da visão é não-vazia | Garante Focar não-vazio em visões pequenas e corte estável | y |
| `metadata.csv` presente em `solution/data/` | Ignorado na ingestão | Não é uma das quatro tabelas modeladas pelo PRD/EDA (accounts, products, sales_teams, sales_pipeline) | y |
| Coluna de preço do catálogo | `products.sales_price` (o PRD/EDA chamam de "preço de lista") | Confirmado no header de `products.csv`; não há coluna `list_price` | y |

**Open questions:** none - all resolved or logged above (required before the spec is confirmed).

---

## User Stories

### P1: Fila priorizada do vendedor ⭐ MVP

**User Story**: As a vendedor, I want ver minha fila de deals abertos ordenada por prioridade com o motivo e a ação, so that eu saiba em segundos onde focar na segunda de manhã.

**Why P1**: É o job-to-be-done primário do produto; sem a fila ordenada e explicada não há ferramenta.

**Acceptance Criteria**:
1. WHEN a vendedor selects their own name THEN the system SHALL display only their open deals whose `deal_stage` is "Engaging" and whose `account` is non-empty, ordered by SCORE descending.
2. The system SHALL exclude every Won, Lost, and Prospecting opportunity from the workable queue.
3. WHEN the queue is ordered by SCORE descending THEN the system SHALL place the deal with the highest PRIORITY (VALOR × URGÊNCIA) in the current view at the top.
4. WHEN a deal is shown in the queue THEN the system SHALL display its product, account, estimated list value, deal stage, days in funnel, SCORE, ESTADO, and CONFIANÇA.
5. WHEN a deal is shown in the queue THEN the system SHALL display a Portuguese business-language reason and a suggested action.

**Independent Test**: Selecionar um vendedor com deals Engaging+conta e verificar que a lista retornada contém só esses deals, ordenada por SCORE desc, cada item com os campos e o motivo/ação.

---

### P1: Motor de priorização valor × urgência

**User Story**: As a produto, I want calcular prioridade como preço de lista × urgência da idade e expor o SCORE como percentil da visão, so that a fila reflita dinheiro em risco de forma determinística.

**Why P1**: É o núcleo de decisão; define a ordem de toda a fila.

**Acceptance Criteria**:
1. The system SHALL compute PRIORITY as VALOR × URGÊNCIA, where VALOR is the product catalog `sales_price` after product-name normalization.
2. The system SHALL compute URGÊNCIA from the deal age against the Won cycle, rising until the Won median (57 days), staying high until the Won p90 (106 days), and decaying afterwards without ever reaching zero.
3. WHEN computing a deal's age THEN the system SHALL anchor "today" to 2017-12-31.
4. The system SHALL compute SCORE as the 0–100 percentile of PRIORITY among the open deals of the current view.
5. The system SHALL NOT include conversion probability (p̂) as a factor in the ranking.

**Independent Test**: Para um conjunto fixo de deals, computar PRIORITY e SCORE e conferir contra valores esperados calculados à mão, incluindo que `p̂` não altera a ordem.

---

### P1: Ingestão e qualidade de dados

**User Story**: As a mantenedor, I want normalizar e logar as correções de dados na ingestão, so that nenhum deal perca preço ou suma em silêncio.

**Why P1**: Sem o alias `GTXPro`, 17% do pipeline (o produto que mais fatura) fica sem preço e some da fila.

**Acceptance Criteria**:
1. WHEN ingesting pipeline rows THEN the system SHALL map the product alias "GTXPro" to "GTX Pro" so that no deal lacks a catalog price after ingestion.
2. WHEN ingesting account rows THEN the system SHALL normalize sector "technolgy" to "technology" and location "Philipines" to "Philippines".
3. WHEN the ingestion applies a normalization THEN the system SHALL log the correction type and the number of affected rows.
4. IF a pipeline product cannot be matched to the catalog after alias normalization THEN the system SHALL set its VALOR to 0 and mark the deal CONFIANÇA as Baixa.
5. WHERE a sales agent has no deals in the pipeline the system SHALL present an explicit empty state instead of listing the agent as a real portfolio.

**Independent Test**: Rodar a ingestão sobre os CSVs reais e verificar o log de correções (1.480 linhas GTXPro, typos de setor/país) e que 0 deals ficam sem preço por causa do alias.

---

### P1: Separação Revisar vs. fila trabalhável

**User Story**: As a vendedor, I want que deals sem conta ou sem data fiquem numa seção Revisar separada, so that a fila ordenada contenha só o que é realmente trabalhável.

**Why P1**: 1.425 abertos sem conta não podem poluir a fila ordenada (CA4).

**Acceptance Criteria**:
1. IF an open deal has no `account` THEN the system SHALL place it in the Revisar state and SHALL exclude it from the ordered queue.
2. IF an open deal has no `engage_date` THEN the system SHALL place it in the Revisar state with CONFIANÇA Baixa and SHALL NOT infer an urgency for it.
3. The system SHALL present the Revisar section separately from the workable queue.

**Independent Test**: Carregar os dados e verificar que os 500 Prospecting e os Engaging sem conta aparecem em Revisar e nunca na fila ordenada.

---

### P1: Estado e badge "Esfriando"

**User Story**: As a vendedor, I want ver o estado do deal (Focar/Acompanhar) e um badge quando ele está esfriando, so that eu saiba a urgência sem nunca perder o deal da fila.

**Why P1**: A restrição crítica (idade não exclui) e o foco no top 20% são centrais ao produto.

**Acceptance Criteria**:
1. WHILE a deal's age exceeds 106 days the system SHALL display an "Esfriando" badge on that deal.
2. The system SHALL never remove a deal from the queue because of its age, and age SHALL only modulate urgency and trigger the badge.
3. WHEN assigning ESTADO THEN the system SHALL mark the top 20% of PRIORITY in the current view as "Focar" and the remaining queue deals as "Acompanhar".
4. The system SHALL compute CONFIANÇA as min(completude, suporte) and map the result to Alta, Média, or Baixa.

**Independent Test**: Com um deal de idade > 106d confirmar que ele tem badge "Esfriando" e permanece na fila; conferir que exatamente `ceil(0,20×N)` deals recebem "Focar".

---

### P1: Filtro e recálculo de percentil por visão

**User Story**: As a usuário, I want filtrar por vendedor/manager/escritório e ter o SCORE recalculado na visão filtrada, so that o percentil sempre reflita o conjunto que estou olhando.

**Why P1**: CA7 exige que trocar meus-deals ↔ time recalcule o percentil.

**Acceptance Criteria**:
1. WHEN the user switches between the "meus deals" and "time" views THEN the system SHALL recompute the SCORE percentile over the deals of the newly selected view.
2. The system SHALL provide filters by sales agent, manager, and regional office.

**Independent Test**: Trocar de meus-deals para time e verificar que o SCORE do mesmo deal muda conforme o conjunto da visão.

---

### P1: Export CSV da visão atual

**User Story**: As a usuário, I want exportar a visão atual em CSV, so that eu tenha o artefato durável da priorização.

**Why P1**: CA9/RF6 — export é o único durável do v1 (sem banco).

**Acceptance Criteria**:
1. WHEN the user exports the current view THEN the system SHALL produce a CSV that reflects exactly the filtered view, with the same deals, same order, and same displayed columns.

**Independent Test**: Exportar uma visão filtrada e comparar o CSV, linha a linha, com o que a UI mostra.

---

### P2: Visão de gestor (rollup do time)

**User Story**: As a gestor, I want alternar para uma visão de rollup por vendedor com os deals bons esfriando, so that eu veja onde o time deixa dinheiro esfriar.

**Why P2**: Importante para o secundário, mas não bloqueia o MVP do vendedor.

**Acceptance Criteria**:
1. WHEN the user switches to the manager role THEN the system SHALL display a team rollup showing, per sales agent, the number of queued deals, the summed expected value, and the number of deals esfriando.
2. The system SHALL highlight "good deals cooling down" per sales agent, defined as a high SCORE combined with the "Esfriando" badge.
3. WHEN the manager filters by a specific agent, manager, or office THEN the system SHALL recompute the rollup and the SCORE percentile over that filtered view.

**Independent Test**: Entrar como gestor, conferir o rollup por vendedor (contagem, valor somado, nº esfriando) e o destaque de deals bons esfriando.

---

### P2: Setup reprodutível (Docker + local)

**User Story**: As a avaliador, I want subir a solução com um comando, so that eu reproduza a ferramenta sem fricção.

**Why P2**: Necessário para a entrega, mas independente da lógica de produto.

**Acceptance Criteria**:
1. WHEN a user runs `docker compose up` THEN the system SHALL start the API and the frontend, and the UI SHALL list real deals from the CSVs.
2. WHERE a local (non-Docker) setup is used the system SHALL start via the two documented local commands.
3. The system SHALL run fully offline and deterministically, producing identical output for identical input with no external calls on the critical path.

**Independent Test**: Rodar `docker compose up` numa máquina limpa e abrir a UI com deals reais; repetir o cálculo e confirmar saída idêntica.

---

## Edge Cases

Edge cases are usually unwanted-behavior (IF/THEN) or boundary (WHEN) criteria:

- IF the current view's workable queue is empty THEN the system SHALL display an empty-state message rather than an error.
- IF a deal's age is exactly 106 days THEN the system SHALL keep urgency at its high plateau and SHALL NOT yet apply the "Esfriando" badge (badge requires age strictly greater than 106).
- IF two deals have identical PRIORITY THEN the system SHALL assign them the same SCORE percentile.
- WHEN the view contains a single workable deal THEN the system SHALL assign it SCORE 100 and ESTADO "Focar".
- IF a product's historical closed count is below the support threshold THEN the system SHALL keep the deal's VALOR unchanged and only lower its CONFIANÇA.

---

## Requirement Traceability

Each requirement gets a unique ID for tracking across design, tasks, and validation.

| Requirement ID | Story | Source (PRD/EDA/ADR) | Phase | Status |
| -------------- | ----- | -------------------- | ----- | ------ |
| LEAD-01 | P1: Fila priorizada | CA1, RF1 | Tasks | Pending |
| LEAD-02 | P1: Fila priorizada | CA1 | Tasks | Pending |
| LEAD-03 | P1: Fila priorizada | CA2 | Tasks | Pending |
| LEAD-04 | P1: Fila priorizada | RF2 | Tasks | Pending |
| LEAD-05 | P1: Fila priorizada | RF3, CA3 | Tasks | Pending |
| LEAD-06 | P1: Motor de priorização | ADR-001, CA2 | Tasks | Pending |
| LEAD-07 | P1: Motor de priorização | EDA §4 | Tasks | Pending |
| LEAD-08 | P1: Motor de priorização | EDA (hoje=2017-12-31) | Tasks | Pending |
| LEAD-09 | P1: Motor de priorização | CA7, RF11 | Tasks | Pending |
| LEAD-10 | P1: Motor de priorização | ADR-001 | Tasks | Pending |
| LEAD-11 | P1: Ingestão e qualidade | CA6 | Tasks | Pending |
| LEAD-12 | P1: Ingestão e qualidade | EDA §2.4 | Tasks | Pending |
| LEAD-13 | P1: Ingestão e qualidade | PRD §6 (log) | Tasks | Pending |
| LEAD-14 | P1: Ingestão e qualidade | EDA §2.1 | Tasks | Pending |
| LEAD-15 | P1: Ingestão e qualidade | EDA §2.5 | Tasks | Pending |
| LEAD-16 | P1: Revisar vs. fila | CA4 | Tasks | Pending |
| LEAD-17 | P1: Revisar vs. fila | CA4 (Prospecting) | Tasks | Pending |
| LEAD-18 | P1: Revisar vs. fila | RF5 | Tasks | Pending |
| LEAD-19 | P1: Estado e badge | CA5, RF4 | Tasks | Pending |
| LEAD-20 | P1: Estado e badge | CA5 | Tasks | Pending |
| LEAD-21 | P1: Estado e badge | PRD §5 (estados) | Tasks | Pending |
| LEAD-22 | P1: Estado e badge | PRD §5 (confiança) | Tasks | Pending |
| LEAD-23 | P1: Filtro e percentil | CA7, RF11 | Tasks | Pending |
| LEAD-24 | P1: Filtro e percentil | RF10 | Tasks | Pending |
| LEAD-25 | P1: Export CSV | RF6, CA9 | Tasks | Pending |
| LEAD-26 | P2: Visão de gestor | RF7, RF8 | Tasks | Pending |
| LEAD-27 | P2: Visão de gestor | RF9 | Tasks | Pending |
| LEAD-28 | P2: Visão de gestor | RF10, RF11 | Tasks | Pending |
| LEAD-29 | P2: Setup reprodutível | CA8, RNF1 | Tasks | Pending |
| LEAD-30 | P2: Setup reprodutível | RNF2 | Tasks | Pending |
| LEAD-31 | Transversal (UI/idioma) | RNF3 | Tasks | Pending |
| LEAD-32 | Transversal (sem persistência) | RNF4 | Execute | Implementing |
| LEAD-33 | P2: Setup reprodutível | RNF1 (fallback local) | Tasks | Pending |

**ID format:** `[CATEGORY]-[NUMBER]` (e.g., `LEAD-01`).

**Status values:** Pending → In Design → In Tasks → Implementing → Verified

**Coverage:** 33 total, all mapped to tasks in `tasks.md`, 0 unmapped.

---

## Success Criteria

How we know the feature is successful:

- [ ] Um vendedor abre a ferramenta e vê ~8 deals prioritários, cada um com motivo em português e ação, em segundos.
- [ ] A fila do vendedor contém apenas Engaging com conta; nenhum Won/Lost/Prospecting aparece como trabalhável (CA1).
- [ ] 0 deals ficam sem preço após a ingestão por causa do alias `GTXPro`→`GTX Pro` (CA6).
- [ ] Nenhum deal é removido por idade; idade > 106d só gera badge (CA5).
- [ ] Trocar o filtro recalcula o percentil do SCORE (CA7) e o export reflete exatamente a visão (CA9).
- [ ] `docker compose up` sobe API + front listando deals reais (CA8), e a saída é determinística (RNF2).
