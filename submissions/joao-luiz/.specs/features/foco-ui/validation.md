# Foco-ui Validation

**Date**: 2026-10-09
**Spec**: `.specs/features/foco-ui/spec.md`
**Diff range**: `be49a4b..7faf1ad` (foco-ui implementation) plus `19adc75` (station assertions only). `repassar-deal` commits between those tips are outside this feature. Line citations are from `19adc75`.
**Verifier**: independent sub-agent (author ≠ verifier)
**Iteration**: re-verify 1

## Validation

**Result**: PASS

---

## Task Completion

All 18 Execute tasks are checked. `19adc75` changes only `VendedorStation.test.tsx` and `GestorStation.test.tsx` (+13 lines). Product UI code is unchanged in that commit.

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1 | ✅ Done | `parseLocation` / `toUrl` |
| T2 | ✅ Done | `useViewRoute` |
| T3 | ✅ Done | Seller and team KPI derivation |
| T4 | ✅ Done | `useViewData` |
| T5 | ✅ Done | `formatValue` |
| T6 | ✅ Done | `SituationStrip` |
| T7 | ✅ Done | `CollapsibleBand` |
| T8 | ✅ Done | `DealCard` densities |
| T9 | ✅ Done | `ReviewRow` |
| T10 | ✅ Done | `EmptyState` |
| T11 | ✅ Done | `RollupTable` |
| T12 | ✅ Done | `ExportButton` error path |
| T13 | ✅ Done | `AppShell` + rail + anchor |
| T14 | ✅ Done | `VendedorStation` |
| T15 | ✅ Done | `GestorStation` drill |
| T16 | ✅ Done | `App` wiring and `/` redirect |
| T17 | ✅ Done | Operational-desk CSS |
| T18 | ✅ Done | `NEXT-ACTION.md` points at the harness lane |

The traceability table lists 36 IDs. The user stories contain 38 acceptance criteria. Two criteria have no ID: Esfriando uses `age_days > 106`, and a Revisar row shows the parked reason with no SCORE. Both are tested.

---

## Spec-Anchored Acceptance Criteria

UI rows cite the Playwright MCP lane already recorded this session (8/8). Backend pytest is not in this feature's matrix and was not run.

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| FOCO-01 WHEN a user opens `/` THEN redirect to `/vendedor?agente=Anna+Snelling` | That exact URL | `solution/frontend/src/App.test.tsx:87` - `expect(\`${pathname}${search}\`).toBe("/vendedor?agente=Anna+Snelling")`. UI scenario 1 (`ui-evidence/01-estacoes-redirect.png`) | ✅ PASS |
| FOCO-02 WHEN the rail control is activated THEN navigate to `/gestor` or `/vendedor` | Path becomes the station | `solution/frontend/src/components/AppShell.test.tsx:25` - `expect(onNavigate).toHaveBeenCalledWith("gestor")`. `solution/frontend/src/App.test.tsx:112` - `expect(window.location.pathname).toBe("/vendedor")`. UI scenario 1 (`ui-evidence/01-estacoes-depois-gestor.png`) | ✅ PASS |
| FOCO-03 The system encodes role in the path and slice in `agente`, `gestor`, `escritorio` | PT path + those query keys, round-trip | `solution/frontend/src/routing/route.test.ts:20` - `toEqual({ station: "gestor", agente: "Anna Snelling", gestor: "Dustin Brinkmann", escritorio: "Central" })` and `:43` - `toBe("/vendedor?agente=Anna+Snelling")` | ✅ PASS |
| FOCO-04 WHEN the page reloads or the URL carries a slice THEN the same view and the same SCORE return | Same station, same slice request | `solution/frontend/src/routing/useViewRoute.test.tsx:31` - `textContent).toBe("vendedor")` and `:32` - `toBe("Anna Snelling")`. `solution/frontend/src/routing/useViewData.test.tsx:119` - `expect(rollupCalls).toHaveLength(2)`. UI scenario 1 (`ui-evidence/01-estacoes-reload-assertado.png`) | ✅ PASS |
| FOCO-05 The system does not render a Visão `<select>` | No Visão combobox | `solution/frontend/src/App.test.tsx:92` - `expect(screen.queryByLabelText("Visão")).toBeNull()` and `:93` - `querySelector("select[name='visao']")` is null. `solution/frontend/src/components/AppShell.test.tsx:39` - `expect(document.querySelector("select")).toBeNull()`. UI scenario 8 (`ui-evidence/08-chrome-assertado.png`) | ✅ PASS |
| FOCO-06 WHILE vendedor, only the Vendedor selector; WHILE gestor, only Gestor and Escritório | Those labels, and not the other station's selectors | `solution/frontend/src/stations/VendedorStation.test.tsx:90` - `getByLabelText("Vendedor")` and `:91` - `queryByLabelText("Gestor")` is null and `:92` - `queryByLabelText("Escritório")` is null. `solution/frontend/src/stations/GestorStation.test.tsx:86` - `getByLabelText("Gestor")` and `:87` - `getByLabelText("Escritório")` and `:88` - `queryByLabelText("Vendedor")` is null | ✅ PASS |
| FOCO-07 IF the path matches no station THEN redirect to `/vendedor` | Unknown path parses as vendedor; `/` navigates to `/vendedor` | `solution/frontend/src/routing/route.test.ts:29` - `expect(parseLocation("/desconhecido", "")).toEqual({ station: "vendedor" })`. `solution/frontend/src/App.tsx:18` redirects every path other than `/vendedor` and `/gestor`. `solution/frontend/src/App.test.tsx:87` asserts `/` lands on `/vendedor?agente=Anna+Snelling` | ✅ PASS |
| FOCO-08 WHEN the vendedor queue loads THEN the strip shows Valor em Focar, Nº Focar, Esfriando, and Revisar from the payload | Those four labels; Focar value and count from Focar rows only; Revisar count from `revisar` | `solution/frontend/src/stations/VendedorStation.test.tsx:93` - `getByText("Valor em Focar")` and `:94` - `getByText("Nº Focar")`. `solution/frontend/src/kpis/summary.test.ts:71` - `expect(kpis.valorEmFocar).toBe(2500)` and `:72` - `toBe(2)` and `:73` - `expect(kpis.revisar).toBe(2)`. UI scenario 2 (`ui-evidence/02-faixa-assertado.png`) | ✅ PASS |
| FOCO-09 The Focar band is expanded by default | `aria-expanded="true"` and the Focar action is visible | `solution/frontend/src/stations/VendedorStation.test.tsx:95` - `getAttribute("aria-expanded")).toBe("true")` on `Focar (1)` and `:104` - `getByText("Avançar proposta")`. UI scenario 2 (`ui-evidence/02-faixa-antes.png`) | ✅ PASS |
| FOCO-10 Acompanhar and Revisar start collapsed, with the count in the title | `aria-expanded="false"` and titles `Acompanhar (1)`, `Revisar (1)`; collapsed body hidden | `solution/frontend/src/stations/VendedorStation.test.tsx:98` - `toBe("false")` and `:101` - `toBe("false")` and `:106` - `queryByText("Nutrir")` is null. `solution/frontend/src/components/CollapsibleBand.test.tsx:31` - `aria-expanded` false and `:34` - collapsed child is null | ✅ PASS |
| FOCO-11 WHEN a collapsed band title is activated THEN it expands, and WHEN activated again THEN it collapses | Toggle `aria-expanded` and show/hide the body | `solution/frontend/src/components/CollapsibleBand.test.tsx:48` - `toBe("true")` then `:53` - `toBe("false")` and `:54` - body is null. UI scenario 2 (`ui-evidence/02-faixa-depois-clique.png`) | ✅ PASS |
| FOCO-12 WHEN the Focar or Revisar KPI is activated THEN the matching band scrolls into place or expands | Revisar band becomes expanded. Nº Focar is a button because `VendedorStation.tsx:75` passes `onActivate` | `solution/frontend/src/stations/VendedorStation.test.tsx:111` - `getByRole("button", { name: "Nº Focar1" })`. `:124` clicks `Revisar1` and `:126` - `aria-expanded` is `"true"` and `:129` - `getByText("Qualificar conta/dados")` | ✅ PASS |
| FOCO-13 The Esfriando KPI is not a filter or an action | On the composed strips, every "Esfriando" node has `closest("button") === null` | `solution/frontend/src/stations/VendedorStation.test.tsx:109` - `expect(node.closest("button")).toBeNull()`. `solution/frontend/src/stations/GestorStation.test.tsx:97` - same on the gestor home strip and `:100` - same for "Bons esfriando" and `:132` - same on the drill strip | ✅ PASS |
| (no ID) Esfriando counts use `age_days > 106` strictly | 106 counts as 0; 107 counts as 1 | `solution/frontend/src/kpis/summary.test.ts:82` - `expect(atBoundary.esfriando).toBe(0)` and `:89` - `expect(over.esfriando).toBe(1)` | ✅ PASS |
| FOCO-14 A Focar card orders action, reason, value/age, then Estado and Esfriando | That vertical order; catalog value from `item.value` | `solution/frontend/src/components/DealCard.test.tsx:42` - `appearsBefore(action, reason)` through `:45` - `appearsBefore(age, estado)`. UI scenario 3 (`ui-evidence/03-card-assertado.png`) | ✅ PASS |
| FOCO-15 SCORE is secondary, tooltip is "posição nesta visão, 0–100", and the chrome never says percentil | That tooltip string; no percentil | `solution/frontend/src/components/DealCard.test.tsx:53` - `getAttribute("title")).toBe(SCORE_TOOLTIP)` and `:54` - `expect(SCORE_TOOLTIP).toBe("posição nesta visão, 0–100")` and `:55` - `not.toMatch(/percentil/i)`. UI scenario 3 and scenario 8 (`ui-evidence/08-chrome-assertado.png`) | ✅ PASS |
| FOCO-16 Cards in the workable queue do not show the deal stage | No "Engaging" and no "Estágio" | `solution/frontend/src/components/DealCard.test.tsx:56` - `queryByText("Estágio")` is null and `:57` - `queryByText("Engaging")` is null. UI scenario 3 | ✅ PASS |
| FOCO-17 PRIORIDADE is not a second money figure; the shown value is the catalog list price | No PRIORIDADE; `value: 1000` renders `US$ 1.000` | `solution/frontend/src/components/DealCard.test.tsx:58` - `queryByText(/PRIORIDADE/i)` is null and `:59` - value cell contains `US$ 1.000` | ✅ PASS |
| FOCO-18 WHILE `age_days > 106` the Esfriando badge is a distinct styled element | Badge with `badge-cooling` at 107; absent at 106 | `solution/frontend/src/components/DealCard.test.tsx:65` - `className).toContain("badge-cooling")` and `:69` - `queryByText("Esfriando")` is null | ✅ PASS |
| FOCO-19 Each Acompanhar item is a compact row (product, account, value, action) with SCORE in the corner | Those fields and the SCORE tooltip class | `solution/frontend/src/components/DealCard.test.tsx:111` - `getByText("GTX Pro")` through `:117` - tooltip equals `SCORE_TOOLTIP` | ✅ PASS |
| (no ID) A Revisar item shows why it is parked (missing account / missing date) and the action, and does not show SCORE | "sem conta" or "sem data", action "Qualificar conta/dados", no SCORE | `solution/frontend/src/components/ReviewRow.test.tsx:31` - `getByText("sem conta")` and `:33` - `not.toMatch(/SCORE/i)`. `:42` - `getByText("sem data")` and `:44` - `not.toMatch(/SCORE/i)`. UI scenario 3 (`ui-evidence/03-card-depois-revisar.png`) | ✅ PASS |
| FOCO-20 IF the agent is empty THEN the empty state tells the user to pick another vendedor, not a generic alert | "Este nome não tem carteira. Escolha outro vendedor." and role `status`, not `alert` | `solution/frontend/src/components/EmptyState.test.tsx:13` - `toBe("Este nome não tem carteira. Escolha outro vendedor.")` and `:16` - `queryByRole("alert")` is null. `solution/frontend/src/stations/VendedorStation.test.tsx:141` repeats that string for agent Ghost. UI scenario 4 (`ui-evidence/04-vazio-fantasma-assertado.png`) | ✅ PASS |
| FOCO-21 IF the workable queue is empty but Revisar has items THEN Focar's empty state points at those N items | "Nada trabalhável. N em Revisar." | `solution/frontend/src/stations/VendedorStation.test.tsx:160` - `toBe("Nada trabalhável. 1 em Revisar.")`. `solution/frontend/src/components/EmptyState.test.tsx:21` - `toBe("Nada trabalhável. 4 em Revisar.")` | ✅ PASS |
| FOCO-22 IF the manager slice has no sellers THEN the copy is "nenhum vendedor neste gestor/escritório" | That sentence | `solution/frontend/src/stations/GestorStation.test.tsx:163` - `toBe("nenhum vendedor neste gestor/escritório")`. UI scenario 4 (`ui-evidence/04-vazio-gestor-assertado.png`) | ✅ PASS |
| FOCO-23 IF export fails THEN an error is shown instead of a silent failure | Visible `alert`, not an uncaught throw | `solution/frontend/src/components/ExportButton.test.tsx:81` - `findByRole("alert")).textContent).toBe("Não foi possível exportar o CSV")` | ✅ PASS |
| FOCO-24 WHEN `/gestor` has no `agente` THEN the hero is the per-agent rollup (na fila, valor, esfriando, bons esfriando) | Seller row and those columns, no deal bands | `solution/frontend/src/stations/GestorStation.test.tsx:92` - `getByRole("button", { name: "Anna Snelling" })` and `:95` - `queryByRole("button", { name: "Focar (1)" })` is null. `solution/frontend/src/components/RollupTable.test.tsx:41` - headers equal `["Vendedor", "Na fila", "Valor", "Esfriando", "Bons esfriando"]`. UI scenario 5 (`ui-evidence/05-rollup-assertado.png`) | ✅ PASS |
| FOCO-25 WHEN the gestor home loads THEN the strip shows Valor do time, Na fila, Esfriando, and Bons esfriando, summed from the rollup | Sums of `expected_value_sum`, `queued_count`, `cooling_count`, `good_deals_cooling` | `solution/frontend/src/kpis/summary.test.ts:115` - `toEqual({ valorTime: 1500, naFila: 10, esfriando: 4, bonsEsfriando: 1 })`. `solution/frontend/src/stations/GestorStation.test.tsx:89` - `getByText("Valor do time")`. UI scenario 5 (`ui-evidence/05-rollup-assertado.png`) | ✅ PASS |
| FOCO-26 WHILE the gestor home shows only the rollup THEN the full team queue is not rendered | No Focar band and no export | `solution/frontend/src/stations/GestorStation.test.tsx:93` - export button is null and `:95` - Focar band button is null. UI scenario 5 | ✅ PASS |
| FOCO-27 Every displayed rollup column has a header cell, including Bons esfriando | Header list matches the five columns; Anna's cells are 8, US$ 48.210, 3, 1 | `solution/frontend/src/components/RollupTable.test.tsx:41` - `expect(headers).toEqual(["Vendedor", "Na fila", "Valor", "Esfriando", "Bons esfriando"])` and `:44` - `getByText("8")` through `:47` - `getByText("1")` | ✅ PASS |
| FOCO-28 WHEN a seller row is activated THEN the hero becomes that seller's bands and `agente` is set on `/gestor` | `navigate` receives `station: "gestor"` and `agente: "Anna Snelling"`; Focar band appears | `solution/frontend/src/stations/GestorStation.test.tsx:115` - `toHaveBeenCalledWith(expect.objectContaining({ station: "gestor", agente: "Anna Snelling" }))` and `:129` - `getByRole("button", { name: "Focar (1)" })`. UI scenario 6 (`ui-evidence/06-drill-fila-assertado.png`) | ✅ PASS |
| FOCO-29 WHILE the drill is active the strip shows that seller's numbers | Valor em Focar equals that seller's Focar value (fixture US$ 2.000) | `solution/frontend/src/stations/GestorStation.test.tsx:127` - `getByText("Valor em Focar")` and `:128` - `getAllByText("US$ 2.000")`. UI scenario 6 (`ui-evidence/06-drill-fila-assertado.png`) | ✅ PASS |
| FOCO-30 WHEN the user leaves the drill THEN `agente` is cleared, the rollup returns, and the path stays `/gestor` | `navigate` station stays `gestor`, `agente` is undefined, gestor slice kept | `solution/frontend/src/stations/GestorStation.test.tsx:150` - `station).toBe("gestor")` and `:151` - `gestor).toBe("Dustin Brinkmann")` and `:152` - `agente).toBeUndefined()`. UI scenario 6 (`ui-evidence/06-drill-rollup-assertado.png`) | ✅ PASS |
| FOCO-31 Exportar CSV appears only where a deal queue is on screen | Button on the vendedor station and on the gestor drill | `solution/frontend/src/stations/VendedorStation.test.tsx:107` - `getByRole("button", { name: "Exportar CSV" })`. `solution/frontend/src/stations/GestorStation.test.tsx:130` - same button after drill. UI scenario 7 (`ui-evidence/07-export-depois-drill.png`) | ✅ PASS |
| FOCO-32 WHILE the gestor home is rollup-only THEN Exportar CSV is absent | Button is null, including the empty rollup | `solution/frontend/src/stations/GestorStation.test.tsx:93` and `:166` - `queryByRole("button", { name: "Exportar CSV" })` is null. UI scenario 7 (`ui-evidence/07-export-home-antes.png`) | ✅ PASS |
| FOCO-33 WHEN the user exports THEN the CSV matches the current queue's order and columns | Request uses the active agent; downloaded text equals the response | `solution/frontend/src/components/ExportButton.test.tsx:63` - `toBe("/api/export.csv?agent=Anna+Snelling&manager=Dustin+Brinkmann&office=Central")` and `:68` - downloaded text equals the response. UI scenario 7 (`ui-evidence/07-export-assertado.png`) | ✅ PASS |
| FOCO-34 The chrome shows "Visão em 31/12/2017" | That exact anchor | `solution/frontend/src/components/AppShell.test.tsx:35` - `getByText(TEMPORAL_ANCHOR)` and `:36` - `expect(TEMPORAL_ANCHOR).toBe("Visão em 31/12/2017")`. UI scenario 8 (`ui-evidence/08-chrome-assertado.png`) | ✅ PASS |
| FOCO-35 No decorative gradients, glassmorphism, or one icon per KPI; the strip is text + number | No svg/img in the strip; `index.css` has no `gradient`, `backdrop-filter`, or `glassmorphism` | `solution/frontend/src/components/SituationStrip.test.tsx:28` - `querySelector("svg")` is null and `:29` - `querySelector("img")` is null. UI scenario 8 (`ui-evidence/08-chrome-assertado.png`) | ✅ PASS |
| FOCO-36 Portuguese user-facing labels; identifiers, JSON keys, and API routes stay English | PT paths and `US$` pt-BR; API uses `agent`, `manager`, `office` | `solution/frontend/src/routing/route.test.ts:36` - `toBe("/vendedor")`. `solution/frontend/src/format/money.test.ts:8` - `expect(formatValue(1000)).toBe("US$ 1.000")`. `solution/frontend/src/routing/useViewData.test.tsx:69` - `toContain("/api/queue?view=mine&agent=Anna+Snelling")`. UI scenario 8 | ✅ PASS |

**Status**: ✅ All ACs covered

**Spec-anchored check**: 38/38 ACs matched the spec outcome | 0 spec-precision gaps

---

## Discrimination Sensor

Scratch: `git worktree add` at `19adc75` under the temp directory (not `git stash`). A first run through a `node_modules` junction failed before any assertion (`Vitest failed to find the runner`), so that run was discarded and not counted. Dependencies were installed inside the worktree and the tests were re-run there. The real tree was not edited. The worktree was removed. `git status --porcelain` on the real tree matched the pre-sensor baseline.

| Mutation | File:line | Description | Killed? |
| -------- | --------- | ----------- | ------- |
| 1 | `stations/VendedorStation.tsx` Esfriando item and `stations/GestorStation.tsx` home Esfriando item | Added `onActivate` so SituationStrip renders those KPIs as `<button>`. Drill strip left unchanged | ✅ Killed. `VendedorStation.test.tsx:109` expected `closest("button")` null and received `<button>Esfriando</button>`. `GestorStation.test.tsx:97` failed the same way on the home strip |

**Sensor depth**: lightweight (1 behavior-level mutation, two composition sites)
**Killed**: 1/1

---

## Interactive UAT Results (if performed)

Interactive UAT with the user was not run in this verifier session. The harness UI lane already executed the eight Independent Tests. Those results are evidence in the table above.

| # | Test | Result | Details |
| - | ---- | ------ | ------- |
| 1 | Estações | ✅ Pass | UI lane. Redirect, rail, reload |
| 2 | Faixa | ✅ Pass | UI lane. Four numbers, Focar open, Acompanhar expands |
| 3 | Card | ✅ Pass | UI lane. Order, tooltip, no stage, Revisar without SCORE |
| 4 | Vazios | ✅ Pass | UI lane. Ghost agent and empty manager slice |
| 5 | Rollup | ✅ Pass | UI lane. Headers and team strip |
| 6 | Drill | ✅ Pass | UI lane. Seller queue and Voltar ao time |
| 7 | Export | ✅ Pass | UI lane. Hidden on the rollup; CSV after drill |
| 8 | Chrome | ✅ Pass | UI lane. Anchor, text+number strip, Portuguese |

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ `19adc75` adds assertions only |
| Surgical changes | ✅ Two test files; no product UI change in the fix |
| No scope creep | ✅ No new endpoint; motor untouched |
| Matches patterns | ✅ Vitest + Testing Library, composed station render |
| Spec-anchored outcome check (asserted values match spec) | ✅ FOCO-13 now asserts the composed strip, not props the test invents |
| Per-layer Coverage Expectation met (domain 1:1 ACs; routes happy+edge+error) | ✅ Station tests lock the Esfriando negative rule |
| Every test maps to a spec requirement - no unclaimed tests | ✅ New assertions map to FOCO-13 |
| Documented guidelines followed: `AGENTS.md`, `.cursor/rules/validation-lane.mdc` | ✅ UI lane used Playwright MCP; this verifier did not add a committed Playwright suite |

---

## Edge Cases

- [x] Unknown or ghost `agente`: teaching empty state. `VendedorStation.test.tsx:141` and UI scenario 4.
- [x] Band with zero items: title interpolates the count (`CollapsibleBand.tsx` count in the title) and an empty Focar list renders the only-Revisar empty state (`VendedorStation.test.tsx:160`).
- [x] Single workable deal stays in Focar: `VendedorStation.test.tsx:95` expects `Focar (1)` open with that deal's action visible.
- [x] Empty rollup: "nenhum vendedor neste gestor/escritório" and no export. `GestorStation.test.tsx:163` and `:166`.
- [x] Back/forward updates station and slice from the URL. `useViewRoute.test.tsx:66` - station returns to `vendedor` and `:67` - agente is `Anna Snelling` after `popstate`.

---

## Gate Check

- **Gate command**: `npm --prefix frontend test -- --run` (cwd `submissions/joao-luiz/solution`)
- **Result**: 70 passed, 0 failed, 0 skipped
- **Test files**: 21 passed
- **19adc75 delta**: no test cases added or removed; four assertion lines in `VendedorStation.test.tsx` and nine in `GestorStation.test.tsx`
- **Skipped tests**: none
- **Failures**: none on the unmutated tree
- **Integrity**: the new assertions are stricter (`closest("button") === null` on the composed strip). No assertion was weakened to make the gate pass
- **Backend lane**: skipped. The Test Coverage Matrix has no pytest row

---

## Fix Plans (if issues found)

None.

---

## Requirement Traceability Update

Statuses below belong in this report. `spec.md` was not edited.

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| FOCO-01 .. FOCO-36 | Implementing, Pending, or Needs Fix | ✅ Verified |
| Esfriando `age_days > 106` (no ID) | not in the ID table | ✅ Verified |
| Revisar row without SCORE (no ID) | not in the ID table | ✅ Verified |

---

## Summary

**Overall**: ✅ Ready

**Spec-anchored check**: 38/38 ACs matched the spec outcome | 0 spec-precision gaps
**Sensor**: 1/1 mutations killed
**Gate**: 70 passed, 0 failed

**What works**: Addressable stations, Focar as the open hero, collapsed Acompanhar/Revisar, card order, empty states, rollup, drill, contextual export, and the operational-desk chrome. The Esfriando KPI stays inert on the vendedor strip and on the gestor home strip. The UI lane passed all eight Independent Tests.

**Issues found**: none

**Next steps**: none for this feature
