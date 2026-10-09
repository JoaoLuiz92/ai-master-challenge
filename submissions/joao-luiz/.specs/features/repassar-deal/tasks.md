# Repassar deal — o gestor passa o negócio sem perdê-lo (`repassar-deal`) Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute flow and Critical Rules.** Do not search for skill files by filesystem path. The skill is the source of truth for the full flow (per-task cycle, sub-agent delegation, adequacy review, Verifier, discrimination sensor).

**If the skill cannot be activated, STOP and tell the user - do not proceed without it.**

---

**Design**: `.specs/features/repassar-deal/design.md`
**Status**: Execute (T4)

> Repasse **só em memória** (ADR-013 / AD-013). Sem `handoffs.jsonl`. Sem AD extra antes da Phase 1: a decisão já está em `docs/adr/013-repasse-so-na-sessao.md` e no README § Limitações.

---

## Test Coverage Matrix

> Generated from codebase, project guidelines, and spec - confirm before Execute. Guidelines found: `AGENTS.md`, `solution/pytest.ini`, pytest em `backend/tests/{unit,integration,e2e}`, Vitest em `frontend/src/**/*.test.tsx`. Strong defaults on top of the existing suite.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| Domain/service (`eligible_candidates`, `assign`, `Deal` replace) | unit | All branches; 1:1 ACs; edges (unknown id, same owner, other office, not workable, no-office, double click) | `backend/tests/unit/test_*.py` | `.venv\Scripts\python.exe -m pytest backend/tests/unit -q` |
| Persistence / startup | integration | Novo `create_app()` restaura donos do CSV; bytes dos quatro CSVs inalterados; nenhum overlay em `data/` | `backend/tests/integration/test_*.py` | `.venv\Scripts\python.exe -m pytest backend/tests/integration -q` |
| Route (POST /api/handoff, GET /api/handoff/candidates, `from_agent` no /api/queue) | e2e | Happy + cada recusa (404/409/422) | `backend/tests/e2e/test_*.py` | `.venv\Scripts\python.exe -m pytest backend/tests/e2e -q` |
| Frontend client | unit | Request shape + error path, mocked fetch | `frontend/src/api/*.test.ts` | `npm --prefix frontend test -- --run` |
| Frontend components/stations | unit | Lista, cooling, cancel, erro, botão só no drill Focar/Acompanhar, "Veio de", refresh | `frontend/src/{components,stations}/**/*.test.tsx` | `npm --prefix frontend test -- --run` |
| Fluxo na UI | UI e2e (Playwright MCP) | Independent Tests da `spec.md` | validation-lane `ui-tester` | Playwright MCP |

## Gate Check Commands

> Cwd `solution/`. Python `.venv\Scripts\python.exe`.

| Gate Level | When to Use | Command |
| ---------- | ----------- | ------- |
| Quick (backend) | Após tasks unit | `.venv\Scripts\python.exe -m pytest backend/tests/unit -q` |
| Full (backend) | Após integration/e2e | `.venv\Scripts\python.exe -m pytest backend/tests -q` |
| Quick (frontend) | Após tasks unit frontend | `npm --prefix frontend test -- --run` |
| Build (frontend) | Após assembly | `npm --prefix frontend run build && npm --prefix frontend test -- --run` |
| Validation lane | Após a última tarefa | `.cursor/agents/validation-lane.md` |

---

## Execution Plan

Paths relativos a `solution/`.

### Phase 1: Serviço em memória

```
T1
T2
T1 → T3
T2 → T3
```

### Phase 2: API + payload

```
T3 → T4
T2 → T5
T4 → T5
T1 → T6
T4 → T6
```

### Phase 3: Frontend

```
T6 → T7
T7 → T8
T7 → T9
T8 → T9
T8 → T10
T9 → T10
```

---

## Task Breakdown

### T1: Deal.from_agent + reassign in memory

**What**: Add `from_agent: str | None = None` to `Deal` and a pure `reassign_deal(deals, opportunity_id, to_agent, from_agent, manager, office)` that returns a new tuple via `replace`; unknown id leaves the tuple unchanged; two reassigns of the same id leave exactly one deal.
**Where**: `backend/app/ingestion/repository.py`
**Depends on**: None
**Reuses**: `dataclasses.replace`.
**Requirement**: REPA-03, REPA-04, REPA-06, REPA-16

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] `Deal` has `from_agent`; `reassign_deal` sets `sales_agent`, `manager`, `regional_office`, `from_agent`; product, account, value, dates, `opportunity_id` unchanged; count unchanged
- [x] Unknown id: same tuple; second reassign of same id: still one deal (REPA-16)
- [x] Unit tests cover those cases
- [x] Gate check passes: `.venv\Scripts\python.exe -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick (backend)

---

### T2: eligible_candidates

**What**: `eligible_candidates(deals, opportunity_id)` returns same-office agents minus the owner; empty for unknown deal or owner with no office.
**Where**: `backend/app/handoffs/service.py`
**Depends on**: None
**Reuses**: `Deal.regional_office` / `sales_agent`.
**Requirement**: REPA-01, REPA-12

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] Same-office minus owner; other offices excluded; `()` for unknown / no-office
- [x] Unit tests cover those cases
- [x] Gate check passes: `.venv\Scripts\python.exe -m pytest backend/tests/unit -q`

**Tests**: unit
**Gate**: quick (backend)

---

### T3: assign (validate + replace, no disk)

**What**: `assign(deals, opportunity_id, to_agent, team_by_agent)` validating in order (exists → workable → colleague exists → same office → not current owner) and returning a new deals tuple; never writes files.
**Where**: `backend/app/handoffs/service.py`
**Depends on**: T1, T2
**Reuses**: `reassign_deal` (T1), `eligible_candidates` (T2), `split_view`.
**Requirement**: REPA-02, REPA-05, REPA-10, REPA-11, REPA-12, REPA-13, REPA-14

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] Success: new owner, `from_agent` set, list value and age unchanged
- [x] Each invalid case keeps the owner and returns the spec message
- [x] Integration: after `assign`, source CSV bytes unchanged and `data/` has no overlay file (REPA-14, REPA-17)
- [x] Gate check passes: `.venv\Scripts\python.exe -m pytest backend/tests -q`

**Tests**: integration
**Gate**: full (backend)

---

### T4: POST /api/handoff

**What**: `POST /api/handoff` body `{opportunity_id, to_agent}` calling `assign` and replacing `app.state.deals`; 200 with `{opportunity_id, sales_agent, from_agent}`; mapped 404/409/422 + `detail`; router in `main.py`.
**Where**: `backend/app/api/handoff.py`
**Depends on**: T3
**Reuses**: `assign`, `queue.py` router pattern.
**Requirement**: REPA-02, REPA-03, REPA-04, REPA-10, REPA-11, REPA-12, REPA-13

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] Success moves the deal between queues (same id/product/account/value/age)
- [x] Unknown→404, same owner→409, other office→422, not workable→422
- [x] E2E TestClient covers success + each rejection
- [x] Gate check passes: `.venv\Scripts\python.exe -m pytest backend/tests/e2e -q`

**Tests**: e2e
**Gate**: full (backend)

---

### T5: GET /api/handoff/candidates

**What**: `GET /api/handoff/candidates?opportunity_id=` returning `{candidates}` from `eligible_candidates`.
**Where**: `backend/app/api/handoff.py`
**Depends on**: T4, T2
**Reuses**: `eligible_candidates`, router from T4.
**Requirement**: REPA-01, REPA-12

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Same-office minus owner; empty list for no-office / unknown
- [ ] E2E covers populated and empty
- [ ] Gate check passes: `.venv\Scripts\python.exe -m pytest backend/tests/e2e -q`

**Tests**: e2e
**Gate**: full (backend)

---

### T6: from_agent on QueueItem + restart restores CSV owners

**What**: Add `from_agent: str | None` to `QueueItem` from the deal; assert a second `create_app()` after a handoff owns deals as in the CSVs.
**Where**: `backend/app/views/query.py`
**Depends on**: T1, T4
**Reuses**: `build_queue`, `Deal.from_agent`, `POST /api/handoff` (T4).
**Requirement**: REPA-15, REPA-18, REPA-19

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] `QueueItem.from_agent` is the previous owner after a handoff, null otherwise
- [ ] Integration: handoff in client A; new `TestClient(create_app())` has CSV owner again (REPA-15)
- [ ] Gate check passes: `.venv\Scripts\python.exe -m pytest backend/tests -q`

**Tests**: integration
**Gate**: full (backend)

---

### T7: client.ts — types + postHandoff + fetchHandoffCandidates

**What**: `from_agent?` on `QueueItem`; `postHandoff` and `fetchHandoffCandidates` with error `detail`.
**Where**: `frontend/src/api/client.ts`
**Depends on**: T6
**Reuses**: `fetch` helpers.
**Requirement**: REPA-01, REPA-18

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] POST `{opportunity_id, to_agent}`; GET candidates; non-ok throws `detail`
- [ ] Unit tests (mocked fetch) cover success and error
- [ ] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick (frontend)

---

### T8: HandoffDialog

**What**: Dialog with candidate list, cooling note only when `age_days > 106`, confirm/cancel, error slot, empty "Nenhum colega neste escritório".
**Where**: `frontend/src/components/HandoffDialog.tsx`
**Depends on**: T7
**Reuses**: client T7.
**Requirement**: REPA-01, REPA-07, REPA-09

**Tools**:

- MCP: `filesystem`
- Skill: `frontend-design`

**Done when**:

- [ ] List; cooling at 107 not at 106; cancel does not post; error shows `detail`; empty copy
- [ ] Unit tests cover those cases
- [ ] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick (frontend)

---

### T9: DealCard — "Passar para colega" + "Veio de"

**What**: Action only on gestor drill Focar/Acompanhar; "Veio de {from_agent}" when set.
**Where**: `frontend/src/components/DealCard.tsx`
**Depends on**: T7, T8
**Reuses**: `DealCard`, `HandoffDialog`.
**Requirement**: REPA-08, REPA-18

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Action on drill Focar/Acompanhar; never vendedor or Revisar
- [ ] Trace is text only
- [ ] Unit tests cover visibility and trace
- [ ] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick (frontend)

---

### T10: GestorStation — dialog + refresh

**What**: Open `HandoffDialog` from a drill card; on success refetch so the deal leaves origin and appears on the colleague; cancel is a no-op.
**Where**: `frontend/src/stations/GestorStation.tsx`
**Depends on**: T8, T9
**Reuses**: dialog, DealCard, existing drill.
**Requirement**: REPA-02, REPA-03, REPA-07, REPA-08

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Confirm refetches; cancel unchanged; action only in drill
- [ ] Unit tests cover those cases
- [ ] Gate check passes: `npm --prefix frontend run build && npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: build (frontend)

---

## Phase Execution Map

```
Phase 1 (serviço):  T1, T2, T3
Phase 2 (API):      T4, T5, T6
Phase 3 (frontend): T7, T8, T9, T10
```

Total 10 tasks (> ~8) → offer batch sub-agents at Execute (Phase 1+2 / Phase 3).

---

## Task Granularity Check

| Task | Scope | Status |
| ---- | ----- | ------ |
| T1 | 1 field + 1 function (same file) | ⚠️ Cohesive |
| T2 | 1 function | ✅ Granular |
| T3 | 1 function (same file as T2) | ✅ Granular |
| T4 | 1 endpoint | ✅ Granular |
| T5 | 1 endpoint (same router) | ✅ Granular |
| T6 | QueueItem field + restart assertion | ⚠️ Cohesive (payload + ADR-013) |
| T7 | 1 client module | ⚠️ Cohesive |
| T8 | 1 component | ✅ Granular |
| T9 | 1 component | ✅ Granular |
| T10 | 1 station | ✅ Granular |

---

## Diagram-Definition Cross-Check

| Task | Depends On (task body) | Diagram Shows | Status |
| ---- | ---------------------- | ------------- | ------ |
| T1 | None | None | ✅ Match |
| T2 | None | None | ✅ Match |
| T3 | T1, T2 | T1→T3, T2→T3 | ✅ Match |
| T4 | T3 | T3→T4 | ✅ Match |
| T5 | T4, T2 | T4→T5, T2→T5 | ✅ Match |
| T6 | T1, T4 | T1→T6, T4→T6 | ✅ Match |
| T7 | T6 | T6→T7 | ✅ Match |
| T8 | T7 | T7→T8 | ✅ Match |
| T9 | T7, T8 | T7→T9, T8→T9 | ✅ Match |
| T10 | T8, T9 | T8→T10, T9→T10 | ✅ Match |

All dependencies point backward or within the same phase.

---

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
| ---- | --------------------------- | --------------- | --------- | ------ |
| T1 | Domain | unit | unit | ✅ OK |
| T2 | Domain | unit | unit | ✅ OK |
| T3 | Domain + CSVs untouched | integration (highest) | integration | ✅ OK |
| T4 | Route | e2e | e2e | ✅ OK |
| T5 | Route | e2e | e2e | ✅ OK |
| T6 | Domain + startup | integration | integration | ✅ OK |
| T7 | Frontend client | unit | unit | ✅ OK |
| T8 | Frontend component | unit | unit | ✅ OK |
| T9 | Frontend component | unit | unit | ✅ OK |
| T10 | Frontend station | unit | unit | ✅ OK |

---

## Tools (MCPs and Skills)

Filesystem + pytest/npm. Motor 001–007 intocado.

- **Skill `frontend-design`**: T8 (diálogo, tom mesa operacional).
- **Validation lane (após T10)**: backend-tester + ui-tester → spec-verifier.

> **ASK before Execute:** confirmar matriz/gates e `frontend-design` no T8. ADR-013 já está gravada — Execute não espera outro AD.
