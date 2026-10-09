# Lead Scorer Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute flow and Critical Rules.** Do not search for skill files by filesystem path. The skill is the source of truth for the full flow (per-task cycle, sub-agent delegation, adequacy review, Verifier, discrimination sensor).

**If the skill cannot be activated, STOP and tell the user - do not proceed without it.**

---

**Design**: `.specs/features/lead-scorer/design.md`
**Status**: Draft

---

## Test Coverage Matrix

> Generated from codebase, project guidelines, and spec - confirm before Execute. Guidelines found: **none** - no existing test suite in the repo (only `solution/eda.py`, an analysis script); strong defaults applied. Provenance: scanned `solution/` (no `pytest.ini`/`pyproject.toml` test config, no `frontend/`), no `AGENTS.md`/`CONTRIBUTING.md` testing section.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| Ingestion / data-access (loader, joins) | integration | Key read/join paths + error handling (missing file, unmatched product) | `backend/tests/integration/*.py` | `.venv\Scripts\python -m pytest backend/tests/integration -q` |
| Domain / scoring (urgency, priority, confidence, cooling) | unit | All branches; 1:1 to spec ACs; every listed edge case has a test | `backend/tests/unit/*.py` | `.venv\Scripts\python -m pytest backend/tests/unit -q` |
| View / query service (filter, percentil, estado, rollup) | unit | All branches; 1:1 to spec ACs; edge cases (N=1, ties, empty view) | `backend/tests/unit/*.py` | `.venv\Scripts\python -m pytest backend/tests/unit -q` |
| API routes (FastAPI) | e2e | All routes in scope: happy path + edge + error | `backend/tests/e2e/*.py` | `.venv\Scripts\python -m pytest backend/tests/e2e -q` |
| React components | unit | Render + behavior per AC (reason/action/badge/estado/empty state) | `frontend/src/**/*.test.tsx` | `npm --prefix frontend test -- --run` |
| User-facing flows (fila, filtros, export vs UI, gestor, empty state, PT labels) | UI e2e (Playwright MCP) | Independent Tests + CA8/CA9/RNF3 against a running UI — not mocked | validation-lane `ui-tester` (no committed Playwright suite) | Playwright MCP: scenarios in `.specs/features/lead-scorer/validation-lane.md` |
| Config / packaging (scaffold, Docker, compose) | none | build gate only | - | build gate only |

## Gate Check Commands

> Generated from codebase - confirm before Execute. Python runs via the project venv `solution\.venv\Scripts\python.exe`; frontend via `npm`.

| Gate Level | When to Use | Command |
| ---------- | ----------- | ------- |
| Quick | After tasks with unit tests only | backend: `.venv\Scripts\python -m pytest backend/tests/unit -q` ; frontend: `npm --prefix frontend test -- --run` |
| Full | After tasks with e2e/integration tests | `.venv\Scripts\python -m pytest backend/tests -q` |
| Build | After phase completion or config/packaging tasks | `.venv\Scripts\python -m pytest backend/tests -q && npm --prefix frontend run build && npm --prefix frontend test -- --run` |
| Validation lane | After the last task (or on "validate") | Orchestrator `.cursor/agents/validation-lane.md`: backend-tester ∥ ui-tester (Playwright MCP) → spec-verifier. See `validation-lane.md`. |

---

## Execution Plan

Phases are ordered and run sequentially - each phase completes before the next begins, and tasks within a phase execute in order. All paths are relative to `solution/`.

### Phase 1: Ingestion & Data Quality

```
T1 → T2 → T3 → T4
```

### Phase 2: Scoring Engine

```
T4 → T5 → T6 → T7
T4 → T8
T5 → T9
```

### Phase 3: View & Query Service

```
T4 → T10
T7 → T11 → T12
T9 → T13
T10 → T14
T11 → T14
T12 → T14
T13 → T14
T14 → T15
```

### Phase 4: API Layer

```
T4 → T16
T14 → T17
T15 → T18
T14 → T19
T3 → T20
```

### Phase 5: Frontend

```
T17 → T21
T21 → T22
T21 → T23
T21 → T24
T18 → T24
T19 → T25
T21 → T25
```

### Phase 6: Packaging & Determinism

```
T25 → T26 → T27
```

---

## Task Breakdown

### T1: Scaffold FastAPI backend app

**What**: Create the backend package skeleton (FastAPI app factory, settings with data dir and frozen constants).
**Where**: `backend/app/main.py`
**Depends on**: None
**Reuses**: `solution/eda.py` load pattern (`pathlib.Path`).
**Requirement**: LEAD-32

**Tools**:

- MCP: `filesystem` (or NONE)
- Skill: NONE

**Done when**:

- [x] FastAPI app factory created with a startup hook placeholder for data load
- [x] Frozen constants module holds TODAY=2017-12-31, WON_MEDIAN=57, WON_P90=106
- [x] App imports cleanly; build gate passes

**Tests**: none
**Gate**: build

---

### T2: CSV loader

**What**: Load the 4 CSVs into pandas DataFrames with a typed `RawDataset`.
**Where**: `backend/app/ingestion/loader.py`
**Depends on**: T1
**Reuses**: `solution/eda.py:46-51` (`load()`).
**Requirement**: nenhum LEAD-* direto (carga dos 4 CSVs). LEAD-08 é a âncora `TODAY` e pertence à T5.

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] `load_dataset(data_dir)` reads accounts, products, sales_teams, sales_pipeline
- [x] Missing/unreadable file raises an explicit startup error (no silent partial load)
- [x] Integration test reads the real CSVs and asserts row counts (8.800 pipeline / 85 / 7 / 35)
- [x] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/integration -q`

**Tests**: integration
**Gate**: full

---

### T3: Data-quality normalization + log

**What**: Apply product/sector/location aliases and emit a quality log of every correction.
**Where**: `backend/app/ingestion/quality.py`
**Depends on**: T2
**Reuses**: `solution/eda.py:27-37` (alias dicts).
**Requirement**: LEAD-11, LEAD-12, LEAD-13

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] `GTXPro`→`GTX Pro`, `technolgy`→`technology`, `Philipines`→`Philippines` applied
- [ ] Each correction logged with type and affected row count (1.480 GTXPro rows logged)
- [ ] Unit tests assert aliases and the log entries (1:1 with ACs LEAD-11/12/13)
- [ ] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick

---

### T4: Build normalized Deal repository

**What**: Join pipeline↔products↔accounts↔teams into in-memory `Deal`s, attach VALOR (sales_price; 0 if unmatched → low confidence flag).
**Where**: `backend/app/ingestion/repository.py`
**Depends on**: T3
**Reuses**: normalized dataset from T3.
**Requirement**: LEAD-14

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Every open deal carries product, account(nullable), stage, engage/close dates, value
- [ ] Product without catalog match after alias → value 0 and low-confidence flag
- [ ] After ingestion, 0 deals lack a price due to the GTXPro alias (asserted)
- [ ] Unit tests cover matched/unmatched value paths
- [ ] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick

---

### T5: Age calculation

**What**: Compute deal age in days from `engage_date` against the frozen TODAY anchor.
**Where**: `backend/app/scoring/age.py`
**Depends on**: T4
**Reuses**: constants from T1.
**Requirement**: LEAD-08, LEAD-17

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] `age_days(engage_date)` returns int for valid dates and `None` when engage_date is missing
- [ ] TODAY anchored to 2017-12-31 (asserted)
- [ ] Unit tests cover valid, missing, and boundary (0 days) cases
- [ ] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick

---

### T6: Urgency curve

**What**: Implement urgency(age): ramp 0–57d (0.5→1.0), plateau 57–106d (1.0), decay >106d to floor 0.35, never zero.
**Where**: `backend/app/scoring/urgency.py`
**Depends on**: T5
**Reuses**: age from T5; EDA knots.
**Requirement**: LEAD-07

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Urgency peaks at 57d, stays 1.0 through 106d, decays after, floored at 0.35
- [ ] `age_days is None` → documented sentinel (deal routed to Revisar, no urgency inferred)
- [ ] Unit tests assert values at 0/57/106/>106 knots and the floor (1:1 with LEAD-07)
- [ ] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick

---

### T7: Priority = value × urgency

**What**: Compute PRIORIDADE as value × urgency; assert p̂ is never a factor.
**Where**: `backend/app/scoring/priority.py`
**Depends on**: T6
**Reuses**: urgency (T6), value (T4).
**Requirement**: LEAD-06, LEAD-10

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] `priority(value, urgency) = value * urgency` (deterministic, no probability input)
- [ ] Unit tests confirm ordering by priority and absence of any p̂ term (LEAD-06/10)
- [ ] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick

---

### T8: Confidence (min completude, suporte)

**What**: Compute CONFIANÇA = min(completude, suporte) → Alta/Média/Baixa.
**Where**: `backend/app/scoring/confidence.py`
**Depends on**: T4
**Reuses**: repo (T4).
**Requirement**: LEAD-22

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Baixa if missing account/engage_date; Média if complete but product support < 100 closed; Alta otherwise
- [ ] Low support lowers confidence but NOT value (asserted for GTK 500)
- [ ] Unit tests cover each level (1:1 with LEAD-22 + edge case)
- [ ] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick

---

### T9: Cooling flag

**What**: Compute the "Esfriando" badge flag (age strictly > 106d) without removing the deal.
**Where**: `backend/app/scoring/cooling.py`
**Depends on**: T5
**Reuses**: age (T5).
**Requirement**: LEAD-19, LEAD-20

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] `cooling(age) == True` iff age > 106; exactly 106 → False
- [ ] Flag never removes a deal from downstream queues (contract documented + asserted)
- [ ] Unit tests cover 106 boundary and >106 (1:1 with LEAD-19/20)
- [ ] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick

---

### T10: View filter + Revisar separation

**What**: Filter deals by view (mine/team, agent/manager/office) and split workable queue vs Revisar.
**Where**: `backend/app/views/filter.py`
**Depends on**: T4
**Reuses**: repo (T4).
**Requirement**: LEAD-16, LEAD-17, LEAD-18, LEAD-24

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Workable = Engaging WITH account; no account and/or no engage_date → Revisar
- [ ] Won/Lost/Prospecting never in the workable queue
- [ ] Filters by agent/manager/office applied correctly
- [ ] Unit tests cover queue vs Revisar routing + each filter (LEAD-16/17/18/24)
- [ ] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick

---

### T11: Percentile SCORE per view

**What**: Compute SCORE 0–100 as the percentile of PRIORIDADE over the current filtered view.
**Where**: `backend/app/views/percentile.py`
**Depends on**: T7
**Reuses**: priority (T7).
**Requirement**: LEAD-09, LEAD-23

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] `percentile_scores(priorities)` returns 0–100; N=1 → 100; ties share the same percentile
- [ ] Recomputed over the passed-in view set (no cached global percentile)
- [ ] Unit tests cover N=1, ties, and view-change recompute (LEAD-09/23)
- [ ] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick

---

### T12: Estado assignment (Focar/Acompanhar)

**What**: Assign ESTADO: top 20% of PRIORIDADE in the view → Focar; rest of queue → Acompanhar.
**Where**: `backend/app/views/estado.py`
**Depends on**: T11
**Reuses**: percentile (T11).
**Requirement**: LEAD-21

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] `ceil(0.20 * N)` deals (≥1 when non-empty) marked Focar; others Acompanhar
- [ ] Single-deal view → that deal is Focar
- [ ] Unit tests cover the 20% cut + single-deal edge case (LEAD-21)
- [ ] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick

---

### T13: Reason + action text (PT)

**What**: Build the Portuguese business-language reason string and suggested action per deal.
**Where**: `backend/app/views/explain.py`
**Depends on**: T9
**Reuses**: scored attributes (value, age, cooling).
**Requirement**: LEAD-05

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Reason format "Produto · US$ valor · N dias no funil · dentro do ciclo|esfriando"
- [ ] Action: ≤106d → "Avançar proposta"; >106d → "Reengajar antes de esfriar"; Revisar → "Qualificar conta/dados"
- [ ] Unit tests cover within-cycle, cooling, and Revisar texts (LEAD-05)
- [ ] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick

---

### T14: Workable queue builder

**What**: Assemble the ordered queue (sort by SCORE desc) composing filter, percentile, estado, and explain.
**Where**: `backend/app/views/query.py`
**Depends on**: T10, T11, T12, T13
**Reuses**: T10–T13.
**Requirement**: LEAD-01, LEAD-02, LEAD-03, LEAD-04

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] `build_queue(repo, view_filter)` returns QueueItems ordered by SCORE desc
- [ ] Highest PRIORIDADE in view is first; each item exposes the LEAD-04 fields
- [ ] Empty view → empty-state result, not error
- [ ] Unit tests cover ordering, field completeness, and empty view (LEAD-01/02/03/04)
- [ ] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick

---

### T15: Manager rollup

**What**: Build the per-agent rollup (queued count, summed expected value, cooling count, good-deals-cooling).
**Where**: `backend/app/views/rollup.py`
**Depends on**: T14
**Reuses**: queue builder (T14).
**Requirement**: LEAD-26, LEAD-27, LEAD-28

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Per agent: queuedCount, expectedValueSum, coolingCount, goodDealsCooling (high SCORE + cooling)
- [ ] Rollup recomputed over the filtered view (LEAD-28)
- [ ] Unit tests cover aggregation + good-deals-cooling highlight (LEAD-26/27/28)
- [ ] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick

---

### T16: GET /api/agents endpoint

**What**: Expose agents/managers/offices with explicit empty state for agents without deals.
**Where**: `backend/app/api/agents.py`
**Depends on**: T4
**Reuses**: repo (T4).
**Requirement**: LEAD-15, LEAD-24

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Endpoint lists agents/managers/offices for the filters
- [ ] 5 agents without deals returned with an explicit empty-state marker, not as real portfolios
- [ ] E2E tests cover listing + empty-state (LEAD-15/24)
- [ ] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/e2e -q`

**Tests**: e2e
**Gate**: full

---

### T17: GET /api/queue endpoint

**What**: Serve the workable queue + Revisar section for the current filtered view.
**Where**: `backend/app/api/queue.py`
**Depends on**: T14
**Reuses**: queue builder (T14).
**Requirement**: LEAD-01, LEAD-04, LEAD-18, LEAD-23

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] `GET /api/queue?view=&agent=&manager=&office=` returns ordered queue + Revisar
- [ ] Switching view recomputes percentile (asserted across two requests)
- [ ] E2E tests cover happy path, Revisar separation, and view switch (LEAD-01/04/18/23)
- [ ] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/e2e -q`

**Tests**: e2e
**Gate**: full

---

### T18: GET /api/rollup endpoint

**What**: Serve the manager rollup for the filtered view.
**Where**: `backend/app/api/rollup.py`
**Depends on**: T15
**Reuses**: rollup service (T15).
**Requirement**: LEAD-26, LEAD-28

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] `GET /api/rollup?manager=&office=` returns per-agent rows
- [ ] Filter recomputes rollup + percentile (LEAD-28)
- [ ] E2E tests cover rollup happy path + filtered recompute (LEAD-26/28)
- [ ] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/e2e -q`

**Tests**: e2e
**Gate**: full

---

### T19: GET /api/export.csv endpoint

**What**: Produce a CSV of the current filtered view (same deals, order, and displayed columns).
**Where**: `backend/app/api/export.py`
**Depends on**: T14
**Reuses**: queue builder (T14).
**Requirement**: LEAD-25

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] CSV rows == queue items of the same filtered view, in the same order and columns
- [ ] E2E test compares CSV payload to the `/api/queue` payload for the same filter (LEAD-25)
- [ ] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/e2e -q`

**Tests**: e2e
**Gate**: full

---

### T20: GET /api/quality-log endpoint

**What**: Expose the ingestion quality log (corrections + affected counts).
**Where**: `backend/app/api/quality_log.py`
**Depends on**: T3
**Reuses**: quality log (T3).
**Requirement**: LEAD-13

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] `GET /api/quality-log` returns each correction with type and affected row count
- [ ] E2E test asserts the GTXPro alias entry is present (LEAD-13)
- [ ] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/e2e -q`

**Tests**: e2e
**Gate**: full

---

### T21: Frontend API client + role/filter state

**What**: React data layer: fetch queue/rollup/agents and hold role + filter state.
**Where**: `frontend/src/api/client.ts`
**Depends on**: T17
**Reuses**: queue endpoint (T17).
**Requirement**: LEAD-24

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Client calls queue/rollup/agents endpoints; role + filter state managed
- [ ] Unit tests (mocked fetch) cover state transitions on filter/role change (LEAD-24)
- [ ] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### T22: QueueList + DealCard components

**What**: Render the ordered queue with per-deal reason, action, Esfriando badge, estado, confiança (PT labels).
**Where**: `frontend/src/components/QueueList.tsx`
**Depends on**: T21
**Reuses**: API client (T21).
**Requirement**: LEAD-04, LEAD-05, LEAD-19, LEAD-31

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Each card shows product, account, value, stage, days, SCORE, estado, confiança, reason, action
- [ ] Esfriando badge rendered when cooling; labels in Portuguese (code/API in English)
- [ ] Component unit tests cover fields, badge, and PT labels (LEAD-04/05/19/31)
- [ ] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### T23: ReviewSection + EmptyState components

**What**: Render the Revisar section separately and the empty state for views/agents without deals.
**Where**: `frontend/src/components/ReviewSection.tsx`
**Depends on**: T21
**Reuses**: API client (T21).
**Requirement**: LEAD-18, LEAD-15

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Revisar shown separate from the workable queue
- [ ] Empty state shown for empty view and ghost agents
- [ ] Component unit tests cover separation + empty state (LEAD-18/15)
- [ ] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### T24: ManagerRollup view component

**What**: Render the manager rollup table with good-deals-cooling highlight.
**Where**: `frontend/src/components/ManagerRollup.tsx`
**Depends on**: T21, T18
**Reuses**: API client (T21), rollup endpoint (T18).
**Requirement**: LEAD-26, LEAD-27

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Per-agent rows (count, expected value, cooling) with good-deals-cooling highlighted
- [ ] Component unit tests cover rendering + highlight (LEAD-26/27)
- [ ] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### T25: ExportButton component

**What**: Trigger CSV download of the current filtered view.
**Where**: `frontend/src/components/ExportButton.tsx`
**Depends on**: T19, T21
**Reuses**: export endpoint (T19), API client (T21).
**Requirement**: LEAD-25

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Button requests `/api/export.csv` with the current filter and downloads it
- [ ] Component unit test asserts the request uses the active filter (LEAD-25)
- [ ] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### T26: Docker + compose + local run

**What**: Dockerfiles for backend/frontend, `docker-compose.yml`, and the two local run commands.
**Where**: `docker-compose.yml`
**Depends on**: T25
**Reuses**: backend app (T1+), frontend build (T22+).
**Requirement**: LEAD-29, LEAD-33

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] `docker compose up` starts API + frontend; UI lists real deals from the CSVs
- [ ] Two documented local commands start the stack without Docker
- [ ] Build gate passes (backend tests + frontend build)
- [ ] Gate check passes: `.venv\Scripts\python -m pytest backend/tests -q && npm --prefix frontend run build && npm --prefix frontend test -- --run`

**Tests**: none
**Gate**: build

---

### T27: Determinism + setup docs

**What**: Add a determinism guard (same input → same output) and the README setup section.
**Where**: `backend/tests/integration/test_determinism.py`
**Depends on**: T26
**Reuses**: full pipeline (T2–T19).
**Requirement**: LEAD-30, LEAD-32

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Running the pipeline twice on identical input yields byte-identical queue output
- [ ] No external calls on the critical path; data only in memory (asserted)
- [ ] README documents Docker + local setup
- [ ] Gate check passes: `.venv\Scripts\python -m pytest backend/tests -q`

**Tests**: integration
**Gate**: full

---

## Task Granularity Check

| Task | Scope | Status |
| ---- | ----- | ------ |
| T1 | 1 app skeleton file | ✅ Granular |
| T2 | 1 loader module | ✅ Granular |
| T3 | 1 normalization module | ✅ Granular |
| T4 | 1 repository module | ✅ Granular |
| T5 | 1 function (age) | ✅ Granular |
| T6 | 1 function (urgency) | ✅ Granular |
| T7 | 1 function (priority) | ✅ Granular |
| T8 | 1 function (confidence) | ✅ Granular |
| T9 | 1 function (cooling) | ✅ Granular |
| T10 | 1 filter module | ✅ Granular |
| T11 | 1 function (percentile) | ✅ Granular |
| T12 | 1 function (estado) | ✅ Granular |
| T13 | 1 module (explain) | ✅ Granular |
| T14 | 1 query builder | ✅ Granular |
| T15 | 1 rollup module | ✅ Granular |
| T16 | 1 endpoint | ✅ Granular |
| T17 | 1 endpoint | ✅ Granular |
| T18 | 1 endpoint | ✅ Granular |
| T19 | 1 endpoint | ✅ Granular |
| T20 | 1 endpoint | ✅ Granular |
| T21 | 1 API client/state | ✅ Granular |
| T22 | 1 component file | ✅ Granular |
| T23 | 1 component file | ✅ Granular |
| T24 | 1 component file | ✅ Granular |
| T25 | 1 component file | ✅ Granular |
| T26 | 1 compose + dockerfiles (packaging unit) | ⚠️ Cohesive packaging |
| T27 | 1 determinism test + docs | ✅ Granular |

---

## Diagram-Definition Cross-Check

| Task | Depends On (task body) | Diagram Shows | Status |
| ---- | ---------------------- | ------------- | ------ |
| T1 | None | None | ✅ Match |
| T2 | T1 | T1→T2 | ✅ Match |
| T3 | T2 | T2→T3 | ✅ Match |
| T4 | T3 | T3→T4 | ✅ Match |
| T5 | T4 | T4→T5 | ✅ Match |
| T6 | T5 | T5→T6 | ✅ Match |
| T7 | T6 | T6→T7 | ✅ Match |
| T8 | T4 | T4→T8 | ✅ Match |
| T9 | T5 | T5→T9 | ✅ Match |
| T10 | T4 | T4→T10 | ✅ Match |
| T11 | T7 | T7→T11 | ✅ Match |
| T12 | T11 | T11→T12 | ✅ Match |
| T13 | T9 | T9→T13 | ✅ Match |
| T14 | T10, T11, T12, T13 | T10→T14, T11→T14, T12→T14, T13→T14 | ✅ Match |
| T15 | T14 | T14→T15 | ✅ Match |
| T16 | T4 | T4→T16 | ✅ Match |
| T17 | T14 | T14→T17 | ✅ Match |
| T18 | T15 | T15→T18 | ✅ Match |
| T19 | T14 | T14→T19 | ✅ Match |
| T20 | T3 | T3→T20 | ✅ Match |
| T21 | T17 | T17→T21 | ✅ Match |
| T22 | T21 | T21→T22 | ✅ Match |
| T23 | T21 | T21→T23 | ✅ Match |
| T24 | T21, T18 | T21→T24, T18→T24 | ✅ Match |
| T25 | T19, T21 | T19→T25, T21→T25 | ✅ Match |
| T26 | T25 | T25→T26 | ✅ Match |
| T27 | T26 | T26→T27 | ✅ Match |

All dependencies point backward or within the same phase. No forward-phase dependency.

---

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
| ---- | --------------------------- | --------------- | --------- | ------ |
| T1 | Config / scaffold | none | none | ✅ OK |
| T2 | Ingestion / data-access | integration | integration | ✅ OK |
| T3 | Ingestion (pure normalize) | unit | unit | ✅ OK |
| T4 | Ingestion (repo/join) | unit | unit | ✅ OK |
| T5 | Domain / scoring | unit | unit | ✅ OK |
| T6 | Domain / scoring | unit | unit | ✅ OK |
| T7 | Domain / scoring | unit | unit | ✅ OK |
| T8 | Domain / scoring | unit | unit | ✅ OK |
| T9 | Domain / scoring | unit | unit | ✅ OK |
| T10 | View / query | unit | unit | ✅ OK |
| T11 | View / query | unit | unit | ✅ OK |
| T12 | View / query | unit | unit | ✅ OK |
| T13 | View / query | unit | unit | ✅ OK |
| T14 | View / query | unit | unit | ✅ OK |
| T15 | View / query | unit | unit | ✅ OK |
| T16 | API route | e2e | e2e | ✅ OK |
| T17 | API route | e2e | e2e | ✅ OK |
| T18 | API route | e2e | e2e | ✅ OK |
| T19 | API route | e2e | e2e | ✅ OK |
| T20 | API route | e2e | e2e | ✅ OK |
| T21 | React component/state | unit | unit | ✅ OK |
| T22 | React component | unit | unit | ✅ OK |
| T23 | React component | unit | unit | ✅ OK |
| T24 | React component | unit | unit | ✅ OK |
| T25 | React component | unit | unit | ✅ OK |
| T26 | Packaging / config | none | none | ✅ OK |
| T27 | Integration (determinism) | integration | integration | ✅ OK |

No violations: every task's `Tests` field matches its code layer's required test type in the Test Coverage Matrix.

The Playwright MCP row is a **feature-level** gate (validation-lane `ui-tester`), not a per-task `Tests` field. T21–T25 still own component unit tests; T26 Independent Test (UI lists real deals) is exercised in that lane after packaging.

---

## Tools (MCPs and Skills)

Execute tasks use the `filesystem` MCP and the project venv / `npm` for gates. Product critical path stays offline (RNF2).

**Validation lane (after last task):** Playwright MCP for UI Independent Tests (`ui-tester`). Enable the Cursor Playwright plugin or approve `.cursor/mcp.json` (`npx -y @playwright/mcp@latest`). Backend gates stay pytest. See `.specs/features/lead-scorer/validation-lane.md`.
