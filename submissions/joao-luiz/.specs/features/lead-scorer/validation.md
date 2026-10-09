# Lead Scorer Validation

**Date**: 2026-10-09
**Spec**: `.specs/features/lead-scorer/spec.md`
**Diff range**: `4aed364..a0f481e` (HEAD `a0f481e`, T27)
**Verifier**: independent sub-agent (author ≠ verifier)

---

## Task Completion

All 27 Execute tasks are checked (104/104 boxes) and committed on `submission/joao-luiz`.

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1 | ✅ Done | FastAPI factory and frozen constants |
| T2 | ✅ Done | CSV loader |
| T3 | ✅ Done | Aliases and quality log |
| T4 | ✅ Done | Normalized deal repository |
| T5 | ✅ Done | Age against 2017-12-31 |
| T6 | ✅ Done | Urgency curve |
| T7 | ✅ Done | Priority = value × urgency |
| T8 | ✅ Done | Confidence |
| T9 | ✅ Done | Esfriando flag |
| T10 | ✅ Done | Filter and Revisar split |
| T11 | ✅ Done | Percentile SCORE |
| T12 | ✅ Done | Estado Focar / Acompanhar |
| T13 | ✅ Done | Portuguese reason and action |
| T14 | ✅ Done | Ordered queue |
| T15 | ✅ Done | Manager rollup |
| T16 | ✅ Done | GET /api/agents |
| T17 | ✅ Done | GET /api/queue |
| T18 | ✅ Done | GET /api/rollup |
| T19 | ✅ Done | GET /api/export.csv |
| T20 | ✅ Done | GET /api/quality-log |
| T21 | ✅ Done | Frontend client and filters |
| T22 | ✅ Done | Queue list and deal card |
| T23 | ✅ Done | Revisar and empty state |
| T24 | ✅ Done | Manager rollup view |
| T25 | ✅ Done | Export button |
| T26 | ✅ Done | Docker Compose and local commands |
| T27 | ✅ Done | Determinism |

---

## Spec-Anchored Acceptance Criteria

Outcomes below are the spec's WHEN/THEN text plus the frozen assumptions in `spec.md` (urgency knots and floor 0.35, percentile formula, ceil(0.20×N), action copy, confidence bands). UI rows also cite the Playwright MCP lane (base `http://127.0.0.1:8080`, the Compose web port).

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| LEAD-01 WHEN the seller selects their name THEN only Engaging deals with a non-empty account, ordered by SCORE descending | Engaging + account, SCORE desc, top score first | `solution/backend/tests/e2e/test_queue.py:30` - `assert all(item["deal_stage"] == "Engaging" for item in items)` and `:29` scores sorted descending and `:31` every account truthy. UI lane scenario 1: Anna Snelling, 19 Engaging cards, SCORE 100 first (`ui-evidence/01-fila-vendedor-assertado.png`) | ✅ PASS |
| LEAD-02 The system excludes Won, Lost, and Prospecting from the workable queue | Those stages never appear as workable | `solution/backend/tests/unit/test_query.py:61` - `assert ids.isdisjoint({"won", "lost", "pros", "no-account"})`. UI lane scenario 2: workable queue has no Won/Lost/Prospecting (`ui-evidence/02-exclusoes-revisar-assertado.png`) | ✅ PASS |
| LEAD-03 WHEN ordered by SCORE THEN the highest PRIORITY (VALOR × URGÊNCIA) is first | First item is the max priority in the view, SCORE 100, ESTADO Focar | `solution/backend/tests/unit/test_query.py:53` - `assert [item.opportunity_id for item in view.items] == ["high", "low", "old"]` and `:54` `assert view.items[0].score == 100` | ✅ PASS |
| LEAD-04 WHEN a deal is shown THEN product, account, list value, stage, days, SCORE, ESTADO, and CONFIANÇA are displayed | Those eight fields, with values from the deal (complete GTX Pro with closed count under 100 is Média) | `solution/backend/tests/unit/test_query.py:66` - `assert item.product == "GTX Pro"` through `:73` `assert item.confidence == "Média"`. UI labels in `solution/frontend/src/components/QueueList.test.tsx:43` - `expect(screen.getByText(label)).toBeTruthy()` | ✅ PASS |
| LEAD-05 WHEN a deal is shown THEN a Portuguese reason and a suggested action are displayed | Within cycle: "Avançar proposta"; age > 106: "Reengajar antes de esfriar"; Revisar: "Qualificar conta/dados" | `solution/backend/tests/unit/test_explain.py:8` - `assert text.reason == "GTX Pro · US$ 4.821 · 40 dias no funil · dentro do ciclo"` and `:9` `assert text.action == "Avançar proposta"`. UI lane scenario 1, same screenshot | ✅ PASS |
| LEAD-06 PRIORITY = VALOR × URGÊNCIA, VALOR = catalog sales_price after alias normalization | `priority(1000, 1.0) == 1000`; former GTXPro rows keep price 4821 | `solution/backend/tests/unit/test_priority.py:9` - `assert priority(1000, 1.0) == 1000`. Price: `solution/backend/tests/unit/test_repository.py:46` - `assert {deal.value for deal in matched} == {4821}` | ✅ PASS |
| LEAD-07 URGÊNCIA rises to the Won median (57), stays high through the Won p90 (106), then decays and never reaches zero | Day 0 = 0.5, day 57 = 1.0, day 106 = 1.0, day 212 and beyond = 0.35, missing age is None | `solution/backend/tests/unit/test_urgency.py:13` - `assert urgency(57) == pytest.approx(1.0)` and `:18` `assert urgency(106) == pytest.approx(1.0)` and `:26` `assert urgency(212) == pytest.approx(0.35)` and `:32` `assert urgency(None) is None` | ✅ PASS |
| LEAD-08 WHEN computing age THEN today is 2017-12-31 | `TODAY == 2017-12-31`; 2017-12-27 is 4 days | `solution/backend/tests/unit/test_age.py:10` - `assert TODAY == date(2017, 12, 31)` and `:11` `assert age_days(date(2017, 12, 27)) == 4` | ✅ PASS |
| LEAD-09 SCORE is the 0–100 percentile of PRIORITY in the current view | `100 × (count of priorities ≤ this one) / N`; N=1 → 100; ties share | `solution/backend/tests/unit/test_percentile.py:7` - `assert percentile_scores([250]) == [100]` and `:11` `assert percentile_scores([1, 2, 3, 4]) == [25, 50, 75, 100]` and `:16` `assert percentile_scores([1, 2, 2, 4]) == [25, 75, 75, 100]` | ✅ PASS |
| LEAD-10 The ranking does not use conversion probability | `priority` takes only value and urgency | `solution/backend/tests/unit/test_priority.py:22` - `assert list(priority.__code__.co_varnames) == ["value", "urgency"]` | ✅ PASS |
| LEAD-11 WHEN ingesting pipeline rows THEN GTXPro maps to GTX Pro and no deal loses its catalog price because of that alias | 1,480 GTXPro rows become GTX Pro; matched value is 4821; zero of them stay at value 0 | `solution/backend/tests/unit/test_quality.py:31` - `assert _counts(after, "GTXPro") == 0` and `solution/backend/tests/unit/test_repository.py:47` - `assert sum(deal.value == 0 for deal in matched) == 0` | ✅ PASS |
| LEAD-12 WHEN ingesting accounts THEN technolgy → technology and Philipines → Philippines | 12 sector rows and 1 location row normalized; typos gone | `solution/backend/tests/unit/test_quality.py:59` - `assert _counts(sector_after, "technolgy") == 0` and `:61` `assert _counts(location_after, "Philipines") == 0` | ✅ PASS |
| LEAD-13 WHEN a normalization is applied THEN the log records the correction type and the affected row count | Three entries: GTXPro 1480, technolgy 12, Philipines 1 | `solution/backend/tests/e2e/test_quality_log.py:19` - `assert product["correction"] == "alias GTXPro->GTX Pro"` and `:20` `assert product["affected_rows"] == 1480` | ✅ PASS |
| LEAD-14 IF a product still does not match THEN VALOR is 0 and CONFIANÇA is Baixa | Synthetic unknown product: value 0, confidence Baixa | `solution/backend/tests/unit/test_repository.py:143` - `assert deal.value == 0` and `:144` `assert deal.confidence == "Baixa"` | ✅ PASS |
| LEAD-15 WHERE an agent has no deals THEN an explicit empty state, not a portfolio | Ghost agents Carl Lin, Carol Thompson, Elizabeth Anderson, Mei-Mei Johns, Natalya Ivanova have `empty` true and `deal_count` 0 | `solution/backend/tests/e2e/test_agents.py:24` - `assert empty == GHOST_AGENTS` and `:28` `assert agent["empty"] is True`. UI lane scenario 7 (`ui-evidence/07-vazio-fantasma-assertado.png`) | ✅ PASS |
| LEAD-16 IF an open deal has no account THEN it is Revisar and out of the ordered queue | Missing account is in `revisar` and not in `workable` | `solution/backend/tests/unit/test_filter.py:38` - `assert split.workable == ()` and `:39` `assert split.revisar == (deal,)` | ✅ PASS |
| LEAD-17 IF an open deal has no engage_date THEN it is Revisar, CONFIANÇA Baixa, and no urgency is inferred | Revisar placement; level Baixa; `urgency(None) is None` | `solution/backend/tests/unit/test_filter.py:45` - `assert split.workable == ()`; `solution/backend/tests/unit/test_confidence.py:17` - `assert assessed.level == "Baixa"`; `solution/backend/tests/unit/test_urgency.py:32` - `assert urgency(None) is None` | ✅ PASS |
| LEAD-18 Revisar is presented separately from the workable queue | Disjoint ids; review estado is Revisar; action is "Qualificar conta/dados" | `solution/backend/tests/e2e/test_queue.py:43` - `assert item_ids.isdisjoint(review_ids)` and `:44` `assert all(item["estado"] == "Revisar" for item in body["revisar"])`. UI: `solution/frontend/src/components/ReviewSection.test.tsx:60` - `getByRole("region", { name: "Revisar" })` and lane scenario 2 | ✅ PASS |
| LEAD-19 WHILE age exceeds 106 days THEN the deal shows an Esfriando badge | `cooling(107)` is true; `cooling(106)` is false; the card renders the badge only above 106 | `solution/backend/tests/unit/test_cooling.py:11` - `assert cooling(107) is True`. UI: `solution/frontend/src/components/QueueList.test.tsx:63` - `expect(screen.getByText("Esfriando")).toBeTruthy()` and lane scenario 3 (`ui-evidence/03-esfriando-focar-assertado.png`) | ✅ PASS |
| LEAD-20 Age never removes a deal from the queue; it only changes urgency and the badge | Every input deal is returned; only the flag changes | `solution/backend/tests/unit/test_cooling.py:18` - `assert [(deal_id, age) for deal_id, age, _flag in flagged] == list(deals)`. The age-212 deal stays in the queue at `solution/backend/tests/unit/test_query.py:78` - `assert old.opportunity_id == "old"` | ✅ PASS |
| LEAD-21 WHEN assigning ESTADO THEN the top ceil(0.20×N) (at least 1 if non-empty) are Focar and the rest Acompanhar | N=1 → Focar; N=5 → 1 Focar; N=6 → 2 Focar | `solution/backend/tests/unit/test_estado.py:7` - `assert assign_estado([10]) == ["Focar"]` and `:18` `assert labels.count("Focar") == 2`. UI lane scenario 3: Focar count 4 = ceil(0.20×19) | ✅ PASS |
| LEAD-22 CONFIANÇA = min(completude, suporte), mapped to Alta, Média, or Baixa | Missing account or date → Baixa; closed count under 100 → Média and value unchanged; otherwise Alta | `solution/backend/tests/unit/test_confidence.py:10` - `assert assessed.level == "Baixa"`; `:33` `assert assessed.level == "Média"` and `:34` `assert assessed.value == 26768`; `:24` `assert assessed.level == "Alta"` | ✅ PASS |
| LEAD-23 WHEN the user switches meus-deals and time THEN SCORE is recomputed on the new view | Same priority scores 100 alone and 50 beside a higher one; at least one real deal changes score between Anna's book and her team | `solution/backend/tests/unit/test_percentile.py:20` - `assert percentile_scores([10]) == [100]` and `:21` `assert percentile_scores([10, 20]) == [50, 100]`. API: `solution/backend/tests/e2e/test_queue.py:69` - `assert changed`. UI lane scenario 4: Groovestreet 89 → 94 (`ui-evidence/04-troca-de-visao-assertado.png`) | ✅ PASS |
| LEAD-24 Filters by sales agent, manager, and regional office | Each filter keeps only that agent, manager, or office, in both sections | `solution/backend/tests/unit/test_filter.py:85` - `assert by_agent.workable == (mine, other_manager, other_office)` and `:89` manager and `:93` office. UI lane scenario 4: Time+East empties the view (`ui-evidence/04-troca-de-visao-escritorio.png`) | ✅ PASS |
| LEAD-25 WHEN the user exports THEN the CSV matches the filtered view: same deals, order, and displayed columns | Header equals the queue columns; each row equals that item's fields | `solution/backend/tests/e2e/test_export.py:36` - `assert rows[0] == DISPLAYED_COLUMNS` and `:40` `assert row == [str(item[column]) for column in DISPLAYED_COLUMNS]`. UI lane scenario 5: 19 lines, 0 mismatches (`ui-evidence/05-export-vs-ui-assertado.png`) | ✅ PASS |
| LEAD-26 WHEN the user switches to manager THEN the rollup shows, per agent, queued count, summed value, and esfriando count | Ana: 2 deals, value 1100, 1 cooling; Bruno: 1 deal, value 50, 0 cooling | `solution/backend/tests/unit/test_rollup.py:52` - `assert ana.queued_count == 2` and `:53` `assert ana.expected_value_sum == 1100` and `:54` `assert ana.cooling_count == 1`. UI: `solution/frontend/src/components/ManagerRollup.test.tsx:45` - `expect(within(anna).getByText("8")).toBeTruthy()` and lane scenario 6 (`ui-evidence/06-gestor-assertado.png`) | ✅ PASS |
| LEAD-27 Highlight good deals that are cooling: high SCORE (Focar, the top slice of the view) and Esfriando | Ana's filtered view has 1 such deal; an agent with cooling but zero Focar+Esfriando is not highlighted | `solution/backend/tests/unit/test_rollup.py:63` - `assert rows["Ana"].good_deals_cooling == 1`. UI: `solution/frontend/src/components/ManagerRollup.test.tsx:72` - `expect(within(anna).getByText("Bons esfriando 2")).toBeTruthy()` and `:75` Darcel has no highlight. Lane scenario 6: Anna 5, Cecily without the highlight | ✅ PASS |
| LEAD-28 WHEN the manager filters by agent, manager, or office THEN rollup and SCORE are recomputed on that view | East keeps only Ana with queued_count 2; Central is a strict subset and good-cooling counts change | `solution/backend/tests/unit/test_rollup.py:72` - `assert set(both) == {"Ana"}` and `:73` `assert both["Ana"].queued_count == 2`. API: `solution/backend/tests/e2e/test_rollup.py:43` - `assert changed` | ✅ PASS |
| LEAD-29 WHEN the user runs docker compose up THEN API and UI start and the UI lists real CSV deals | Compose publishes the UI on 127.0.0.1:8080; the lane opened that origin and matched Bioholding US$ 5.482 / 139 days to products.csv 5482 and pipeline NSX4NR40, engage date 2017-08-14 | `solution/docker-compose.yml:31` - `"8080:80"`. UI lane scenario 8 (`ui-evidence/08-deals-reais-assertado.png`) | ✅ PASS |
| LEAD-33 WHERE a local setup is used THEN it starts with the two documented commands | README lists uvicorn on 127.0.0.1:8000 and `npm --prefix frontend run dev` (UI on 5173) | `README.md:46` - `.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --app-dir backend --host 127.0.0.1 --port 8000` and `:47` `npm --prefix frontend run dev`. Same factory is what Compose and the API tests boot | ✅ PASS |
| LEAD-30 The system is offline and deterministic: identical input, identical output, no external calls on the critical path | Two queue responses are byte-identical; a non-local socket connect fails the test; deals stay on app state | `solution/backend/tests/integration/test_determinism.py:22` - `assert _queue_bytes() == _queue_bytes()` and `:38` raises if the host is not local and `:57` `assert client.app.state.deals` | ✅ PASS |
| LEAD-31 UI copy is Portuguese; API fields stay English | Card labels are Produto, Conta, Valor, Estágio, Dias no funil, SCORE, Estado, Confiança, Motivo, Ação; queue JSON keys are the English field set | `solution/frontend/src/components/QueueList.test.tsx:43` - `expect(screen.getByText(label)).toBeTruthy()`; `solution/backend/tests/e2e/test_queue.py:32` - `assert items[0].keys() >= QUEUE_FIELDS`. UI lane scenario 1 | ✅ PASS |
| LEAD-32 No persistence; data stays in memory | Settings have no database URL; the queue does not rewrite the CSV directory | `solution/backend/tests/unit/test_scaffold.py:32` - `assert not hasattr(settings, "database_url")`; `solution/backend/tests/integration/test_determinism.py:61` - `assert after == before` | ✅ PASS |
| Edge: empty workable view shows a message, not an error | `empty_message == "sem deals nesta visão"` and both lists empty | `solution/backend/tests/e2e/test_queue.py:78` - `assert body["empty_message"] == "sem deals nesta visão"`. UI lane scenario 7 (`ui-evidence/07-vazio-filtro-assertado.png`) | ✅ PASS |
| Edge: age exactly 106 stays on the urgency plateau and has no Esfriando badge | `urgency(106) == 1.0` and `cooling(106) is False`; the card does not render the badge | `solution/backend/tests/unit/test_urgency.py:18` - `assert urgency(106) == pytest.approx(1.0)`; `solution/backend/tests/unit/test_cooling.py:7` - `assert cooling(106) is False`; `solution/frontend/src/components/QueueList.test.tsx:67` - `expect(screen.queryByText("Esfriando")).toBeNull()` | ✅ PASS |
| Edge: identical PRIORITY shares one SCORE | Priorities `[1, 2, 2, 4]` score `[25, 75, 75, 100]` | `solution/backend/tests/unit/test_percentile.py:16` - `assert percentile_scores([1, 2, 2, 4]) == [25, 75, 75, 100]` | ✅ PASS |
| Edge: a single workable deal is SCORE 100 and ESTADO Focar | Both functions return that pair | `solution/backend/tests/unit/test_percentile.py:7` - `assert percentile_scores([250]) == [100]`; `solution/backend/tests/unit/test_estado.py:7` - `assert assign_estado([10]) == ["Focar"]` | ✅ PASS |
| Edge: low historical support lowers CONFIANÇA and leaves VALOR unchanged | GTK 500 stays 26768 at Média | `solution/backend/tests/unit/test_confidence.py:33` - `assert assessed.level == "Média"` and `:34` `assert assessed.value == 26768` | ✅ PASS |

**Status**: ✅ All ACs covered

---

## Discrimination Sensor

Isolated worktree at `a0f481e` (detached). The real tree was not mutated. Each fault was restored before the next. Scratch `git status --porcelain` was empty before the worktree was removed. Real-tree porcelain after removal matched the pre-sensor baseline (14 paths, none of them product code).

| Mutation | File:line | Description | Killed? |
| -------- | --------- | ----------- | ------- |
| 1 | `solution/backend/app/scoring/cooling.py:8` | Flipped the badge bound `age_days > WON_P90` to `age_days >= WON_P90` | ✅ Killed. `test_cooling.py:7` `assert cooling(106) is False` failed (got True). `test_cooling.py:19` also failed |
| 2 | `solution/backend/app/scoring/priority.py:5` | Replaced `return value * urgency` with `return value + urgency` | ✅ Killed. `test_priority.py:9` `assert priority(1000, 1.0) == 1000` failed (got 1001.0). Ordering assertion at `:18` also failed |
| 3 | `solution/backend/app/views/filter.py:39` | Dropped the `deal_stage == "Engaging"` gate so any staged deal with account and date entered the workable queue | ✅ Killed. `test_filter.py:56` `assert split.workable == ()` failed (Won and Lost leaked). `test_query.py:61` `ids.isdisjoint({won, lost, pros, no-account})` failed |

**Sensor depth**: lightweight (3 behavior-level faults on scoring and filter, P1)
**Result**: 3/3 killed - PASS

---

## Interactive UAT Results (if performed)

Human UAT was not run in this pass. The UI lane (Playwright MCP, `http://127.0.0.1:8080`) is the user-facing evidence. All eight scenarios passed.

| # | Test | Result | Details |
| - | ---- | ------ | ------- |
| 1 | Fila do vendedor | ✅ Pass | Anna Snelling, 19 Engaging cards, SCORE 100 first, Portuguese reason and action. `ui-evidence/01-fila-vendedor-assertado.png` |
| 2 | Exclusões / Revisar | ✅ Pass | Workable queue has no Won/Lost/Prospecting; Revisar is a separate section. `ui-evidence/02-exclusoes-revisar-assertado.png` |
| 3 | Esfriando / Focar | ✅ Pass | 19 deals older than 106 days keep the badge and stay in the queue; Focar = 4 = ceil(0.20×19). `ui-evidence/03-esfriando-focar-assertado.png` |
| 4 | Troca de visão | ✅ Pass | Groovestreet SCORE 89 (meus deals) → 94 (time); Time+East shows the empty state. `ui-evidence/04-troca-de-visao-assertado.png` |
| 5 | Export vs UI | ✅ Pass | export.csv has 19 rows, same order and columns, 0 mismatches. `ui-evidence/05-export-vs-ui-assertado.png` |
| 6 | Gestor | ✅ Pass | Count, summed value, esfriando; "Bons esfriando" on Anna (5), not on Cecily. `ui-evidence/06-gestor-assertado.png` |
| 7 | Vazio / fantasma | ✅ Pass | Carl Lin and Time+East show "sem deals nesta visão", no error. `ui-evidence/07-vazio-fantasma-assertado.png`, `ui-evidence/07-vazio-filtro-assertado.png` |
| 8 | Deals reais | ✅ Pass | Bioholding US$ 5.482 / 139 days matches products.csv (5482) and pipeline NSX4NR40 (2017-08-14). `ui-evidence/08-deals-reais-assertado.png` |

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
| Documented guidelines followed: none - strong defaults applied (`tasks.md` Test Coverage Matrix) | ✅ |

Domain modules stay small and arithmetic: priority is one product, the urgency knots and the 0.35 floor live in one function, and the filter is a single pass. Routes in scope (`/api/agents`, `/api/queue`, `/api/rollup`, `/api/export.csv`, `/api/quality-log`) have an e2e happy path; empty view and missing CSV are the edge and error paths. Scaffold and loader tests map to T1/T2 done-when and to LEAD-08, LEAD-32, and the real CSV row counts. Spot-check of the queue story: `test_query.py` asserts the exact order, the eight fields, and the Portuguese strings from the spec assumptions, not a mere "has a score".

---

## Edge Cases

- [x] Empty workable view: message "sem deals nesta visão", not an error
- [x] Age == 106: urgency stays at 1.0 and the Esfriando badge stays off
- [x] Identical PRIORITY: same SCORE percentile
- [x] Single workable deal: SCORE 100 and ESTADO Focar
- [x] Low support: CONFIANÇA drops, VALOR stays the catalog price

---

## Gate Check

- **Gate command**: `.venv\Scripts\python -m pytest backend/tests -q && npm --prefix frontend run build && npm --prefix frontend test -- --run` (from `solution/`)
- **Result**: 68 pytest passed, 0 failed, 0 skipped; frontend production build succeeded; 10 vitest passed, 0 failed, 0 skipped
- **Pytest breakdown** (same run, matches the backend lane): unit 51, integration 7, e2e 10
- **Test count before feature** (`4aed364`): 0
- **Test count after feature** (`a0f481e`): 78 (68 pytest + 10 vitest)
- **Delta**: +78 new tests
- **Skipped tests**: none
- **Failures**: none
- **Note**: pytest emitted one Starlette deprecation warning. It is not a skip and not a failure.

---

## Fix Plans (if issues found)

None.

---

## Requirement Traceability Update

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| LEAD-01 | Pending | ✅ Verified |
| LEAD-02 | Pending | ✅ Verified |
| LEAD-03 | Pending | ✅ Verified |
| LEAD-04 | Pending | ✅ Verified |
| LEAD-05 | Pending | ✅ Verified |
| LEAD-06 | Pending | ✅ Verified |
| LEAD-07 | Pending | ✅ Verified |
| LEAD-08 | Pending | ✅ Verified |
| LEAD-09 | Pending | ✅ Verified |
| LEAD-10 | Pending | ✅ Verified |
| LEAD-11 | Pending | ✅ Verified |
| LEAD-12 | Pending | ✅ Verified |
| LEAD-13 | Pending | ✅ Verified |
| LEAD-14 | Pending | ✅ Verified |
| LEAD-15 | Pending | ✅ Verified |
| LEAD-16 | Pending | ✅ Verified |
| LEAD-17 | Pending | ✅ Verified |
| LEAD-18 | Pending | ✅ Verified |
| LEAD-19 | Pending | ✅ Verified |
| LEAD-20 | Pending | ✅ Verified |
| LEAD-21 | Pending | ✅ Verified |
| LEAD-22 | Pending | ✅ Verified |
| LEAD-23 | Pending | ✅ Verified |
| LEAD-24 | Pending | ✅ Verified |
| LEAD-25 | Pending | ✅ Verified |
| LEAD-26 | Pending | ✅ Verified |
| LEAD-27 | Pending | ✅ Verified |
| LEAD-28 | Pending | ✅ Verified |
| LEAD-29 | Pending | ✅ Verified |
| LEAD-30 | Pending | ✅ Verified |
| LEAD-31 | Pending | ✅ Verified |
| LEAD-32 | Implementing | ✅ Verified |
| LEAD-33 | Pending | ✅ Verified |

---

## Summary

**Overall**: ✅ Ready

**Spec-anchored check**: 38/38 ACs matched spec outcome | 0 spec-precision gaps
**Sensor**: 3/3 mutations killed
**Gate**: 68 pytest passed, 10 vitest passed, frontend build succeeded

**What works**: The seller queue is Engaging-plus-account, ordered by a percentile of list price times urgency, with Portuguese reason and action. Revisar is separate. Age badges and never drops a deal. Filters recompute SCORE. Export matches the view. The manager rollup highlights Focar deals that are cooling. Compose on port 8080 served real CSV deals, and the same input returns the same queue with no off-machine calls.

**Issues found**: none

**Next steps**: none for this feature
