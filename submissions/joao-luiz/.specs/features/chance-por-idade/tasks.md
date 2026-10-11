# Chance por idade — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute flow and Critical Rules.** Do not search for skill files by filesystem path. The skill is the source of truth for the full flow (per-task cycle, sub-agent delegation, adequacy review, Verifier, discrimination sensor).

**If the skill cannot be activated, STOP and tell the user - do not proceed without it.**

---

**Design**: `.specs/features/chance-por-idade/design.md`
**Status**: In Progress

---

## Test Coverage Matrix

> Generated from codebase, project guidelines, and spec - confirm before Execute. Existing suite: backend pytest (`backend/tests/**`) and frontend vitest (`frontend/src/**/*.test.tsx`) from the `lead-scorer` feature. Reuse those locations and run commands. Provenance: `solution/pytest.ini`, `backend/tests/{unit,integration,e2e}`, `frontend` vitest config.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| Cohort / survival (cohort, chance table, wall) | unit | All branches; censoring path; wall derivation; 1:1 to spec ACs | `backend/tests/unit/*.py` | `.venv\Scripts\python -m pytest backend/tests/unit -q` |
| Domain / scoring (priority = value × chance) | unit | Ordering; past-wall → 0; no ML term | `backend/tests/unit/*.py` | `.venv\Scripts\python -m pytest backend/tests/unit -q` |
| View / query (bucketize Trabalhar/Decidir/Revisar, percentil on Trabalhar) | unit | All branches; edge cases (empty Trabalhar, all past wall, ties) | `backend/tests/unit/*.py` | `.venv\Scripts\python -m pytest backend/tests/unit -q` |
| Explain (chance sentence, wall sentence, action per bucket) | unit | Each bucket text; numbers from data | `backend/tests/unit/*.py` | `.venv\Scripts\python -m pytest backend/tests/unit -q` |
| Backtest (no-leakage reconstruction, capture vs baselines) | integration | Leakage guard; capture per cutoff; nova vs preço comparison | `backend/tests/integration/*.py` | `.venv\Scripts\python -m pytest backend/tests/integration -q` |
| API routes (queue with 3 buckets, rollup Trabalhar vs Decidir) | e2e | Happy path + edge + error | `backend/tests/e2e/*.py` | `.venv\Scripts\python -m pytest backend/tests/e2e -q` |
| React components (DecidirSection, DealCard chance, ManagerRollup parked value) | unit | Render + behavior per AC | `frontend/src/**/*.test.tsx` | `npm --prefix frontend test -- --run` |
| User-facing flows (Trabalhar vs Decidir, chance/wall text, rollup parked) | UI e2e (Playwright MCP) | Independent Tests against a running UI — not mocked | validation-lane `ui-tester` | Playwright MCP, one scenario per UI Independent Test in `spec.md` |

## Gate Check Commands

> Python runs via the project venv `solution\.venv\Scripts\python.exe`; frontend via `npm`. On Windows hosts with the pandas block, run backend tests inside the image as documented in the lead-scorer feature.

| Gate Level | When to Use | Command |
| ---------- | ----------- | ------- |
| Quick | After tasks with unit tests only | backend: `.venv\Scripts\python -m pytest backend/tests/unit -q` ; frontend: `npm --prefix frontend test -- --run` |
| Full | After tasks with e2e/integration tests | `.venv\Scripts\python -m pytest backend/tests -q` |
| Build | After phase completion or config/packaging tasks | `.venv\Scripts\python -m pytest backend/tests -q && npm --prefix frontend run build && npm --prefix frontend test -- --run` |
| Validation lane | After the last task (or on "validate") | Harness orchestrator `.cursor/agents/validation-lane.md`: backend-tester ∥ ui-tester (Playwright MCP) → spec-verifier. Rule: `.cursor/rules/validation-lane.mdc`. |

---

## Execution Plan

Phases are ordered and run sequentially - each phase completes before the next begins, and tasks within a phase execute in order. All paths are relative to `solution/`.

### Phase 1: Survival chance engine

```
C1 → C2 → C3
C1 → C4
```

### Phase 2: Priority & buckets

```
C3 → C5
C3 → C6
C5 → C7
C6 → C7
```

### Phase 3: Explain & backtest

```
C3 → C8
C7 → C8
C4 → C9
```

### Phase 4: API & rollup

```
C7 → C10
C10 → C11
```

### Phase 5: Frontend

```
C10 → C12
C12 → C13
C11 → C14
```

### Phase 6: Docs, config & supersession

```
C9 → C15
C14 → C15
C15 → C16
```

---

## Task Breakdown

### C1: Cohort builder (closed + censored)

**What**: Build the cohort from the in-memory repository: each deal with its age and outcome, counting still-open deals as censored.
**Where**: `backend/app/scoring/cohort.py`
**Depends on**: lead-scorer T4 (repository), T5 (age)
**Reuses**: `ingestion/repository.py`, `scoring/age.py`
**Requirement**: CHANCE-01, CHANCE-04

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] `build_cohort(repo, today)` returns, per deal, age and outcome (won | censored)
- [x] Still-open deals are tagged `censored`, not dropped
- [x] TODAY anchored to 2017-12-31 (asserted)
- [x] Unit tests cover won/censored tagging and the anchor
- [x] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick

---

### C2: Survival table with censoring

**What**: Compute `chance` per age band = Won ÷ (deals that reached the band), counting censored as non-Won.
**Where**: `backend/app/scoring/chance.py`
**Depends on**: C1
**Reuses**: cohort (C1); band config.
**Requirement**: CHANCE-01, CHANCE-03

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] `survival_table(cohort, bands)` returns a chance per band
- [x] A cohort without censoring yields a different (increasing) curve — asserted to prove censoring matters
- [x] The censored curve is non-increasing after its peak
- [x] Bands are read from config, not hard-coded in logic
- [x] Unit tests cover the censoring contrast and monotonicity (CHANCE-01)
- [x] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick

---

### C3: Chance(age) + wall derivation

**What**: Derive the wall (max age with a Won) and expose `chance(age)`: band chance; 0 above the wall; sentinel for missing age.
**Where**: `backend/app/scoring/chance.py`
**Depends on**: C2
**Reuses**: survival table (C2).
**Requirement**: CHANCE-02, CHANCE-03, CHANCE-05

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] `derive_wall(cohort)` returns the max age at which any Won occurred
- [x] `chance(age)` returns 0 for age > wall; the last band's chance at age == wall
- [x] `age is None` → documented sentinel (routes to Revisar; no chance)
- [x] Deterministic: identical input → identical table/wall (asserted)
- [x] Wall exposed as a configurable constant derived at load time
- [x] Unit tests cover wall boundary, above-wall zero, and None (CHANCE-02/03/05)
- [x] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick

---

### C4: Past-wall open count (wall sentence input)

**What**: Compute how many open deals are past the wall (the number used in the wall sentence).
**Where**: `backend/app/scoring/chance.py`
**Depends on**: C1
**Reuses**: cohort (C1).
**Requirement**: CHANCE-17

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] `past_wall_open_count(repo, wall)` returns the count of open deals with age > wall
- [x] Unit test asserts the count against a fixed fixture (CHANCE-17)
- [x] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick

---

### C5: Priority = value × chance (rewrite)

**What**: Rewrite `priority()` to `value × chance`; past-wall deal → priority 0; remove the urgency floor from the ranking path.
**Where**: `backend/app/scoring/priority.py`
**Depends on**: C3
**Reuses**: existing `priority.py` signature.
**Requirement**: CHANCE-06, CHANCE-07, CHANCE-09, CHANCE-10

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] `priority(value, chance) = value * chance` (deterministic, no probability-model term)
- [x] Deal above the wall → priority 0 (asserted)
- [x] No reference to `urgency` remains in the ranking path
- [x] Unit tests confirm new ordering and past-wall zero (CHANCE-06/07/09/10)
- [x] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick

---

### C6: Bucketizer (Trabalhar / Decidir / Revisar)

**What**: Split the filtered view into Trabalhar (Engaging, account, age ≤ wall), Decidir (Engaging, account, age > wall), Revisar (no account/no date, Prospecting).
**Where**: `backend/app/views/buckets.py`
**Depends on**: C3
**Reuses**: view filter (lead-scorer T10).
**Requirement**: CHANCE-11, CHANCE-12, CHANCE-13, CHANCE-14

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] Engaging+account+age>wall → Decidir; ≤wall → Trabalhar; no account/date & Prospecting → Revisar
- [x] Decidir ordered by list price desc; Revisar unchanged
- [x] Each bucket carries its count and summed value
- [x] Unit tests cover routing, Decidir order, and three-way split (CHANCE-11/12/13/14)
- [x] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick

---

### C7: View builder with percentil on Trabalhar

**What**: Assemble the view result; SCORE percentile and ESTADO computed over Trabalhar only; Trabalhar ordered by SCORE desc.
**Where**: `backend/app/views/query.py`
**Depends on**: C5, C6
**Reuses**: percentile/estado (lead-scorer T11/T12), bucketizer (C6).
**Requirement**: CHANCE-08, CHANCE-15

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] `build_view(repo, filter)` returns { trabalhar, decidir, revisar, totals }
- [x] Percentile computed over Trabalhar deals of the view (not over Decidir/Revisar)
- [x] Trabalhar ordered by SCORE desc; highest `value × chance` first
- [x] Unit tests cover percentile scope and ordering (CHANCE-08/15)
- [x] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick

---

### C8: Explain — chance & wall sentences (PT)

**What**: Portuguese chance sentence for Trabalhar and wall sentence for Decidir; action per bucket.
**Where**: `backend/app/views/explain.py`
**Depends on**: C3, C7
**Reuses**: existing `explain.py`; past-wall count (C4).
**Requirement**: CHANCE-16, CHANCE-17, CHANCE-18, CHANCE-19

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] Chance sentence (e.g., "47% dos deals desta idade fecharam") for workable deals
- [x] Wall sentence states wall age and past-wall open count for Decidir deals
- [x] Action: Trabalhar → advance; Decidir → "Requalificar ou encerrar"; Revisar → fix data
- [x] Every number is computed from data (no literal) — asserted
- [x] Unit tests cover all three bucket texts (CHANCE-16/17/18/19)
- [x] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick

---

### C9: Backtest runner (no-leakage) + gate

**What**: Reconstruct each view at ≥3 past cut-offs using only data known then; measure next-90-days captured revenue in top‑N per agent for the new ranking, price-only, and random.
**Where**: `backend/app/analysis/backtest.py` + `solution/backtest.py`
**Depends on**: C3
**Reuses**: cohort/chance recalibrated per cutoff.
**Requirement**: CHANCE-20, CHANCE-21, CHANCE-22, CHANCE-23, CHANCE-24

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] For each cutoff, the table is recalibrated using only deals known at that date (no future field read)
- [x] Reports captured revenue (top‑N per agent, next 90 days) for new/price/random with a dispersion measure
- [x] Emits the new-vs-price comparison; documents that the change is adopted only if new > price
- [x] Integration test asserts no field later than the cutoff is read (leakage guard)
- [x] Reproducible with a single documented command (`python backtest.py`)
- [x] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/integration -q`

**Tests**: integration
**Gate**: full

---

### C10: GET /api/queue — three buckets

**What**: Serve Trabalhar + Decidir + Revisar for the filtered view.
**Where**: `backend/app/api/queue.py`
**Depends on**: C7
**Reuses**: view builder (C7).
**Requirement**: CHANCE-11, CHANCE-14, CHANCE-29

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] `GET /api/queue?...` returns the three buckets with counts and totals
- [x] Switching view recomputes the Trabalhar percentile (asserted across two requests)
- [x] E2E tests cover the three-bucket payload and view switch (CHANCE-14/29)
- [x] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/e2e -q`

**Tests**: e2e
**Gate**: full

---

### C11: GET /api/rollup — Trabalhar vs Decidir

**What**: Serve the per-agent rollup splitting worked value from parked (Decidir) value.
**Where**: `backend/app/api/rollup.py`
**Depends on**: C10
**Reuses**: rollup service (lead-scorer T15), buckets (C6).
**Requirement**: CHANCE-25, CHANCE-26, CHANCE-27

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] Per agent: trabalharCount/Value and decidirCount/Value
- [x] Parked (Decidir) value highlighted as the primary cleanup figure
- [x] Filter recomputes both rollups and the percentile (CHANCE-27)
- [x] E2E tests cover the split rollup + filtered recompute (CHANCE-25/26/27)
- [x] Gate check passes: `.venv\Scripts\python -m pytest backend/tests/e2e -q`

**Tests**: e2e
**Gate**: full

---

### C12: DealCard shows chance (Trabalhar)

**What**: Render the chance sentence and value on each workable card; keep the Esfriando badge as a visual cue.
**Where**: `frontend/src/components/QueueList.tsx` (DealCard)
**Depends on**: C10
**Reuses**: API client (lead-scorer T21).
**Requirement**: CHANCE-16, CHANCE-31 (PT labels)

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] Each workable card shows the chance sentence in Portuguese
- [x] Esfriando badge still rendered where applicable (visual only)
- [x] Component unit tests cover the chance text and label language
- [x] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### C13: DecidirSection component

**What**: Render the Decidir list (price desc) with the wall sentence and the requalify-or-close action.
**Where**: `frontend/src/components/DecidirSection.tsx`
**Depends on**: C12
**Reuses**: API client (T21).
**Requirement**: CHANCE-11, CHANCE-12, CHANCE-17, CHANCE-18

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] Decidir rendered separate from Trabalhar, ordered by price desc
- [x] Wall sentence shown; action "Requalificar ou encerrar"
- [x] Empty-work-but-decide state renders the decision list, not an error
- [x] Component unit tests cover list, order, wall text, and the empty-work state (CHANCE-11/12/17/18)
- [x] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### C14: ManagerRollup shows parked value

**What**: Render the rollup with Trabalhar vs Decidir columns and the parked value highlighted.
**Where**: `frontend/src/components/ManagerRollup.tsx`
**Depends on**: C11
**Reuses**: rollup endpoint (C11), API client (T21).
**Requirement**: CHANCE-25, CHANCE-26

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] Per-agent rows show worked and parked counts/values; parked highlighted
- [x] Component unit tests cover the split columns + highlight (CHANCE-25/26)
- [x] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### C15: Config, ADRs & doc supersession

**What**: Expose wall/bands in config; add ADR-014/015/016; mark ADR-001/003 superseded; update README, `docs/evolucao-do-score.md` (v3), `docs/analise-exploratoria.md` (survival + wall).
**Where**: `backend/app/main.py` (settings), `docs/adr/`, `README.md`, `docs/evolucao-do-score.md`, `docs/analise-exploratoria.md`
**Depends on**: C9, C14
**Reuses**: existing ADR/doc structure.
**Requirement**: CHANCE-03, CHANCE-23 (documented decision)

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Wall and bands configurable; no magic literal in logic
- [ ] ADR-014/015/016 added; ADR-001/003 marked Superseded with original text intact
- [ ] README (summary, score logic, limitations), evolução-do-score (v3) and análise (survival/wall) updated; LEAD-07/19/20 marked Superseded in `lead-scorer/spec.md`
- [ ] Build gate passes
- [ ] Gate check passes: `.venv\Scripts\python -m pytest backend/tests -q && npm --prefix frontend run build && npm --prefix frontend test -- --run`

**Tests**: none
**Gate**: build

---

### C16: Validation lane

**What**: Run the harness validation lane for this feature.
**Where**: validation lane (no committed Playwright suite)
**Depends on**: C15
**Reuses**: `.cursor/agents/validation-lane.md`, `.cursor/rules/validation-lane.mdc`
**Requirement**: all CHANCE-* (verification)

**Tools**:

- MCP: Playwright MCP (ui-tester)
- Skill: NONE

**Done when**:

- [ ] backend-tester ∥ ui-tester pass; spec-verifier maps each AC → file:line
- [ ] UI scenarios: Trabalhar vs Decidir split, chance/wall text, rollup parked value
- [ ] `validation.md` written for the feature
- [ ] Lane reports PASS

**Tests**: UI e2e (Playwright MCP) + verifier
**Gate**: validation lane

---

## Task Granularity Check

| Task | Scope | Status |
| ---- | ----- | ------ |
| C1 | 1 cohort module | ✅ Granular |
| C2 | 1 survival-table function | ✅ Granular |
| C3 | chance() + wall in 1 module | ✅ Granular |
| C4 | 1 count function | ✅ Granular |
| C5 | 1 function rewrite (priority) | ✅ Granular |
| C6 | 1 bucketizer module | ✅ Granular |
| C7 | 1 view builder | ✅ Granular |
| C8 | 1 explain module (2 sentences) | ✅ Granular |
| C9 | 1 backtest module + script | ⚠️ Cohesive analysis unit |
| C10 | 1 endpoint | ✅ Granular |
| C11 | 1 endpoint | ✅ Granular |
| C12 | 1 component change | ✅ Granular |
| C13 | 1 component file | ✅ Granular |
| C14 | 1 component change | ✅ Granular |
| C15 | config + ADRs + docs (cohesive) | ⚠️ Cohesive docs unit |
| C16 | validation lane | ✅ Granular |

---

## Diagram-Definition Cross-Check

| Task | Depends On (task body) | Diagram Shows | Status |
| ---- | ---------------------- | ------------- | ------ |
| C1 | T4, T5 (lead-scorer) | — (external dep) | ✅ Match |
| C2 | C1 | C1→C2 | ✅ Match |
| C3 | C2 | C2→C3 | ✅ Match |
| C4 | C1 | C1→C4 | ✅ Match |
| C5 | C3 | C3→C5 | ✅ Match |
| C6 | C3 | C3→C6 | ✅ Match |
| C7 | C5, C6 | C5→C7, C6→C7 | ✅ Match |
| C8 | C3, C7 | C3→C8, C7→C8 | ✅ Match |
| C9 | C4 (count) / C3 (chance) | C3→C9, C4→C9 | ✅ Match |
| C10 | C7 | C7→C10 | ✅ Match |
| C11 | C10 | C10→C11 | ✅ Match |
| C12 | C10 | C10→C12 | ✅ Match |
| C13 | C12 | C12→C13 | ✅ Match |
| C14 | C11 | C11→C14 | ✅ Match |
| C15 | C9, C14 | C9→C15, C14→C15 | ✅ Match |
| C16 | C15 | C15→C16 | ✅ Match |

All dependencies point backward or within the same phase. No forward-phase dependency.

---

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
| ---- | --------------------------- | --------------- | --------- | ------ |
| C1 | Cohort / survival | unit | unit | ✅ OK |
| C2 | Cohort / survival | unit | unit | ✅ OK |
| C3 | Cohort / survival | unit | unit | ✅ OK |
| C4 | Cohort / survival | unit | unit | ✅ OK |
| C5 | Domain / scoring | unit | unit | ✅ OK |
| C6 | View / query | unit | unit | ✅ OK |
| C7 | View / query | unit | unit | ✅ OK |
| C8 | Explain | unit | unit | ✅ OK |
| C9 | Backtest | integration | integration | ✅ OK |
| C10 | API route | e2e | e2e | ✅ OK |
| C11 | API route | e2e | e2e | ✅ OK |
| C12 | React component | unit | unit | ✅ OK |
| C13 | React component | unit | unit | ✅ OK |
| C14 | React component | unit | unit | ✅ OK |
| C15 | Config / docs | none | none | ✅ OK |
| C16 | Validation lane | UI e2e + verifier | lane | ✅ OK |

No violations: every task's `Tests` field matches its code layer's required test type in the Test Coverage Matrix. The Playwright MCP row runs once, through the harness validation lane (`ui-tester`), not as a per-task `Tests` field.

---

## Tools (MCPs and Skills)

Execute tasks use the `filesystem` MCP and the project venv / `npm` for gates. Product critical path stays offline (RNF2); the backtest is an offline script.

**Validation lane (after last task):** Playwright MCP for UI Independent Tests (`ui-tester`). Enable the Cursor Playwright plugin or approve `submissions/joao-luiz/.cursor/mcp.json`. Backend gates stay pytest. Lane contract: `.cursor/rules/validation-lane.mdc`.
