# Chance por idade — a fila separa esforço de decisão (`chance-por-idade`) Specification

> **Supersessão.** Esta feature substitui o eixo de ordenação definido em ADR-001/003 (`PRIORIDADE = VALOR × URGÊNCIA`, com piso 0,35 e idade que "só modula, nunca exclui"). O motor passa a ordenar por `VALOR × CHANCE(idade)`, onde `CHANCE` é uma curva de sobrevivência que chega a zero na idade além da qual nenhum deal fechado da base converteu. Os critérios LEAD-07, LEAD-19 e LEAD-20 são reescritos pelos CHANCE-* abaixo. A UI, a ingestão, o export, os filtros e o rollup do gestor permanecem; muda o que entra na fila de trabalho e o que vai para uma fila de decisão.

## Problem Statement

A Head de RevOps pediu que o vendedor pare de gastar tempo em deal que não fecha. A EDA do pipeline mostra que a probabilidade de fechamento **cai com a idade do deal** e zera a partir de uma parede observada nos dados: nenhum deal fechado converteu depois dessa idade. O motor atual não usa essa curva — ordena por `VALOR × URGÊNCIA` com um piso que mantém o deal velho na fila de trabalho, só marcado como "Esfriando". Resultado: a maior parte do pipeline aberto além da parede continua na fila do vendedor como trabalho, quando deveria ser decisão do gestor (requalificar ou encerrar).

Esta feature troca a urgência com piso por uma **chance de fechar por idade**, calculada contando também os deals que seguem abertos (censura), e separa o pipeline em duas filas: **Trabalhar** (ainda pode fechar) e **Decidir** (parado além da parede). O achado de negócio — o volume e o valor parados além da parede — passa a ser a primeira leitura do gestor, com evidência em backtest de que a nova ordem captura mais receita que ordenar por preço.

## Goals

- [ ] O motor calcula `CHANCE(idade)` a partir de uma curva de sobrevivência sobre o ciclo de fechamento, contando como censurados os deals ainda abertos, de modo que a chance decline com a idade e seja 0 além da parede (maior idade de deal fechado na coorte).
- [ ] `PRIORIDADE = sales_price × CHANCE(idade)` substitui `VALOR × URGÊNCIA`; sem piso que sustente deal parado no topo.
- [ ] A fila de trabalho (Trabalhar) contém só deals Engaging com conta e idade ≤ parede; o deal além da parede sai da fila de trabalho e entra na fila **Decidir**, ordenada por valor, para requalificar ou encerrar.
- [ ] Cada deal traz, em português, a chance e a frase da parede ("Nenhum deal da base fechou depois de N dias; M abertos já passaram disso").
- [ ] Um backtest reconstrói a fila em cortes passados sem olhar o futuro e prova que a nova ordem captura mais receita no top‑N que ordenar só por preço; se não bater o baseline, a mudança não entra.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
| ------- | ------ |
| Modelo de ML / classificador de conversão no ranking | A chance vem de uma tábua de sobrevivência por idade (determinística e auditável), não de um modelo treinado. Qualquer classificador fica, no máximo, como experimento no process log. |
| LLM no caminho crítico | O score continua 100% aritmético sobre CSV; nenhuma chamada externa entra no cálculo (mantém RNF2). |
| Fatores de vendedor, setor, conta, região no score | Fora desta feature. A chance é função só da idade; outros sinais não entram sem passar pelo mesmo backtest. |
| Persistência da decisão (encerrar/requalificar) em banco ou disco | Dados só em memória; a decisão na fila Decidir vive na sessão, como o repasse (ADR-013). O durável é o export CSV. |
| Mudança no repasse, no login ou na ingestão | O repasse (ADR-013) e a ingestão (LEAD-11..15) seguem iguais; esta feature só muda a fórmula, as filas e os textos. |
| Nova curva por produto ou por segmento | A parede e a curva são globais da coorte nesta versão; recalibrar por produto fica para a v2 (registrado em Limitações). |

---

## Assumptions & Open Questions

Every ambiguity is resolved or recorded here - nothing is left silently unclear.

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| Como contar a chance por idade | Tábua de sobrevivência: para cada faixa de idade, fração dos deals que **chegaram àquela idade** e terminaram em Won, contando os que seguem abertos como censurados (não-Won) | Sem a censura, a chance cresce com a idade (viés de sobrevivência): só deals já fechados entrariam na conta e o deal velho pareceria bom | y (EDA) |
| A "parede" (idade de chance 0) | Maior idade de um deal **fechado** (Won) na coorte; derivada dos dados, parametrizável em `config` | É a leitura honesta de "até quando a base mostra fechamento"; não é um número mágico no código | y (EDA) |
| Faixas da curva | Degraus por faixa de idade (ex.: 0–29, 30–59, 60–89, 90–parede, > parede), calculados na coorte de fechados + censurados | Degraus são explicáveis ao vendedor ("47% até 29 dias") e estáveis com a amostra desta base | y |
| Coorte da curva | Deals com desfecho ou abertura dentro do pipeline, âncora `TODAY = 2017-12-31` (igual ao motor atual) | Mantém a âncora temporal já decidida; a curva é recalculada sobre a mesma base | y |
| O que vai para Decidir | Engaging, com conta, idade > parede (CHANCE = 0) | É o pipeline parado que a Head quer tirar da frente do vendedor; continua sendo trabalho de decisão do gestor | y |
| Ordem da fila Decidir | Preço de lista desc | O gestor encerra/requalifica primeiro o que vale mais; não há chance para ordenar | y |
| Deal exatamente na parede | Trabalhável (usa a chance da última faixa com fechamento); só **acima** da parede vai para Decidir | Fronteira explícita, igual ao tratamento de borda já usado no badge | y |
| Prospecting e deal sem conta/sem `engage_date` | Continuam em **Revisar** (LEAD-16/17), fora de Trabalhar e de Decidir | Sem data não há idade; sem conta não é trabalhável. Inalterado. | y |
| Gate de aceite do novo motor | Backtest em ≥ 3 cortes passados: receita capturada no top‑N por vendedor nos 90 dias seguintes, nova ordem vs. "só preço" e vs. aleatório | A troca de motor só se justifica se a fila capturar mais receita que o baseline trivial; senão, reverte | y |

**Open questions:** none - all resolved or logged above.

---

## User Stories

### P1: Chance de fechar por idade (curva de sobrevivência) ⭐ núcleo

**User Story**: As a produto, I want calcular a chance de fechar como função da idade do deal, contando os deals ainda abertos, so that a fila reflita a probabilidade real de conversão e não uma urgência com piso.

**Why P1**: É o novo núcleo de decisão; define a ordem de toda a fila e a parede que separa Trabalhar de Decidir.

**Acceptance Criteria**:
1. The system SHALL compute `CHANCE(idade)` from a survival table where, for each age band, the value is the fraction of deals that reached that age and ended as Won, counting still-open deals as censored (non-Won).
2. WHEN a deal's age exceeds the wall (the maximum age at which any closed deal in the cohort was Won) THEN the system SHALL set its `CHANCE` to 0.
3. The system SHALL derive the wall from the data at load time and expose it as a configurable parameter, not a hard-coded literal in business logic.
4. WHEN computing a deal's age THEN the system SHALL anchor "today" to 2017-12-31.
5. The system SHALL compute `CHANCE` deterministically, producing identical values for identical input with no external calls.

**Independent Test**: Para uma coorte fixa, computar a tábua por faixa à mão (com censura) e conferir que `CHANCE` bate por faixa, que é monotônica não-crescente após o pico e que vale 0 acima da parede.

---

### P1: Prioridade por valor × chance (substitui urgência)

**User Story**: As a produto, I want ordenar a fila por preço de lista × chance de fechar, so that o topo seja o deal com mais valor esperado de conversão, não o mais caro parado.

**Why P1**: Substitui `VALOR × URGÊNCIA` (ADR-001) e remove o piso que mantinha deal morto no topo.

**Acceptance Criteria**:
1. The system SHALL compute `PRIORIDADE = sales_price × CHANCE(idade)`, where `sales_price` is the normalized catalog price.
2. The system SHALL NOT apply a non-zero floor to the age factor; a deal past the wall SHALL have `PRIORIDADE = 0`.
3. The system SHALL compute `SCORE` as the 0–100 percentile of `PRIORIDADE` among the workable deals of the current view.
4. The system SHALL NOT include any trained conversion model in the ranking.
5. WHERE the previous engine used `URGÊNCIA` with floor 0,35 the system SHALL no longer reference it in the ranking path.

**Independent Test**: Com um conjunto fixo de deals, conferir que a ordem muda em relação a `VALOR × URGÊNCIA` nos deals velhos (caem), que o deal além da parede recebe PRIORIDADE 0 e que o SCORE é o percentil na visão.

---

### P1: Fila Decidir separada da fila de trabalho

**User Story**: As a vendedor, I want que os deals parados além da parede saiam da minha fila de trabalho e fiquem numa fila Decidir, so that eu só trabalhe o que ainda pode fechar.

**Why P1**: É a resposta direta ao pedido da Head (parar de gastar tempo em deal que não fecha).

**Acceptance Criteria**:
1. IF an open deal is Engaging, has an account, and its age exceeds the wall THEN the system SHALL place it in the "Decidir" queue and SHALL exclude it from the "Trabalhar" queue.
2. The system SHALL order the "Decidir" queue by list price descending.
3. The system SHALL keep Prospecting deals and deals without account or without `engage_date` in "Revisar", separate from both "Trabalhar" and "Decidir".
4. The system SHALL present "Trabalhar", "Decidir" and "Revisar" as three distinct sections, each with its own count and summed value.
5. WHEN a deal's age is at or below the wall THEN the system SHALL keep it in "Trabalhar" ordered by SCORE descending.

**Independent Test**: Carregar os dados e verificar que os Engaging com conta e idade > parede aparecem só em Decidir (por preço desc), os ≤ parede só em Trabalhar (por SCORE desc) e os sem conta/data só em Revisar.

---

### P1: Explicação da chance e da parede em português

**User Story**: As a vendedor, I want ver a chance do deal e por que ele está em Decidir, so that eu entenda a priorização sem jargão.

**Why P1**: Explainability é o critério explícito do challenge ("o vendedor entende por quê").

**Acceptance Criteria**:
1. WHEN a workable deal is shown THEN the system SHALL display its chance of closing in plain Portuguese (e.g., "47% dos deals desta idade fecharam").
2. WHEN a deal is in "Decidir" THEN the system SHALL display the wall sentence stating the wall age and how many open deals are past it (e.g., "Nenhum deal da base fechou depois de N dias; M abertos já passaram disso").
3. The system SHALL present, for each deal, a suggested action consistent with its queue: advance for "Trabalhar", requalify-or-close for "Decidir", fix-data for "Revisar".
4. The system SHALL compute every number in these sentences from the data, with no fabricated value.

**Independent Test**: Abrir um deal de cada fila e conferir que a frase da chance (Trabalhar), a frase da parede (Decidir) e a ação batem com os números calculados.

---

### P1: Backtest como gate do novo motor

**User Story**: As a mantenedor, I want um backtest que prove que a nova ordem captura mais receita que ordenar por preço, so that a troca de motor seja justificada por evidência e não por intuição.

**Why P1**: Sem o gate, a mudança de fórmula é opinião; o challenge valoriza verificação.

**Acceptance Criteria**:
1. The system SHALL provide a backtest script that, for at least three past cut-off dates, reconstructs each view using only data known at that date (no future leakage).
2. WHEN running the backtest THEN the system SHALL measure the share of the next-90-days won revenue captured by the top‑N deals per sales agent, for the new ranking, for "price only", and for random.
3. The backtest SHALL report the new ranking's capture against the "price only" baseline with a dispersion measure across the cut-offs.
4. IF the new ranking does not exceed the "price only" baseline on captured revenue THEN the change SHALL NOT be adopted (documented decision).
5. The backtest SHALL be reproducible offline with a single documented command.

**Independent Test**: Rodar o backtest e conferir que ele emite, por corte, a receita capturada das três ordens e o comparativo nova ordem vs. preço, sem usar nenhum campo posterior ao corte.

---

### P2: Rollup do gestor reflete Trabalhar e Decidir

**User Story**: As a gestor, I want ver, por vendedor, o valor em Trabalhar e o valor parado em Decidir, so that eu ataque primeiro a limpeza do pipeline.

**Why P2**: Importante para o secundário; não bloqueia o MVP do vendedor.

**Acceptance Criteria**:
1. WHEN the manager view is shown THEN the system SHALL display, per sales agent, the count and summed value of "Trabalhar" and of "Decidir" separately.
2. The system SHALL highlight the total value parked in "Decidir" as the primary cleanup figure.
3. WHEN the manager filters by agent, manager, or office THEN the system SHALL recompute both rollups and the SCORE percentile over that view.

**Independent Test**: Entrar como gestor e conferir que o rollup separa valor em Trabalhar de valor em Decidir por vendedor e destaca o total parado.

---

### P2: Export e filtros refletem as duas filas

**User Story**: As a usuário, I want exportar e filtrar vendo as filas Trabalhar e Decidir, so that o artefato durável traga a separação.

**Why P2**: Mantém a paridade export/UI (CA9) com o novo modelo de filas.

**Acceptance Criteria**:
1. WHEN the user exports the current view THEN the CSV SHALL reflect exactly the filtered view, including the queue (Trabalhar/Decidir/Revisar) of each deal, in the same order shown.
2. WHEN the user switches views THEN the system SHALL recompute the SCORE percentile over the workable deals of the new view.

**Independent Test**: Exportar uma visão filtrada e comparar o CSV, linha a linha, com a UI, conferindo a coluna de fila.

---

## Edge Cases

- IF an age band in the cohort has no Won deal THEN the system SHALL set `CHANCE` to 0 for that band.
- IF a deal's age is exactly the wall THEN the system SHALL keep it in "Trabalhar" using the last non-zero band's chance.
- IF the "Trabalhar" queue of the current view is empty but "Decidir" is not THEN the system SHALL show the decision list with an explicit empty-state for work, not an error.
- IF two deals have identical `PRIORIDADE` THEN the system SHALL assign them the same SCORE percentile.
- WHEN a view contains a single workable deal THEN the system SHALL assign it SCORE 100.
- IF a product's historical closed count is below the support threshold THEN the system SHALL still compute `CHANCE` from age and only lower CONFIANÇA (support is confidence, not chance).
- IF every workable deal in a view is past the wall THEN the system SHALL render that agent's work queue as empty and route all deals to "Decidir".

---

## Requirement Traceability

| Requirement ID | Story | Source | Phase | Status |
| -------------- | ----- | ------ | ----- | ------ |
| CHANCE-01 | P1: Chance por idade | EDA (curva de sobrevivência) | Spec | Implementing |
| CHANCE-02 | P1: Chance por idade | EDA (parede) | Spec | Verified |
| CHANCE-03 | P1: Chance por idade | config parametrizável | Spec | Implementing |
| CHANCE-04 | P1: Chance por idade | âncora 2017-12-31 | Spec | Verified |
| CHANCE-05 | P1: Chance por idade | RNF2 (determinismo) | Spec | Verified |
| CHANCE-06 | P1: Valor × chance | supersede ADR-001 | Spec | Verified |
| CHANCE-07 | P1: Valor × chance | remove piso (ADR-003) | Spec | Verified |
| CHANCE-08 | P1: Valor × chance | SCORE percentil da visão | Spec | Verified |
| CHANCE-09 | P1: Valor × chance | sem ML no ranking | Spec | Verified |
| CHANCE-10 | P1: Valor × chance | supersede LEAD-07 | Spec | Verified |
| CHANCE-11 | P1: Fila Decidir | pedido da Head | Spec | Verified |
| CHANCE-12 | P1: Fila Decidir | ordem por preço | Spec | Verified |
| CHANCE-13 | P1: Fila Decidir | mantém Revisar (LEAD-16/17) | Spec | Verified |
| CHANCE-14 | P1: Fila Decidir | três seções | Spec | Verified |
| CHANCE-15 | P1: Fila Decidir | supersede LEAD-19/20 | Spec | Verified |
| CHANCE-16 | P1: Explicação | RF3 (motivo/ação) | Spec | Verified |
| CHANCE-17 | P1: Explicação | frase da parede | Spec | Verified |
| CHANCE-18 | P1: Explicação | ação por fila | Spec | Verified |
| CHANCE-19 | P1: Explicação | sem número fabricado | Spec | Verified |
| CHANCE-20 | P1: Backtest gate | verificação | Spec | Verified |
| CHANCE-21 | P1: Backtest gate | receita top‑N | Spec | Verified |
| CHANCE-22 | P1: Backtest gate | baseline preço | Spec | Verified |
| CHANCE-23 | P1: Backtest gate | reverter se não bater | Spec | Implementing |
| CHANCE-24 | P1: Backtest gate | reprodutível offline | Spec | Verified |
| CHANCE-25 | P2: Rollup gestor | RF7/RF8 | Spec | Verified |
| CHANCE-26 | P2: Rollup gestor | destaque parado | Spec | Verified |
| CHANCE-27 | P2: Rollup gestor | recálculo por visão | Spec | Verified |
| CHANCE-28 | P2: Export/filtros | CA9 | Spec | Pending |
| CHANCE-29 | P2: Export/filtros | percentil por visão | Spec | Verified |

**ID format:** `CHANCE-[NUMBER]`.

**Status values:** Pending → In Design → In Tasks → Implementing → Verified

**Coverage:** 29 total, 14 mapped (CHANCE-02/04/05/06/07/09 Verified; CHANCE-01/03/10/11/12/13/14/17 Implementing).

---

## Success Criteria

How we know the feature is successful:

- [ ] A chance por idade é calculada com censura e vale 0 acima da parede derivada dos dados (CHANCE-01/02).
- [ ] A fila ordena por `VALOR × CHANCE`; o deal além da parede tem PRIORIDADE 0 e sai da fila de trabalho (CHANCE-06/07).
- [ ] Trabalhar, Decidir e Revisar são três seções distintas, cada uma com contagem e valor (CHANCE-11/14).
- [ ] Cada deal traz a chance (Trabalhar) ou a frase da parede (Decidir) em português, com números do dado (CHANCE-16/17/19).
- [ ] O backtest prova, em ≥ 3 cortes, que a nova ordem captura mais receita no top‑N que ordenar por preço; caso contrário, a troca não é adotada (CHANCE-20..23).
- [ ] O gestor vê, por vendedor, o valor parado em Decidir como figura principal de limpeza (CHANCE-25/26).
- [ ] `docker compose up` sobe a solução com as duas filas e saída determinística (RNF1/RNF2 preservados).

---

## Supersession & migration notes

- **ADR a criar:** ADR-014 (chance por idade com censura), ADR-015 (fila Decidir separada), ADR-016 (backtest como gate do motor). Os ADR-001 e ADR-003 passam a `Superseded by ADR-014/015`, com o texto original preservado.
- **Critérios reescritos:** LEAD-07 (urgência) → CHANCE-01/06; LEAD-19/20 (idade só modula, nunca exclui) → CHANCE-02/11/15. Atualizar o status desses LEAD-* para `Superseded` em `lead-scorer/spec.md` quando esta feature entrar em Tasks.
- **O que não muda:** ingestão e normalização (LEAD-11..15), Revisar (LEAD-16/17), export (LEAD-25), âncora temporal, repasse (ADR-013), ausência de banco/login. A UI ganha a seção Decidir e troca o texto de urgência pela chance; o chrome das estações permanece.
- **Docs a atualizar junto do Execute:** `README.md` (Executive Summary, lógica do score, limitações), `docs/evolucao-do-score.md` (v3) e `docs/analise-exploratoria.md` (seção da curva de sobrevivência e da parede).
