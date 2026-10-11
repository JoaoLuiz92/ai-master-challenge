# Chance por idade — Design

**Spec**: `.specs/features/chance-por-idade/spec.md`
**Status**: Draft

---

## Architecture Overview

A feature troca o eixo de ordenação do motor existente **sem mudar a arquitetura de duas camadas** (FastAPI em memória + React). Entra um estágio novo na ingestão/score: a partir dos deals já normalizados (T4 do `lead-scorer`), o motor materializa **uma tábua de sobrevivência por idade** — contando os deals ainda abertos como censurados — e deriva a **parede** (maior idade com fechamento). `CHANCE(idade)` substitui `URGÊNCIA(idade)`, e `PRIORIDADE = sales_price × CHANCE`. A camada de query ganha uma terceira cesta: a fila de trabalho (**Trabalhar**, ≤ parede, por SCORE) e a fila de decisão (**Decidir**, > parede, por preço). Revisar segue igual. Um script de **backtest** reconstrói a fila em cortes passados e é o gate que autoriza (ou barra) a troca de motor.

Decisão central (ADR-014): a chance é **determinística e derivada do dado** (tábua por faixa + censura), não um modelo treinado; a parede é um parâmetro lido dos dados no startup, não um literal no código.

```mermaid
graph TD
    REPO[(In-memory DealRepository<br/>lead-scorer T4)] --> COHORT[Cohort Builder<br/>fechados + censurados]
    COHORT --> SURV[Survival Table<br/>chance por faixa de idade]
    SURV --> WALL[Wall deriver<br/>maior idade com Won]
    SURV --> CHANCE[chance(idade)]
    WALL --> CHANCE
    CHANCE --> PRIO[priority = value x chance]
    PRIO --> QUERY[View/Query Service]
    WALL --> BUCKETS[Bucketizer<br/>Trabalhar / Decidir / Revisar]
    QUERY --> BUCKETS
    BUCKETS --> API[FastAPI Routers]
    API --> UI[React App]
    UI --> WORK[QueueList Trabalhar]
    UI --> DECIDE[DecidirSection]
    UI --> ROLLUP[ManagerRollup: Trabalhar vs Decidir]
    REPO --> BT[Backtest script<br/>cortes passados, sem leakage]
    BT --> GATE{captura > preço?}
```

Fluxo de uma requisição: `GET /api/queue?...` → Query Service filtra os deals da visão → o Bucketizer separa Trabalhar (idade ≤ parede) de Decidir (idade > parede) e de Revisar → Trabalhar ordena por SCORE (percentil de `value × chance`), Decidir por preço → serializa com a frase da chance ou da parede em português.

---

## Code Reuse Analysis

### Existing Components to Leverage

| Component | Location | How to Use |
| --------- | -------- | ---------- |
| `DealRepository` normalizado (deals com idade, valor, conta) | `backend/app/ingestion/repository.py` (lead-scorer T4) | Fonte da coorte; não re-ingerir CSV. |
| `age_days()` | `backend/app/scoring/age.py` (T5) | Idade por deal e por faixa; reutilizado sem alteração. |
| `priority()` | `backend/app/scoring/priority.py` (T7) | **Reescrito**: passa de `value × urgency` para `value × chance`. |
| `urgency()` | `backend/app/scoring/urgency.py` (T6) | **Aposentado** do caminho de ranking; mantido só como referência histórica (v2). |
| `cooling()` | `backend/app/scoring/cooling.py` (T9) | Reaproveitado para o badge visual dentro de Trabalhar; não decide mais a cesta. |
| `ViewQueryService` (filter, percentile, estado) | `backend/app/views/` (T10–T14) | Estendido com o Bucketizer; percentil continua sobre os deals **de Trabalhar** da visão. |
| `explain.py` (reason/action PT) | `backend/app/views/explain.py` (T13) | Estendido com a frase da chance e a frase da parede. |
| `manager_rollup()` | `backend/app/views/rollup.py` (T15) | Estendido para somar valor de Trabalhar e de Decidir separados. |
| Constantes congeladas / âncora `TODAY` | `backend/app/main.py` settings (T1) | A âncora 2017-12-31 é a mesma; a parede entra como constante derivada. |
| `pandas`/`numpy` no `.venv` | `solution/.venv` | Tábua de sobrevivência vetorizada e backtest. |

### Integration Points

| System | Integration Method |
| ------ | ------------------ |
| Coorte ↔ Repositório | A tábua é construída uma vez no startup, a partir do `DealRepository` já carregado (mesmo lifespan do lead-scorer). |
| Chance ↔ Query | `chance(idade)` é atributo independente de visão (como era a urgência); o percentil continua por visão. |
| Backtest ↔ Dados | Script offline lê os mesmos CSVs e reconstrói cortes por data; não usa a API nem campos posteriores ao corte. |
| Frontend ↔ Backend | Mesma REST; a seção Decidir é mais um bloco no payload de `/api/queue`. |

---

## Components

### CohortBuilder

- **Purpose**: Montar a coorte para a tábua: deals fechados (Won/Lost) e deals ainda abertos como censurados, por faixa de idade.
- **Location**: `backend/app/scoring/cohort.py`
- **Interfaces**:
  - `build_cohort(repo, today=date(2017,12,31)) -> Cohort` — para cada deal, idade e desfecho (won / censored).
- **Dependencies**: repo (T4), `age_days` (T5).
- **Reuses**: repositório normalizado.

### SurvivalChanceEngine (pure, deterministic)

- **Purpose**: Calcular a tábua de sobrevivência por faixa (fração de Won entre os que chegaram à faixa, com censura) e expor `chance(idade)`; derivar a parede.
- **Location**: `backend/app/scoring/chance.py`
- **Interfaces**:
  - `survival_table(cohort, bands) -> dict[Band, float]` — chance por faixa.
  - `derive_wall(cohort) -> int` — maior idade de um Won na coorte.
  - `chance(age_days: int | None, table, wall) -> float` — chance da faixa; `0` acima da parede; `None`→sentinela (Revisar).
- **Dependencies**: numpy; coorte (CohortBuilder).
- **Reuses**: parâmetros de faixa em config.

### Priority (reescrito)

- **Purpose**: `PRIORIDADE = value × chance`.
- **Location**: `backend/app/scoring/priority.py`
- **Interfaces**:
  - `priority(value: float, chance: float) -> float` — `value * chance`; deal acima da parede → `0`.
- **Dependencies**: chance (SurvivalChanceEngine), value (T4).
- **Reuses**: assinatura antiga, trocando o segundo fator.

### Bucketizer

- **Purpose**: Separar a visão em Trabalhar (Engaging, conta, idade ≤ parede), Decidir (Engaging, conta, idade > parede) e Revisar (sem conta/sem data, Prospecting).
- **Location**: `backend/app/views/buckets.py`
- **Interfaces**:
  - `bucketize(scored_deals, wall) -> Buckets` — três listas, cada uma com contagem e soma de valor.
  - `order_trabalhar(deals) -> list` — por SCORE desc. `order_decidir(deals) -> list` — por preço desc.
- **Dependencies**: percentile/estado (T11/T12), wall.
- **Reuses**: filtro de visão (T10).

### ViewQueryService (estendido)

- **Purpose**: Montar a resposta da visão com as três cestas; percentil e estado sobre **Trabalhar**.
- **Location**: `backend/app/views/query.py`
- **Interfaces**:
  - `build_view(repo, view_filter) -> ViewResult` — { trabalhar, decidir, revisar, rollupHints }.
- **Dependencies**: Bucketizer, percentile, explain.
- **Reuses**: query builder existente.

### Explain (estendido)

- **Purpose**: Frases em português da chance (Trabalhar) e da parede (Decidir), e a ação por cesta.
- **Location**: `backend/app/views/explain.py`
- **Interfaces**:
  - `chance_sentence(scored) -> str` — ex.: "47% dos deals desta idade fecharam."
  - `wall_sentence(wall, past_count) -> str` — ex.: "Nenhum deal da base fechou depois de 138 dias; 1.291 abertos já passaram disso."
  - `action_for(bucket) -> str` — avançar / requalificar-ou-encerrar / qualificar dados.
- **Dependencies**: chance, wall.
- **Reuses**: reason/action existentes.

### BacktestRunner

- **Purpose**: Reconstruir a fila em ≥ 3 cortes passados e medir a receita capturada no top‑N por vendedor nos 90 dias seguintes, para a nova ordem, "só preço" e aleatório.
- **Location**: `solution/backtest.py` (script) + `backend/app/analysis/backtest.py` (lógica)
- **Interfaces**:
  - `run_backtest(cutoffs: list[date], top_n: int) -> BacktestReport` — captura por corte e comparativo.
- **Dependencies**: CohortBuilder, SurvivalChanceEngine (recalibrada em cada corte só com o passado).
- **Reuses**: motor de chance; nenhum campo posterior ao corte.

### API / React (estendidos)

- **Api**: `/api/queue` passa a retornar `trabalhar`, `decidir`, `revisar`; `/api/rollup` soma Trabalhar e Decidir por agente. `backend/app/api/queue.py`, `rollup.py`.
- **React**: `DecidirSection.tsx` (lista por preço + frase da parede), `DealCard` mostra a chance, `ManagerRollup` destaca o valor parado. `frontend/src/components/`.

---

## Data Models

### Cohort / SurvivalTable

```typescript
interface CohortEntry {
  ageDays: number
  outcome: 'won' | 'censored'   // censored = ainda aberto na âncora
}

interface SurvivalTable {
  bands: { maxAge: number; chance: number }[]  // chance = Won / (chegaram à faixa), com censura
  wall: number                                  // maior idade com Won na coorte
  pastWallOpenCount: number                     // quantos abertos > wall (frase da parede)
}
```

### ScoredDeal (atributos de visão-independente — revisto)

```typescript
interface ScoredDeal {
  deal: Deal
  value: number            // sales_price do catálogo (0 se sem match)
  ageDays: number | null
  chance: number           // [0 .. ~0.47]; 0 acima da parede  (substitui urgency)
  priority: number         // value * chance
  confidence: 'Alta' | 'Media' | 'Baixa'
  pastWall: boolean        // ageDays > wall  (roteia para Decidir)
  cooling: boolean         // badge visual dentro de Trabalhar
}
```

### ViewResult (dependente da visão)

```typescript
interface ViewResult {
  trabalhar: QueueItem[]   // idade <= wall, ordenado por SCORE desc
  decidir: DecideItem[]    // idade > wall, ordenado por preço desc
  revisar: Deal[]          // sem conta / sem engage_date / Prospecting
  totals: { trabalharValue: number; decidirValue: number; counts: Record<string, number> }
}

interface DecideItem {
  scored: ScoredDeal
  wallSentence: string     // PT
  action: 'Requalificar ou encerrar'
}
```

### RollupRow (revisto)

```typescript
interface RollupRow {
  salesAgent: string
  trabalharCount: number
  trabalharValue: number
  decidirCount: number
  decidirValue: number     // valor parado — figura principal de limpeza
}
```

### BacktestReport

```typescript
interface BacktestReport {
  cutoffs: string[]
  capture: { ranking: 'nova' | 'preco' | 'aleatorio'; perCutoff: number[]; median: number }[]
  novaVsPreco: { delta: number; dispersion: number }   // adotar só se delta > 0
}
```

---

## Error Handling Strategy

| Error Scenario | Handling | User Impact |
| -------------- | -------- | ----------- |
| Faixa de idade sem nenhum Won na coorte | `chance = 0` naquela faixa | Deal da faixa cai para o fim/Decidir, sem erro (edge case). |
| Deal exatamente na parede | Trabalhável (chance da última faixa com Won) | Fica em Trabalhar; só acima da parede vai para Decidir. |
| Visão com Trabalhar vazio mas Decidir cheio | Empty-state de trabalho + lista de decisão | Mensagem "nada a trabalhar; N deals a decidir", não erro. |
| Deal sem `engage_date` | Sem idade → Revisar, sem chance inferida | Inalterado (LEAD-17). |
| Produto sem suporte histórico | Chance ainda calculada pela idade; CONFIANÇA baixa | Suporte é confiança, não chance (edge case). |
| Backtest pedido com corte sem desfecho nos 90 dias | Corte reportado com captura indefinida e excluído da mediana, com aviso | Report honesto, sem número inventado. |

---

## Risks & Concerns

| Concern | Location (file:line) | Impact | Mitigation |
| ------- | -------------------- | ------ | ---------- |
| Esquecer a censura ao montar a tábua (só contar fechados) | `backend/app/scoring/cohort.py` | Chance cresce com a idade (viés de sobrevivência); fila volta a premiar deal velho | Teste CHANCE-01: tábua com e sem censura difere; a curva com censura é não-crescente após o pico. |
| Parede como literal no código | `backend/app/scoring/chance.py` | Número mágico quebra se a base muda | Derivar `wall` no startup e expor em config (CHANCE-03). |
| Percentil calculado sobre as três cestas por engano | `backend/app/views/query.py` | SCORE distorcido ao misturar Decidir | Percentil só sobre Trabalhar da visão; teste CHANCE-08. |
| Backtest com vazamento (usar desfecho posterior ao corte) | `backend/app/analysis/backtest.py` | Resultado otimista e inválido | Recalibrar a tábua só com o passado de cada corte; teste assegura nenhum campo > corte. |
| Textos antigos de urgência deixados na UI/README | `README.md`, `docs/evolucao-do-score.md` | Documento contradiz o motor | Docs na lista de atualização do Execute (supersession notes da spec). |
| Deal parado some da conta do gestor | `backend/app/views/rollup.py` | Gestor perde a figura de limpeza | Rollup soma Decidir explicitamente (CHANCE-25/26). |

> Nenhum concern de segurança novo — superfície continua leitura de CSV local, sem auth/entrada externa.

---

## Tech Decisions (only non-obvious ones)

| Decision | Choice | Rationale |
| -------- | ------ | --------- |
| Origem da chance | Tábua de sobrevivência por faixa, com censura | Determinística, explicável por faixa e honesta com deal aberto; evita classificador frágil. |
| Parede | Derivada do dado (maior idade com Won) | "Até quando a base mostra fechamento" é fato, não hiperparâmetro. |
| Onde o deal parado vai | Fila Decidir separada, por preço | Responde ao pedido da Head (tirar do vendedor); preço ordena a limpeza do gestor. |
| Piso da chance | Sem piso (0 acima da parede) | O piso 0,35 era o que mantinha deal morto no topo; removê-lo é o ponto da feature. |
| Gate da troca | Backtest vs. "só preço" | Trocar o motor só se a nova ordem capturar mais receita; senão, não adota (CHANCE-23). |
| Urgência antiga | Aposentada do ranking, preservada como referência | Mantém a rastreabilidade da evolução sem duplicar caminho de decisão. |

> **Project-level decisions:** a registrar em `.specs/STATE.md` `## Decisions` (AD-008..) e em `docs/adr/` (ADR-014 chance por idade; ADR-015 fila Decidir; ADR-016 backtest como gate). ADR-001/003 passam a `Superseded`.
