# Repassar deal Validation

**Date**: 2026-10-09
**Spec**: `.specs/features/repassar-deal/spec.md`
**Diff range**: `2689e83^..5385bb5` (HEAD `5385bb5`)
**Verifier**: independent sub-agent (author ≠ verifier)

---

## Task Completion

T1–T10 are checked and committed on `submission/joao-luiz`. No task is blocked or partial.

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1 | ✅ Done | `from_agent` and in-memory `reassign_deal` |
| T2 | ✅ Done | Same-office candidates, owner omitted |
| T3 | ✅ Done | `assign` refuses without changing the owner or the CSVs |
| T4 | ✅ Done | `POST /api/handoff` |
| T5 | ✅ Done | `GET /api/handoff/candidates` |
| T6 | ✅ Done | `from_agent` on the queue; restart restores the CSV owner |
| T7 | ✅ Done | Client post and candidate fetch |
| T8 | ✅ Done | Confirm dialog, cooling copy, empty office |
| T9 | ✅ Done | Button visibility and "Veio de" |
| T10 | ✅ Done | Drill wires the dialog and refetches |

---

## Spec-Anchored Acceptance Criteria

### P1: Passar um negócio para um colega do mesmo escritório

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| WHEN `/gestor` drill activates "Passar para colega" on Focar or Acompanhar THEN list same-office `sales_agent` names and omit the owner | Names that share the deal's `regional_office`, current owner absent | `backend/tests/unit/test_candidates.py:37` - `eligible_candidates(deals, "opp-1") == ("Bruno",)`; `backend/tests/e2e/test_handoff.py:162` - `deal.sales_agent not in names` and `team[name][1] == deal.regional_office`; `frontend/src/components/HandoffDialog.test.tsx:46` - radios "Bruno" and "Otto". UI IT1: dialog lists same-office colleagues (`ui-evidence/01-repasse-focar-colega-selecionado.png`) | ✅ PASS |
| WHEN the user confirms one listed colleague THEN that `opportunity_id` is assigned to the colleague and exactly one deal keeps that id | One deal, `sales_agent` is the chosen colleague | `backend/tests/unit/test_assign.py:57` - `sum(item.opportunity_id == "opp-1") == 1` and `moved.sales_agent == "Bruno"`; `backend/tests/e2e/test_handoff.py:69` - same count of that id is 1; `frontend/src/stations/GestorStation.test.tsx:280` - POST body `{opportunity_id: "OPP-1", to_agent: "Bruno"}` | ✅ PASS |
| WHEN assignment succeeds THEN the deal leaves the previous queue and appears on the colleague's queue with the same id, product, account, list value, and `age_days` | Those five fields match the pre-handoff item; id absent from the origin queue | `backend/tests/e2e/test_handoff.py:60` - origin ids exclude the deal; `:62` - `moved["product"] == before["product"]`; `:63` account; `:64` value; `:65` `age_days`. UI IT1: NSX4NR40 left Anna (19→18, US$ 37.641→32.159) and appeared on Cecily Lampkin (`ui-evidence/01-repasse-focar-origem-assertado.png`, `ui-evidence/01-repasse-focar-destino-assertado.png`) | ✅ PASS |
| WHEN assignment succeeds THEN `manager` and `regional_office` come from that colleague's `sales_teams` row | Stored manager and office equal the roster row for the colleague | `backend/tests/e2e/test_handoff.py:67` - `stored.manager == colleague_manager` and `:68` `stored.regional_office == colleague_office`, with the roster read from `sales_teams` in `backend/app/api/handoff.py:54`. Unit stand-in: `backend/tests/unit/test_assign.py:60` - `moved.manager == "Otto"` and `regional_office == "East"` | ✅ PASS |
| WHEN assignment succeeds THEN catalog list value and age stay unchanged and SCORE is the percentile of the destination view | `value` and `age_days` unchanged; score equals `percentile_scores` of the destination agent's priorities | `backend/tests/unit/test_assign.py:83` - `moved.value == 1000`; `:84` - `age_days(moved.engage_date) == before_age`; `:101` - `listed.score == expected["opp-1"]` where `expected` is the destination-view percentile | ✅ PASS |
| The system keeps the total number of deals unchanged across a handoff | `len(deals)` before equals `len(deals)` after | `backend/tests/unit/test_reassign.py:88` - `len(result) == len(deals) == 2`; `backend/tests/e2e/test_handoff.py:68` - `len(client.app.state.deals) == before_count`. UI IT1: Na fila stayed 501 and the deal total stayed 8800 | ✅ PASS |
| WHEN the user cancels the colleague list THEN `sales_agent` stays unchanged | No handoff POST; the deal remains with the original owner | `frontend/src/components/HandoffDialog.test.tsx:78` - `postHandoff` not called; `frontend/src/stations/GestorStation.test.tsx:239` - no fetch with method POST, deal text still present. UI IT1: NSX4NR40 stayed on Anna Snelling after Cancelar (`ui-evidence/01-repasse-focar-cancelado.png`) | ✅ PASS |
| "Passar para colega" only on the gestor drill for Focar and Acompanhar, never on the vendedor station or on Revisar | Button present for those two bands in the drill; absent on vendedor and on Revisar rows | `frontend/src/stations/GestorStation.test.tsx:198` - one button on Focar; `:202` - two after Acompanhar opens; `:207` - still two after Revisar opens; `frontend/src/stations/VendedorStation.test.tsx:105` and `:126` - `queryByRole("button", { name: "Passar para colega" })` is null. UI IT2: Revisar stayed at 93 with no Passar button (`ui-evidence/02-recusas-revisar-depois.png`) | ✅ PASS |
| WHILE the confirm dialog is open for `age_days > 106` THEN the text is "Este negócio está esfriando." | That exact sentence is in the open dialog | `frontend/src/components/HandoffDialog.test.tsx:60` - `findByText("Este negócio está esfriando.")` at age 107. UI IT1: dialog showed that sentence for age 139 (`ui-evidence/01-repasse-focar-dialogo-esfriando.png`) | ✅ PASS |

### P1: Recusa não apaga o negócio

The four refusal sentences are asserted on the domain result and on `detail`. Playwright IT2 did not paint them in the dialog: the dialog only lists valid colleagues, so the lane read the copy from `POST /api/handoff` (page fetch). The dialog's alert renders that `detail` when a confirm fails. Screenshot evidence for IT2 is the owner left in place, not the sentence on screen.

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| IF the target agent is unknown THEN reject, keep the original `sales_agent`, and show "Colega não encontrado" | Owner unchanged; that exact sentence | `backend/tests/unit/test_assign.py:109` - `_refused(..., "Ninguém", "Colega não encontrado")` keeps `sales_agent == "Ana"`; `backend/tests/e2e/test_handoff.py:86` - `detail == "Colega não encontrado"` and status 404; `frontend/src/components/HandoffDialog.test.tsx:90` - alert `textContent` is "Colega não encontrado" and confirm is not called. UI IT2 page fetch: 7FZ9CBZ3 + "Agente Inexistente" → 404 with that sentence; deal stayed on Anna (`ui-evidence/02-recusas-anna-antes.png`) | ✅ PASS |
| IF the target is the current owner THEN reject, keep the original `sales_agent`, and show "Este negócio já está com essa pessoa" | Owner unchanged; that exact sentence | `backend/tests/unit/test_assign.py:113` - message is that sentence and `sales_agent` stays "Ana"; `backend/tests/e2e/test_handoff.py:104` - `detail` equals that sentence and status 409. UI IT2 page fetch: same deal + "Anna Snelling" → 409 with that sentence. The dialog did not render it | ✅ PASS |
| IF the target belongs to a different `regional_office` THEN reject, keep the original `sales_agent`, and show "Colega de outro escritório" | Owner unchanged; that exact sentence | `backend/tests/unit/test_assign.py:117` - message is that sentence; `backend/tests/e2e/test_handoff.py:127` - `detail` equals that sentence and status 422. UI IT2 page fetch: "Boris Faz" (East) → 422 with that sentence. The dialog did not render it | ✅ PASS |
| IF the opportunity is Won, Lost, Prospecting, or has no account or no `engage_date` THEN reject, keep the original `sales_agent`, and show "Este negócio não está na fila trabalhável" | Each of those five shapes keeps the owner and returns that sentence | `backend/tests/unit/test_assign.py:131` - Won, Lost, Prospecting, `account=None`, and `engage_date=None` all `_refused` with that sentence; `backend/tests/e2e/test_handoff.py:146` - a Won deal returns that `detail` and status 422. UI IT2 page fetch: Revisar LAYVBSH4 → 422 with that sentence; Revisar count stayed 93 | ✅ PASS |
| The system does not modify `accounts.csv`, `products.csv`, `sales_teams.csv`, or `sales_pipeline.csv` | Bytes of those four files are unchanged after a successful assign | `backend/tests/integration/test_handoff_disk.py:47` - `after[name] == before[name]` for each source CSV | ✅ PASS |

### P1: Restart devolve o snapshot

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| WHEN the API process starts THEN every deal is owned as in the source CSVs | A new `create_app()` returns the handed-off id to the CSV owner | `backend/tests/integration/test_handoff_restart.py:61` - `owner.sales_agent == deal.sales_agent` and `:64` the id is absent from the colleague queue. UI IT3: after restarting `solution-api-1`, NSX4NR40 was back on Anna, Anna na fila 19 / US$ 37.641, Cecily 3 / US$ 6.841 (`ui-evidence/03-restart-anna-assertado.png`, `ui-evidence/03-restart-cecily-assertado.png`) | ✅ PASS |
| WHEN the same `opportunity_id` is passed to a second colleague in the same process THEN exactly one deal with that id remains | One row for that id, owned by the second colleague | `backend/tests/unit/test_reassign.py:131` - `len(matches) == 1` after Bruno then Carla; `:133` - `sales_agent == "Carla"` | ✅ PASS |
| The system does not write `handoffs.jsonl` or any other owner overlay | `data/` file set unchanged and `handoffs.jsonl` absent | `backend/tests/integration/test_handoff_disk.py:44` - `after.keys() == before.keys()`; `:45` - `"handoffs.jsonl" not in after`. UI IT3: `data/` had only the source CSVs, no `handoffs.jsonl`, no overlay | ✅ PASS |

### P2: Rastro na fila

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| WHEN a passed deal is rendered THEN show "Veio de {from_agent}" using the previous owner | Visible text is "Veio de" plus the previous owner | `frontend/src/components/DealCard.test.tsx:92` - `getByText("Veio de Ana")`; `backend/tests/integration/test_handoff_restart.py:44` - `moved["from_agent"] == deal.sales_agent`. UI IT4: Cecily's card showed "Veio de Anna Snelling" (`ui-evidence/04-veio-de-antes-restart.png`) | ✅ PASS |
| `from_agent` lives only on the in-memory deal for the current process | After a new process, `from_agent` is null and the badge is gone | `backend/tests/integration/test_handoff_restart.py:62` - `owner.from_agent is None` and `:63` - restored queue `from_agent` is null. UI IT4: after restart the badge is gone and the deal is back on Anna with no "Veio de" (`ui-evidence/03-restart-anna-assertado.png`) | ✅ PASS |

**Status**: ✅ All 19 ACs covered

---

## Discrimination Sensor

Scratch: `git worktree add` at a temp path on HEAD `5385bb5`. Mutations never touched the real worktree. `git stash` was not used. After `git worktree remove --force`, `git status --porcelain` matched the pre-sensor baseline.

| Mutation | File:line | Description | Killed? |
| -------- | --------- | ----------- | ------- |
| 1 | `backend/app/handoffs/service.py:75` | Same-owner guard forced false (`if False and to_agent == deal.sales_agent`) | ✅ Killed. `test_repa_11_current_owner_keeps_the_owner`, `test_repa_16_second_assign_to_the_same_colleague_stays_one_deal`, and e2e `test_repa_11_same_owner_is_409_and_keeps_the_owner` failed (ok True / HTTP 200) |
| 2 | `backend/app/ingestion/repository.py:60` | `reassign_deal` appended the updated tuple onto the original (`return deals + updated`) | ✅ Killed. `test_repa_06_reassign_keeps_the_deal_count` saw len 4, `test_repa_16_second_reassign_of_the_same_id_stays_one_deal` saw 4 rows for one id, `test_repa_02_assign_moves_the_one_deal` saw len 4 |
| 3 | `frontend/src/components/HandoffDialog.tsx:66` | Cooling comparison `ageDays > 106` changed to `ageDays >= 106` | ✅ Killed. `HandoffDialog.test.tsx:67` found "Este negócio está esfriando." at age 106 |

**Sensor depth**: lightweight (3 behavior-level mutants)
**Result**: 3/3 killed, PASS

---

## Interactive UAT Results (if performed)

No human UAT in this pass. The ui-tester lane ran the four Independent Tests on `http://127.0.0.1:8080`. Recorded here as that lane's evidence.

| # | Test | Result | Details |
| --- | ---- | ------ | ------- |
| 1 | IT1 Focar, cancel, then confirm | ✅ Pass | NSX4NR40 stayed on Anna after Cancelar. Confirm moved it to Cecily Lampkin. Counts and US$ totals moved with that one deal. Dialog included the cooling sentence (age 139) |
| 2 | IT2 refusals | ✅ Pass | Owner unchanged. Copy asserted on the API body via page fetch, not inside the dialog. Revisar had no Passar button |
| 3 | IT3 restart snapshot | ✅ Pass | New API process put NSX4NR40 back on Anna. `data/` had no overlay |
| 4 | IT4 Veio de, then restart clears it | ✅ Pass | Badge "Veio de Anna Snelling" before restart; gone after, deal back on Anna |

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ |
| Surgical changes | ✅ |
| No scope creep | ✅ |
| Matches patterns | ✅ |
| Spec-anchored outcome check (asserted values match spec) | ✅ |
| Per-layer Coverage Expectation met (domain 1:1 ACs; routes happy+edge+error) | ✅ |
| Every test maps to a spec requirement - no unclaimed tests | ✅ |
| Documented guidelines followed: `AGENTS.md`, `solution/pytest.ini`, coverage matrix in `tasks.md` | ✅ |

The diff adds the handoff service, two routes, `from_agent` on the deal and the queue item, and the drill dialog. `VendedorStation` only threads an optional `onPass` so the seller station does not render the button. No overlay file, no scoring-formula change, no batch handoff. Domain tests assert the spec sentences and the single-id invariant. `POST /api/handoff` covers 200 plus 404, 409, and 422. Spot-check of the success story: `test_repa_02_post_moves_the_deal_between_queues` asserts the five preserved fields, the roster manager and office, and a deal count that does not change.

---

## Edge Cases

- [x] No other colleague in the office: `frontend/src/components/HandoffDialog.test.tsx:98` shows "Nenhum colega neste escritório", hides Confirmar, and does not post
- [x] Same colleague confirmed twice: `backend/tests/unit/test_assign.py:153` - second `assign` is not ok, message is "Este negócio já está com essa pessoa", and `len(deals) == 1`
- [x] `age_days` equal to 106: `frontend/src/components/HandoffDialog.test.tsx:67` - cooling sentence is null
- [x] Owner with no `regional_office`: `backend/tests/unit/test_assign.py:120` - refused with "Colega de outro escritório" and the original owner kept; candidates are empty at `backend/tests/unit/test_candidates.py:59`

---

## Gate Check

- **Gate command**: `python -m pytest backend/tests -q` inside `solution-api:latest` (cwd equivalent `/app`, `PYTHONPATH=/app/backend`). Host `.venv` was not used. Windows WDAC blocks pandas there.
- **Result**: 96 passed, 0 failed, 0 skipped
- **Pytest breakdown** (backend-tester lane, same run): unit 70, integration 9, e2e 17
- **Test count before feature** (`2689e83^`): 68 pytest functions
- **Test count after feature** (`5385bb5`): 96 pytest functions
- **Delta**: +28 pytest
- **Skipped tests**: none
- **Failures**: none
- **Frontend**: vitest count moved from 56 to 70. A parallel host run hit four 5s timeouts (first test in `HandoffDialog`, `RollupTable`, `VendedorStation`, `GestorStation`) while the machine was loaded. Those four files passed 17/17 on an immediate retry with a 20s timeout. The timeouts are host load, not a product failure. The cooling, cancel, refusal alert, empty-office, button, and confirm tests passed in that retry.

---

## Fix Plans (if issues found)

None.

---

## Requirement Traceability Update

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| REPA-01 | Implementing | ✅ Verified |
| REPA-02 | Implementing | ✅ Verified |
| REPA-03 | Implementing | ✅ Verified |
| REPA-04 | Implementing | ✅ Verified |
| REPA-05 | Implementing | ✅ Verified |
| REPA-06 | Implementing | ✅ Verified |
| REPA-07 | Implementing | ✅ Verified |
| REPA-08 | Implementing | ✅ Verified |
| REPA-09 | Implementing | ✅ Verified |
| REPA-10 | Implementing | ✅ Verified |
| REPA-11 | Implementing | ✅ Verified |
| REPA-12 | Implementing | ✅ Verified |
| REPA-13 | Implementing | ✅ Verified |
| REPA-14 | Implementing | ✅ Verified |
| REPA-15 | Implementing | ✅ Verified |
| REPA-16 | Implementing | ✅ Verified |
| REPA-17 | Implementing | ✅ Verified |
| REPA-18 | Implementing | ✅ Verified |
| REPA-19 | Implementing | ✅ Verified |

---

## Summary

**Overall**: ✅ Ready

**Spec-anchored check**: 19/19 ACs matched spec outcome | 0 spec-precision gaps
**Sensor**: 3/3 mutations killed
**Gate**: 96 passed, 0 failed

**What works**: A gestor drill can pass one Focar or Acompanhar deal to a same-office colleague. The id stays unique, the catalog value and age stay put, and SCORE is the destination view's percentile. Invalid targets keep the original owner and return the spec sentence. Restart reloads the CSV owners and drops `from_agent`. The destination card shows "Veio de {previous owner}" only in that process.

**Issues found**: none

**Next steps**: none for this feature
