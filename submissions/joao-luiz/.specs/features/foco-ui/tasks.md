# Foco da Semana — Reorganização da UX (`foco-ui`) Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute flow and Critical Rules.** Do not search for skill files by filesystem path. The skill is the source of truth for the full flow (per-task cycle, sub-agent delegation, adequacy review, Verifier, discrimination sensor).

**If the skill cannot be activated, STOP and tell the user - do not proceed without it.**

---

**Design**: `.specs/features/foco-ui/design.md`
**Status**: Draft

---

## Test Coverage Matrix

> Generated from codebase, project guidelines, and spec - confirm before Execute. Guidelines found: `AGENTS.md` (UI em PT / código em EN, faixa de validação por Playwright MCP), existing Vitest + Testing Library suite under `frontend/src/**/*.test.tsx`, `frontend/package.json` (`test` = `vitest`, `build` = `tsc --noEmit && vite build`). No coverage threshold configured; strong defaults applied on top of the existing suite as the floor.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| Routing/derivation pure utils (`parseLocation`, `toUrl`, `deriveSellerKpis`, `deriveTeamKpis`, `formatValue`) | unit | All branches; 1:1 to the ACs they implement; every listed edge case (unknown path, 106 boundary, empty) | `frontend/src/{routing,kpis}/**/*.test.ts` | `npm --prefix frontend test -- --run` |
| React hooks (`useViewRoute`, `useViewData`) | unit | State transitions on navigate/popstate; route→fetch mapping + loading/error, with mocked fetch/history | `frontend/src/routing/**/*.test.tsx` | `npm --prefix frontend test -- --run` |
| React components (strip, band, card variants, review row, rollup, export, empty, shell, stations) | unit | Render + behavior per AC (hierarchy, collapse, SCORE tooltip, no stage, badge, empty copy, clickable rows, contextual export) | `frontend/src/{components,stations}/**/*.test.tsx` | `npm --prefix frontend test -- --run` |
| CSS / visual system (`index.css`) | none | build gate only; visual constraints (FOCO-35) verified in the UI lane | - | build gate only |
| User-facing flows (rotas, drill, export contextual, estados vazios, âncora, mesa operacional, rótulos PT) | UI e2e (Playwright MCP) | Independent Tests + FOCO cross-cutting against the running UI — not mocked | validation-lane `ui-tester` (no committed Playwright suite) | Playwright MCP: scenarios in `.specs/features/foco-ui/validation-lane.md` |

## Gate Check Commands

> Generated from codebase - confirm before Execute. Frontend only; the backend is untouched.

| Gate Level | When to Use | Command |
| ---------- | ----------- | ------- |
| Quick | After tasks with unit tests only | `npm --prefix frontend test -- --run` |
| Build | After assembly/CSS/doc tasks | `npm --prefix frontend run build && npm --prefix frontend test -- --run` |
| Validation lane | After the last task (or on "validate") | Orchestrator `submissions/joao-luiz/.cursor/agents/validation-lane.md`: ui-tester (Playwright MCP) → spec-verifier. See `.specs/features/foco-ui/validation-lane.md`. |

---

## Execution Plan

Phases are ordered and run sequentially - each phase completes before the next begins, and tasks within a phase execute in order. All paths are relative to `solution/`.

### Phase 1: Routing & derivation foundation

```
T1 → T2
T1 → T4
T2 → T4
T3
T5
```

### Phase 2: Vendedor station pieces

```
T5 → T6
T7
T5 → T8
T9
T10
```

### Phase 3: Gestor station pieces

```
T5 → T11
T12
```

### Phase 4: Assembly, visual, docs

```
T2 → T13
T4 → T14
T6 → T14
T7 → T14
T8 → T14
T9 → T14
T10 → T14
T3 → T14
T4 → T15
T6 → T15
T10 → T15
T11 → T15
T12 → T15
T13 → T16
T14 → T16
T15 → T16
T16 → T17
T16 → T18
```

---

## Task Breakdown

### T1: Route serialization (parseLocation / toUrl)

**What**: Pure functions mapping URL path+query ↔ `ViewRoute` (station + agente/gestor/escritorio), with unknown-path fallback to vendedor.
**Where**: `frontend/src/routing/route.ts`
**Depends on**: None
**Reuses**: `withParams` pattern from `frontend/src/api/client.ts`.
**Requirement**: FOCO-01, FOCO-03, FOCO-07

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] `parseLocation(pathname, search)` returns `{ station, agente?, gestor?, escritorio? }`; unknown path → `station: "vendedor"`
- [x] `toUrl(route)` is the inverse (PT path + PT query keys), stable round-trip
- [x] Unit tests cover vendedor/gestor, each query param, unknown path, and round-trip (1:1 with FOCO-01/03/07)
- [x] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### T2: useViewRoute hook

**What**: Hook syncing `ViewRoute` with the browser via History API + `popstate` (`useSyncExternalStore`), exposing `{ route, navigate }`.
**Where**: `frontend/src/routing/useViewRoute.tsx`
**Depends on**: T1
**Reuses**: `parseLocation`/`toUrl` (T1).
**Requirement**: FOCO-02, FOCO-03, FOCO-04

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] `navigate(next)` pushes `toUrl(next)` without a full reload; reading returns the parsed current route
- [x] `popstate` (back/forward) updates the route (asserted in jsdom)
- [x] Unit tests cover navigate, popstate, and initial parse (1:1 with FOCO-02/04)
- [x] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### T3: KPI derivation util

**What**: Pure `deriveSellerKpis(queue)` and `deriveTeamKpis(rows)` returning the four-number summaries; "Esfriando" uses `age_days > 106`.
**Where**: `frontend/src/kpis/summary.ts`
**Depends on**: None
**Reuses**: payload types from `client.ts`.
**Requirement**: FOCO-06, FOCO-25

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] `deriveSellerKpis` returns valorEmFocar, nFocar, esfriando (`age_days > 106`), revisar
- [x] `deriveTeamKpis` sums valorTime, naFila, esfriando, bonsEsfriando from rollup rows
- [x] Unit tests cover the 106/107 boundary, Focar-only sums, and empty inputs (1:1 with FOCO-06)
- [x] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### T4: useViewData hook

**What**: Map a `ViewRoute` to the right endpoint call (queue for vendedor/drill, rollup+agents for gestor home) and expose `{ snapshot, status }` with loading/error.
**Where**: `frontend/src/routing/useViewData.tsx`
**Depends on**: T1, T2
**Reuses**: `queuePath`/`rollupPath` + `/api/agents` (client.ts).
**Requirement**: FOCO-04, FOCO-23

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [x] Vendedor/drill route → `GET /api/queue?view=mine&agent=`; gestor-home route → `GET /api/rollup` + `/api/agents`
- [x] Reload/route carrying a slice reproduces the same request (asserted) → supports FOCO-04
- [x] `status: "error"` on failed fetch instead of a thrown uncaught error
- [x] Unit tests (mocked fetch) cover both route kinds + error path (FOCO-04/23)
- [x] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### T5: Shared formatValue util

**What**: Extract the `US$ pt-BR` money formatter into a shared util for strip, cards, and rollup.
**Where**: `frontend/src/format/money.ts`
**Depends on**: None
**Reuses**: `formatValue` from `QueueList.tsx:62-64`.
**Requirement**: FOCO-36

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] `formatValue(n)` returns `US$ ` + `toLocaleString("pt-BR")`
- [ ] Unit test covers thousands separator and zero
- [ ] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### T6: SituationStrip component

**What**: Text+number strip rendering the four KPIs; Focar/Revisar items are activatable, Esfriando/Bons-esfriando are not.
**Where**: `frontend/src/components/SituationStrip.tsx`
**Depends on**: T5
**Reuses**: `formatValue` (T5).
**Requirement**: FOCO-06, FOCO-10, FOCO-35

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Renders each `{ label, value }`; items with `onActivate` are buttons, others are static
- [ ] No icon per KPI; text + number only (FOCO-35)
- [ ] Unit tests cover activatable vs static items and the labels (FOCO-06/10)
- [ ] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### T7: CollapsibleBand component

**What**: Band with a title showing the item count, `defaultOpen`, and expand/collapse on activation.
**Where**: `frontend/src/components/CollapsibleBand.tsx`
**Depends on**: None
**Reuses**: —.
**Requirement**: FOCO-08, FOCO-09

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Title shows `count`; `defaultOpen` controls initial state; activating the title toggles it (`aria-expanded`)
- [ ] Unit tests cover default-open Focar, default-collapsed with count, and toggle (FOCO-08/09)
- [ ] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### T8: DealCard variants refactor

**What**: Two densities — Focar hero (order: action, reason, value/age, Estado/Esfriando; SCORE demoted with tooltip "posição nesta visão, 0–100"; no stage; no PRIORIDADE) and Acompanhar compact row (product, account, value, action; SCORE in corner).
**Where**: `frontend/src/components/DealCard.tsx`
**Depends on**: T5
**Reuses**: refatora `QueueList.tsx` (PT labels) + `formatValue` (T5).
**Requirement**: FOCO-11, FOCO-12, FOCO-13, FOCO-14, FOCO-15, FOCO-17

**Tools**:

- MCP: `filesystem`
- Skill: `frontend-design` (hierarchy/density craft)

**Done when**:

- [ ] Focar variant renders in order action → reason → value/age → Estado/Esfriando
- [ ] SCORE is secondary with the tooltip text; the word "percentil" appears nowhere; stage not rendered; no second money figure
- [ ] Esfriando badge rendered as a distinct element when `age_days > 106`
- [ ] Acompanhar variant is a compact row with SCORE in the corner
- [ ] Unit tests cover both variants, SCORE tooltip, absence of stage/percentil, badge at 107 and none at 106 (FOCO-11/12/13/14/15/17)
- [ ] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### T9: ReviewRow component

**What**: Revisar item showing the reason it is parked (missing account / missing date) and the action, with no SCORE.
**Where**: `frontend/src/components/ReviewRow.tsx`
**Depends on**: None
**Reuses**: `ReviewItem` type + labels from `ReviewSection.tsx`.
**Requirement**: FOCO-16

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Shows product, the parked-reason, and action; renders no SCORE
- [ ] Unit tests cover missing-account and missing-date reasons and the no-SCORE invariant (FOCO-16)
- [ ] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### T10: EmptyState variants

**What**: Case-specific empty states: ghost agent ("escolha outro vendedor"), only-Revisar ("nada trabalhável; N em Revisar"), no-sellers ("nenhum vendedor neste gestor/escritório").
**Where**: `frontend/src/components/EmptyState.tsx`
**Depends on**: None
**Reuses**: extrai o `EmptyState` de `ReviewSection.tsx`.
**Requirement**: FOCO-20, FOCO-21, FOCO-22

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Each variant renders its specific teaching copy (role `status`), never a generic alert
- [ ] Unit tests cover the three variants (FOCO-20/21/22)
- [ ] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### T11: RollupTable refactor (header fix + clickable rows)

**What**: Per-agent table with a `<th>` for every displayed column (including "Bons esfriando") and rows that invoke `onSelectAgent` for the drill.
**Where**: `frontend/src/components/RollupTable.tsx`
**Depends on**: T5
**Reuses**: evolui `ManagerRollup.tsx` + `formatValue` (T5).
**Requirement**: FOCO-24, FOCO-27

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Every displayed column has a header cell; "Bons esfriando" no longer a headerless `<td>`
- [ ] Activating a row calls `onSelectAgent(sales_agent)`
- [ ] Unit tests cover header alignment and row click (FOCO-24/27) — update/replace `ManagerRollup.test.tsx`
- [ ] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### T12: ExportButton contextual + error handling

**What**: Export the current view's queue; surface an error message on failure (no silent throw).
**Where**: `frontend/src/components/ExportButton.tsx` (refactor)
**Depends on**: None
**Reuses**: `exportCsvPath` + download logic (existing).
**Requirement**: FOCO-23, FOCO-33

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Download uses the active filter; the CSV reflects the current filtered view (FOCO-33, preserves CA9/LEAD-25)
- [ ] A failed request shows an error message (role `alert`) instead of throwing uncaught (FOCO-23)
- [ ] Unit tests cover the request filter and the error path
- [ ] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### T13: AppShell + RoleRail + temporal anchor

**What**: Persistent chrome: left rail (Vendedor | Gestor) that navigates stations, "Visão em 31/12/2017" anchor, station outlet; no "Visão" `<select>`.
**Where**: `frontend/src/components/AppShell.tsx`
**Depends on**: T2
**Reuses**: `useViewRoute` (T2).
**Requirement**: FOCO-02, FOCO-05, FOCO-34

**Tools**:

- MCP: `filesystem`
- Skill: `frontend-design` (rail/chrome craft)

**Done when**:

- [ ] Rail navigates between `/vendedor` and `/gestor`; active station marked
- [ ] Anchor "Visão em 31/12/2017" present; no "Visão" select anywhere (FOCO-05/34)
- [ ] Unit tests cover rail navigation and the anchor/no-select invariants (FOCO-02/05/34)
- [ ] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### T14: VendedorStation assembly

**What**: Compose the vendedor station: situation strip + Focar hero band + collapsed Acompanhar/Revisar + contextual export + empty states.
**Where**: `frontend/src/stations/VendedorStation.tsx`
**Depends on**: T3, T4, T6, T7, T8, T9, T10
**Reuses**: strip, band, card, review row, empty, kpis, data hook.
**Requirement**: FOCO-06, FOCO-07, FOCO-08, FOCO-09, FOCO-10, FOCO-20, FOCO-21, FOCO-31

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Renders only the "quem sou eu" selector; strip from `deriveSellerKpis`; Focar open, Acompanhar/Revisar collapsed with counts
- [ ] KPI Focar/Revisar activation opens/scrolls the matching band
- [ ] Ghost agent and only-Revisar empty states shown; Export present (FOCO-31)
- [ ] Unit tests cover the composed layout, band defaults, KPI activation, and empty states (FOCO-06/07/08/09/10/20/21)
- [ ] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### T15: GestorStation + drill

**What**: Compose the gestor station: team strip + rollup hero (no team queue) in home; clicking a seller drills into that seller's queue (bands + strip switches + export appears); back clears `agente`.
**Where**: `frontend/src/stations/GestorStation.tsx`
**Depends on**: T4, T6, T10, T11, T12
**Reuses**: strip, rollup table, bands (via card), export, data hook.
**Requirement**: FOCO-24, FOCO-25, FOCO-26, FOCO-28, FOCO-29, FOCO-30, FOCO-32

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Home (no `agente`) shows team strip + rollup hero, no full team queue, no export (FOCO-24/26/32)
- [ ] Selecting a seller sets `?agente=` and replaces the hero with that seller's bands; strip reflects that seller (FOCO-28/29)
- [ ] Leaving the drill clears `agente` and restores the rollup, staying on `/gestor` (FOCO-30)
- [ ] Unit tests cover home, drill, strip switch, export visibility, and back (FOCO-24/25/26/28/29/30/32)
- [ ] Gate check passes: `npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: quick

---

### T16: Wire App.tsx to shell + stations

**What**: Replace the single-form `App` with `AppShell` + route-driven station rendering via `useViewRoute`/`useViewData`; drop `createViewClient` from the main path; `/` redirects to `/vendedor?agente=Anna+Snelling`.
**Where**: `frontend/src/App.tsx`
**Depends on**: T13, T14, T15
**Reuses**: shell, stations, routing/data hooks.
**Requirement**: FOCO-01, FOCO-04, FOCO-05

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] `/` redirects to `/vendedor?agente=Anna+Snelling`; stations render from the route
- [ ] Old `<select>`-based form and `createViewClient` removed from the render path; `App.test.tsx` updated
- [ ] Unit/integration render tests cover the redirect and station switch by route (FOCO-01/04/05)
- [ ] Gate check passes: `npm --prefix frontend run build && npm --prefix frontend test -- --run`

**Tests**: unit
**Gate**: build

---

### T17: Mesa operacional visual system (index.css)

**What**: Rewrite `index.css` to the operational-desk tone: light, dense, typographic hierarchy, little radius, no gradients/glassmorphism/per-KPI icons; distinct densities for Focar/Acompanhar/Revisar.
**Where**: `frontend/src/index.css`
**Depends on**: T16
**Reuses**: existing global CSS as the starting point.
**Requirement**: FOCO-35

**Tools**:

- MCP: `filesystem`
- Skill: `frontend-design` (visual system)

**Done when**:

- [ ] Hierarchy supports Focar-as-hero vs compact Acompanhar; no decorative gradient/glass; strip is text+number
- [ ] `npm --prefix frontend run build` succeeds (no CSS/TS errors); existing component tests still pass
- [ ] Visual constraints (FOCO-35) are left for the UI lane to assert on the running UI
- [ ] Gate check passes: `npm --prefix frontend run build && npm --prefix frontend test -- --run`

**Tests**: none
**Gate**: build

---

### T18: foco-ui validation-lane doc + NEXT-ACTION

**What**: Author `.specs/features/foco-ui/validation-lane.md` (UI scenarios + AC→lane map for the new UX) and update `NEXT-ACTION.md`.
**Where**: `.specs/features/foco-ui/validation-lane.md`
**Depends on**: T16
**Reuses**: `lead-scorer/validation-lane.md` structure + ui-evidence convention.
**Requirement**: FOCO-30, FOCO-35, FOCO-36

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Lane doc lists UI scenarios (rotas/trilho, Focar herói, card hierarchy, empty states, rollup+drill, export contextual, âncora, PT) with ui-evidence paths under `.specs/features/foco-ui/ui-evidence/`
- [ ] `NEXT-ACTION.md` points to Execute/validation of `foco-ui`
- [ ] Gate check passes: `npm --prefix frontend run build && npm --prefix frontend test -- --run`

**Tests**: none
**Gate**: build

---

## Phase Execution Map

Phases run in sequence; tasks within a phase run in order. The authoritative dependency edges are the per-phase diagrams in **Execution Plan** above; the listing below is membership only (no arrows, to avoid implying edges beyond the task bodies).

```
Phase 1  (routing & derivation):  T1, T2, T3, T4, T5
Phase 2  (vendedor pieces):       T6, T7, T8, T9, T10
Phase 3  (gestor pieces):         T11, T12
Phase 4  (assembly, visual, docs): T13, T14, T15, T16, T17, T18
```

Execution is strictly sequential - one task at a time, in order, within each phase. Total 18 tasks (> ~8) → offer batch sub-agents at Execute (packing whole phases into ~7-task batches, e.g. Phase 1+2 / Phase 3+4).

---

## Task Granularity Check

| Task | Scope | Status |
| ---- | ----- | ------ |
| T1 | 1 route util module | ✅ Granular |
| T2 | 1 hook | ✅ Granular |
| T3 | 1 kpi util module | ✅ Granular |
| T4 | 1 hook | ✅ Granular |
| T5 | 1 util function | ✅ Granular |
| T6 | 1 component | ✅ Granular |
| T7 | 1 component | ✅ Granular |
| T8 | 1 component (2 variants, 1 file) | ⚠️ Cohesive (same card, two densities) |
| T9 | 1 component | ✅ Granular |
| T10 | 1 component (variants) | ✅ Granular |
| T11 | 1 component | ✅ Granular |
| T12 | 1 component | ✅ Granular |
| T13 | 1 shell component | ✅ Granular |
| T14 | 1 station (composition) | ✅ Granular |
| T15 | 1 station (composition) | ✅ Granular |
| T16 | 1 top-level wiring file | ✅ Granular |
| T17 | 1 CSS file | ✅ Granular |
| T18 | 1 doc + 1 pointer | ⚠️ Cohesive docs |

---

## Diagram-Definition Cross-Check

| Task | Depends On (task body) | Diagram Shows | Status |
| ---- | ---------------------- | ------------- | ------ |
| T1 | None | None | ✅ Match |
| T2 | T1 | T1→T2 | ✅ Match |
| T3 | None | None | ✅ Match |
| T4 | T1, T2 | T1→T4, T2→T4 | ✅ Match |
| T5 | None | None | ✅ Match |
| T6 | T5 | T5→T6 | ✅ Match |
| T7 | None | None | ✅ Match |
| T8 | T5 | T5→T8 | ✅ Match |
| T9 | None | None | ✅ Match |
| T10 | None | None | ✅ Match |
| T11 | T5 | T5→T11 | ✅ Match |
| T12 | None | None | ✅ Match |
| T13 | T2 | T2→T13 | ✅ Match |
| T14 | T3, T4, T6, T7, T8, T9, T10 | T3→T14, T4→T14, T6→T14, T7→T14, T8→T14, T9→T14, T10→T14 | ✅ Match |
| T15 | T4, T6, T10, T11, T12 | T4→T15, T6→T15, T10→T15, T11→T15, T12→T15 | ✅ Match |
| T16 | T13, T14, T15 | T13→T16, T14→T16, T15→T16 | ✅ Match |
| T17 | T16 | T16→T17 | ✅ Match |
| T18 | T16 | T16→T18 | ✅ Match |

All dependencies point backward or within the same phase. No forward-phase dependency.

---

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
| ---- | --------------------------- | --------------- | --------- | ------ |
| T1 | Routing pure util | unit | unit | ✅ OK |
| T2 | React hook | unit | unit | ✅ OK |
| T3 | KPI pure util | unit | unit | ✅ OK |
| T4 | React hook | unit | unit | ✅ OK |
| T5 | Pure util | unit | unit | ✅ OK |
| T6 | React component | unit | unit | ✅ OK |
| T7 | React component | unit | unit | ✅ OK |
| T8 | React component | unit | unit | ✅ OK |
| T9 | React component | unit | unit | ✅ OK |
| T10 | React component | unit | unit | ✅ OK |
| T11 | React component | unit | unit | ✅ OK |
| T12 | React component | unit | unit | ✅ OK |
| T13 | React component | unit | unit | ✅ OK |
| T14 | React station (component) | unit | unit | ✅ OK |
| T15 | React station (component) | unit | unit | ✅ OK |
| T16 | App wiring (component) | unit | unit | ✅ OK |
| T17 | CSS / visual | none | none | ✅ OK |
| T18 | Docs | none | none | ✅ OK |

No violations: every code task co-locates its Vitest tests; T17 (CSS) and T18 (docs) map to the "none" layer (build gate), with FOCO-35 visual verification owned by the Playwright MCP lane.

---

## Tools (MCPs and Skills)

Execute tasks use the `filesystem` MCP and `npm` for gates. The product critical path stays offline and the backend is untouched (no new endpoint — ADR-011).

- **Skill `frontend-design`**: recommended for T8 (card densities), T13 (rail/chrome) and T17 (visual system) to hit the "mesa operacional" tone without AI-slop tells (ADR-012).
- **Validation lane (after T18 / on "validate")**: Playwright MCP for the UI Independent Tests. Enable the Cursor Playwright plugin or approve `submissions/joao-luiz/.cursor/mcp.json`. See `.specs/features/foco-ui/validation-lane.md`.

> **ASK before Execute:** confirm these tool choices (filesystem + npm gates; `frontend-design` on T8/T13/T17; Playwright MCP only in the lane), and confirm the Test Coverage Matrix + Gate Check Commands above.
