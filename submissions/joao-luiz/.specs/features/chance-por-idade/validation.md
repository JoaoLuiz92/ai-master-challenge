# chance-por-idade Validation

**Date**: 2026-10-11
**Spec**: `.specs/features/chance-por-idade/spec.md`
**Diff range**: `040d296..HEAD` (`cb2f89f`)
**Verifier**: independent sub-agent (author ≠ verifier)
**Result**: PASS

Re-verify loop 2 of 3. Coverage re-derived from spec.md and tests; previous report verdicts were not copied.

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| C1 | ✅ Done | Cohort won/censored + TODAY anchor |
| C2 | ✅ Done | Survival table with censoring |
| C3 | ✅ Done | Wall derivation + chance(age) |
| C4 | ✅ Done | Past-wall open count |
| C5 | ✅ Done | PRIORIDADE = value × chance |
| C6 | ✅ Done | Trabalhar / Decidir / Revisar |
| C7 | ✅ Done | Percentile on Trabalhar |
| C8 | ✅ Done | Chance and wall sentences (PT) |
| C9 | ✅ Done | Backtest, no leakage |
| C10 | ✅ Done | GET /api/queue three buckets |
| C11 | ✅ Done | GET /api/rollup split |
| C12 | ✅ Done | DealCard chance sentence |
| C13 | ✅ Done | DecidirSection |
| C14 | ✅ Done | ManagerRollup parked value |
| C15 | ✅ Done | Config, ADRs, docs |
| C16 | ✅ Lane PASS | backend-tester 133 passed; ui-tester 4 scenarios passed; this report |

C16 remains unchecked in `tasks.md` until the orchestrator records the lane result.

---

## Spec-Anchored Acceptance Criteria

### P1: Chance de fechar por idade (CHANCE-01..05)

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| CHANCE-01 SHALL compute `CHANCE(idade)` as Won ÷ deals that reached the band, censored as non-Won | Hand-count 4/10, 5/6, 3/15; censored curve ≠ closed-only (closed-only increases to 1.0); non-increasing after peak | `backend/tests/unit/test_chance.py:42` `assert by_band[(0, 9)] == 4 / 10`; `:43` `== 5 / 6`; `:44` `== 3 / 15`; `:51` `assert with_censoring != without_censoring`; `:53` `without_censoring[0] < ...[1] < ...[2]`; `:60` `assert after == sorted(after, reverse=True)` | ✅ PASS |
| CHANCE-02 WHEN age exceeds the wall THEN `CHANCE` SHALL be 0 | `chance(wall) == 3/15`; `chance(wall+1) == 0.0` | `backend/tests/unit/test_chance.py:96` `assert chance(wall, table, wall) == 3 / 15`; `:97` `assert chance(wall + 1, table, wall) == 0.0` | ✅ PASS |
| CHANCE-03 SHALL derive the wall from data at load and expose it as config, not a hard-coded literal | Wall = max Won age (25 / 10); bands from `get_settings().chance_bands` | `backend/tests/unit/test_chance.py:88` `assert derive_wall(_hand_cohort()) == 25`; `:90` `== 10`; `:78` `assert bands == ((0, 29), (30, 59), (60, 89), (90, 10_000))`; `:80` table bands `== list(bands)` | ✅ PASS |
| CHANCE-04 WHEN computing age THEN today SHALL be 2017-12-31 | `TODAY == date(2017, 12, 31)`; open 2017-12-01 → age 30 | `backend/tests/unit/test_cohort.py:31` `assert TODAY == date(2017, 12, 31)`; `:34` `assert entry.age_days == 30` | ✅ PASS |
| CHANCE-05 SHALL compute `CHANCE` deterministically, identical input → identical values, no external calls | Repeat table/wall/chance equal | `backend/tests/unit/test_chance.py:111` `assert survival_table(cohort, _BANDS) == survival_table(cohort, _BANDS)`; `:112` `assert derive_wall(cohort) == derive_wall(cohort)`; `:115` `assert chance(25, table, wall) == chance(25, table, wall)` | ✅ PASS |

### P1: Prioridade por valor × chance (CHANCE-06..10)

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| CHANCE-06 SHALL compute `PRIORIDADE = sales_price × CHANCE(idade)` | `priority(1000, 0.47) == 470` | `backend/tests/unit/test_priority.py:9` `assert priority(1000, 0.47) == 470` | ✅ PASS |
| CHANCE-07 SHALL NOT apply a non-zero floor; past-wall `PRIORIDADE = 0` | `priority(26768, 0.0) == 0`; cheap live > expensive dead | `backend/tests/unit/test_priority.py:15` `assert priority(26768, 0.0) == 0`; `:18` `assert cheap_live > expensive_dead` | ✅ PASS |
| CHANCE-08 SHALL compute SCORE as 0–100 percentile of PRIORIDADE among workable deals of the view | Percentile only over Trabalhar; top SCORE 100; parked Decidir score 0 | `backend/tests/unit/test_view.py:52` `assert work_ids == ["high", "low"]`; `:55` `assert view.trabalhar[0].score == 100`; `:56` `assert view.decidir[0].score == 0`; `backend/tests/unit/test_percentile.py:7` `assert percentile_scores([250]) == [100]` | ✅ PASS |
| CHANCE-09 SHALL NOT include any trained conversion model in the ranking | `priority` takes only `value, chance`; extra arg TypeError | `backend/tests/unit/test_priority.py:22` `assert list(priority.__code__.co_varnames) == ["value", "chance"]`; `:24` `pytest.raises(TypeError)` | ✅ PASS |
| CHANCE-10 SHALL no longer reference `URGÊNCIA` in the ranking path | `urgency` not in `priority` args or docstring; live path is `build_view` × chance | `backend/tests/unit/test_priority.py:28` `assert "urgency" not in priority.__code__.co_varnames`; `:29` `assert "urgency" not in (priority.__doc__ or "").lower()` | ✅ PASS |

### P1: Fila Decidir (CHANCE-11..15)

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| CHANCE-11 IF Engaging + account + age > wall THEN Decidir, excluded from Trabalhar | `decide-hi` in Decidir, not in Trabalhar; `work` in Trabalhar | `backend/tests/unit/test_buckets.py:51-56` `"work" in work_ids`; `"decide-hi" in decide_ids`; `"decide-hi" not in work_ids` | ✅ PASS |
| CHANCE-12 SHALL order Decidir by list price descending | ids `decide-hi`, `decide-lo`; values `[500, 80]` | `backend/tests/unit/test_buckets.py:61-65` `== ["decide-hi", "decide-lo"]`; `== [500, 80]`; Playwright P1 Fila Decidir (Anna 19 Decidir price desc); `ui-evidence/01-vendedor-assertado.png` | ✅ PASS |
| CHANCE-13 SHALL keep Prospecting / no account / no `engage_date` in Revisar | review ids `{"no-account", "pros"}`; Won/other agent excluded | `backend/tests/unit/test_buckets.py:71` `assert review_ids == {"no-account", "pros"}`; `:77` disjoint `{"won", "bruno"}`; Playwright P1 93 Revisar incl. Prospecting | ✅ PASS |
| CHANCE-14 SHALL present three distinct sections, each with count and summed value | Trabalhar 2/150, Decidir 2/580, Revisar 2; API three keys + disjoint ids | `backend/tests/unit/test_buckets.py:82-87`; `backend/tests/e2e/test_queue.py:88-98` three keys + disjoint id sets; Playwright P1 Anna 0/19/93; `ui-evidence/01-vendedor-assertado.png` | ✅ PASS |
| CHANCE-15 WHEN age ≤ wall THEN Trabalhar ordered by SCORE descending | work ids high then low; scores sorted desc | `backend/tests/unit/test_view.py:52` `work_ids == ["high", "low"]`; `:65` `scores == sorted(scores, reverse=True)`; Playwright P1 Zane SCORE 100→93→86 | ✅ PASS |

### P1: Explicação (CHANCE-16..19)

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| CHANCE-16 WHEN a workable deal is shown THEN chance sentence in Portuguese | `"47% dos deals desta idade fecharam."`; percent from computed chance | `backend/tests/unit/test_explain.py:30` `chance_sentence(0.47) == "47% dos deals desta idade fecharam."`; `backend/tests/unit/test_view.py:94` `reason.endswith("dos deals desta idade fecharam.")`; `:96` `str(round(...chance * 100)) in reason`; `frontend/src/components/DealCard.test.tsx:51`; Playwright P1 Explicação 57%/61%/64%; `ui-evidence/02-chance-wall-assertado.png` | ✅ PASS |
| CHANCE-17 WHEN in Decidir THEN wall sentence with wall age and past-wall open count | Template with interpolated N and M; count fixture == 2 | `backend/tests/unit/test_explain.py:36` `== "Nenhum deal da base fechou depois de 77 dias; 3 abertos já passaram disso."`; `backend/tests/unit/test_chance.py:152` `assert past_wall_open_count(repo, wall) == 2`; `backend/tests/unit/test_view.py:101` `reason.startswith("Nenhum deal da base fechou depois de ")`; Playwright P1 138 dias / 1291 abertos; `ui-evidence/02-chance-wall-decidir-passo.png` | ✅ PASS |
| CHANCE-18 SHALL present action per queue: advance / requalify-or-close / fix-data | Trabalhar `Avançar proposta`; Decidir `Requalificar ou encerrar`; Revisar `Qualificar conta/dados` | `backend/tests/unit/test_explain.py:43-45`; `backend/tests/unit/test_view.py:95,102`; Playwright P1 Explicação those three strings; `ui-evidence/02-chance-wall-assertado.png` | ✅ PASS |
| CHANCE-19 SHALL compute every number from the data, no fabricated value | Chance % from `deal.chance`; wall sentence uses arguments, not a 138 literal | `backend/tests/unit/test_view.py:96` `str(round(view.trabalhar[0].chance * 100)) in reason`; `backend/tests/unit/test_explain.py:37` `assert "138" not in text`; `:39` `"12" in other and "9" in other` | ✅ PASS |

### P1: Backtest gate (CHANCE-20..24)

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| CHANCE-20 SHALL reconstruct ≥3 past cut-offs with no future leakage | Future closes hidden; no close/engage after cutoff | `backend/tests/integration/test_backtest.py:30-32` `seen.close_date is None`; `:34-38` all close/engage `<= cutoff`; `:41` `len(report.cutoffs) >= 3` | ✅ PASS |
| CHANCE-21 SHALL measure next-90-days won revenue captured by top-N per agent for nova, price, random | Each cutoff has `nova`, `preco`, `aleatorio` ≥ 0 | `backend/tests/integration/test_backtest.py:45-48` `assert row.nova >= 0`; `row.preco >= 0`; `row.aleatorio >= 0`; `:44` cutoffs `== DEFAULT_CUTOFFS` | ✅ PASS |
| CHANCE-22 SHALL report new vs price with a dispersion measure | `nova_vs_preco_delta` float; `dispersion >= 0` | `backend/tests/integration/test_backtest.py:53-55` `isinstance(..., float)`; `assert report.dispersion >= 0` | ✅ PASS |
| CHANCE-23 IF new does not exceed price THEN SHALL NOT be adopted | `adopted is (nova_vs_preco_delta > 0)` | `backend/tests/integration/test_backtest.py:57` `assert report.adopted is (report.nova_vs_preco_delta > 0)` | ✅ PASS |
| CHANCE-24 SHALL be reproducible offline with a single documented command | `run_backtest` runs in tests; command `python backtest.py` | `backend/tests/integration/test_backtest.py:42` `report = run_backtest(_repo())`; README documents `python backtest.py` | ✅ PASS |

### P2: Rollup gestor (CHANCE-25..27)

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| CHANCE-25 WHEN manager view THEN per agent count and value of Trabalhar and of Decidir | Ana trabalhar 1/100, decidir 1/1000 | `backend/tests/unit/test_rollup.py:59-62`; Playwright P2 Dustin US$ 109.717 / East US$ 229.377; `ui-evidence/03-gestor-rollup-assertado.png` | ✅ PASS |
| CHANCE-26 SHALL highlight total value parked in Decidir | parked sum 1050; API `parked_value`; UI `mark` "Valor parado" | `backend/tests/unit/test_rollup.py:73` `sum(...) == 1050`; `backend/tests/e2e/test_rollup.py:32-33` `"parked_value" in body`; `frontend/src/components/ManagerRollup.test.tsx:48-49` `toContain("Valor parado")` / `toBe("US$ 1.050")`; Playwright P2 US$ 1.064.848 | ✅ PASS |
| CHANCE-27 WHEN filter by agent/manager/office THEN recompute both rollups and SCORE percentile | East = Ana only; office switch changes Trabalhar scores | `backend/tests/unit/test_rollup.py:78` `set(east) == {"Ana"}`; `backend/tests/e2e/test_queue.py:120-121` `assert changed`; Playwright P2 agent drill recomputes; `ui-evidence/03-gestor-rollup-east-passo.png` | ✅ PASS |

### P2: Export e filtros (CHANCE-28..29)

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| CHANCE-28 WHEN export THEN CSV matches the filtered view, including queue Trabalhar/Decidir/Revisar, same order as UI | Header starts with `fila`; body = Trabalhar×n + Decidir×n + Revisar×n; line match product/estado/action; filtered Anna keeps Decidir+Revisar and total length | `backend/tests/e2e/test_export.py:37` `assert rows[0] == DISPLAYED_COLUMNS`; `:42-44` `filas == (["Trabalhar"] * n_work + ["Decidir"] * n_decide + ["Revisar"] * n_review)`; `:45-56` zip match vs queue; `:70-72` `"Decidir" in filas`; `"Revisar" in filas`; `len(body) == len(trabalhar)+len(decide)+len(review)`; Playwright P2 Anna 19 Decidir then 93 Revisar; `ui-evidence/04-export-assertado.png` | ✅ PASS |
| CHANCE-29 WHEN switching views THEN recompute SCORE percentile over workable deals of the new view | World vs East Trabalhar scores differ for overlapping ids | `backend/tests/e2e/test_queue.py:120-121` `assert world["trabalhar"] and east["trabalhar"]`; `assert changed` | ✅ PASS |

**Status**: ✅ All ACs covered (29/29). No spec-precision gaps flagged.

---

## Discrimination Sensor

Isolated scratch: `git worktree add` at HEAD `cb2f89f` → `%TEMP%\chance-por-idade-sensor`. Real tree never mutated. Pytest ran in Docker with the scratch backend volume mounted (not host `.venv`).

| Mutation | File:line | Description | Killed? |
| -------- | --------- | ----------- | ------- |
| 1 | `backend/app/scoring/chance.py:69` | Flipped wall boundary `age_days > wall` → `age_days >= wall` (chance at wall becomes 0) | ✅ Killed by `test_chance_02_above_wall_is_zero_and_wall_keeps_last_band` (`assert chance(wall, table, wall) == 3 / 15` got 0.0) |
| 2 | `backend/app/views/buckets.py:46` | Swapped routing `age > wall` → `age < wall` (young deals to Decidir) | ✅ Killed by `test_chance_11_past_wall_engaging_goes_to_decidir` and 5 other bucket/view tests |
| 3 | `backend/app/api/export.py:46-49` | Dropped Revisar rows from CSV (Trabalhar+Decidir only) | ✅ Killed by `test_chance_28_csv_includes_three_queues_in_screen_order` (`len(body) == n_work+n_decide+n_review`) and `test_chance_28_filtered_export_keeps_the_three_queues` (`"Revisar" in filas`) |

Worktree removed with `git worktree remove --force`. Real-tree porcelain after cleanup: empty (matches pre-sensor baseline).

**Sensor depth**: lightweight
**Result**: 3/3 killed - PASS

---

## Interactive UAT Results (if performed)

UI Independent Tests ran on the validation-lane `ui-tester` (Playwright MCP, base `http://127.0.0.1:8080`). Not a human walkthrough.

| # | Test | Result | Details |
| --- | -------- | -------- | ------- |
| 1 | P1 Fila Decidir | ✅ Pass | Anna 0 Trabalhar / 19 Decidir (price desc) / 93 Revisar; empty-work "Nada para trabalhar agora." not error; Zane Focar SCORE 100→93→86. Prints `01-vendedor-*.png` |
| 2 | P1 Explicação | ✅ Pass | Trabalhar "57%/61%/64% dos deals desta idade fecharam" + Avançar proposta; Decidir 138 dias / 1291 abertos + Requalificar ou encerrar; Revisar Qualificar conta/dados. Prints `02-chance-wall-*.png` |
| 3 | P2 Rollup | ✅ Pass | Per-agent Trabalhar+Decidir count/value; Valor parado US$ 1.064.848; Dustin / East / agent drill recomputes. Prints `03-gestor-rollup-*.png` |
| 4 | P2 Export | ✅ Pass | Anna CSV `fila` present; 19 Decidir then 93 Revisar; line-by-line match with UI; no Trabalhar rows. Prints `04-export-*.png` |

---

## Code Quality

| Principle | Status |
| ---------------- | ------ |
| Minimum code | ✅ |
| Surgical changes | ✅ |
| No scope creep | ✅ |
| Matches patterns | ✅ |
| Spec-anchored outcome check (asserted values match spec) | ✅ |
| Per-layer Coverage Expectation met (domain 1:1 ACs; routes happy+edge+error) | ✅ |
| Every test maps to a spec requirement - no unclaimed tests | ✅ |
| Documented guidelines followed: `references/coding-principles.md`; project pytest in Docker (WDAC pandas block) | ✅ |

Note (not a gap): `build_queue` in `backend/app/views/query.py` still calls `urgency`. The live ranking path is `build_view` → `priority(value, chance)`, which is what `/api/queue` and `/api/export.csv` use.

---

## Edge Cases

- [x] Age band with no Won → `CHANCE` 0: `backend/tests/unit/test_chance.py:66` `assert row.chance == 0.0`
- [x] Age exactly the wall → Trabalhar with last band chance: `test_chance.py:96` `chance(wall) == 3/15`; `test_buckets.py` deal at wall=10 is in Trabalhar
- [x] Empty Trabalhar, Decidir not empty → decision list + empty-work, not error: `test_view.py:87-89`; `DecidirSection.test.tsx:60` `"Nada para trabalhar agora."`; Playwright P1
- [x] Identical PRIORIDADE → same SCORE: `test_percentile.py:16` `[25, 75, 75, 100]`
- [x] Single workable deal → SCORE 100: `test_percentile.py:7`; `test_view.py:55`
- [x] Low product support lowers CONFIANÇA, not chance: `test_confidence.py:33-34` level Média, value unchanged; `chance()` has no product term
- [x] Every workable past the wall → empty Trabalhar, all in Decidir: `test_view.py:87-89`

---

## Gate Check

- **Gate command**: validation-lane backend-tester (Docker, pandas blocked on host):
  `docker compose run --rm --no-deps -e PYTHONPATH=/app/backend -v "<host>/solution/backend:/app/backend" api python -m pytest /app/backend/tests -q`
- **Result**: 133 passed, 0 failed, 0 skipped
- **Test count before feature** (`040d296`): 102 backend `def test_` functions
- **Test count after feature** (`HEAD`): 133
- **Delta**: +31 tests (no deletions; export gained the three-queue assertions)
- **Skipped tests**: none
- **Failures**: none
- **UI lane**: Playwright MCP, 4 Independent Tests PASS
- **Frontend vitest/build**: C15 build gate; not re-run in this verifier pass

---

## Fix Plans (if issues found)

None.

---

## Requirement Traceability Update

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| CHANCE-01 | Implementing | ✅ Verified |
| CHANCE-02 | Verified | ✅ Verified |
| CHANCE-03 | Verified | ✅ Verified |
| CHANCE-04 | Verified | ✅ Verified |
| CHANCE-05 | Verified | ✅ Verified |
| CHANCE-06 | Verified | ✅ Verified |
| CHANCE-07 | Verified | ✅ Verified |
| CHANCE-08 | Verified | ✅ Verified |
| CHANCE-09 | Verified | ✅ Verified |
| CHANCE-10 | Verified | ✅ Verified |
| CHANCE-11 | Verified | ✅ Verified |
| CHANCE-12 | Verified | ✅ Verified |
| CHANCE-13 | Verified | ✅ Verified |
| CHANCE-14 | Verified | ✅ Verified |
| CHANCE-15 | Verified | ✅ Verified |
| CHANCE-16 | Verified | ✅ Verified |
| CHANCE-17 | Verified | ✅ Verified |
| CHANCE-18 | Verified | ✅ Verified |
| CHANCE-19 | Verified | ✅ Verified |
| CHANCE-20 | Verified | ✅ Verified |
| CHANCE-21 | Verified | ✅ Verified |
| CHANCE-22 | Verified | ✅ Verified |
| CHANCE-23 | Verified | ✅ Verified |
| CHANCE-24 | Verified | ✅ Verified |
| CHANCE-25 | Verified | ✅ Verified |
| CHANCE-26 | Verified | ✅ Verified |
| CHANCE-27 | Verified | ✅ Verified |
| CHANCE-28 | Verified | ✅ Verified |
| CHANCE-29 | Verified | ✅ Verified |

---

## Summary

**Overall**: ✅ Ready

**Spec-anchored check**: 29/29 ACs matched spec outcome | 0 spec-precision gaps
**Sensor**: 3/3 mutations killed
**Gate**: 133 passed, 0 failed, 0 skipped

**What works**: Survival chance with censoring and a data-derived wall; ranking by value × chance without a floor; Trabalhar / Decidir / Revisar split; Portuguese chance and wall copy; backtest adoption rule; manager parked-value rollup; export CSV column `fila` with all three queues in screen order (including Revisar).

**Issues found**: none

**Next steps**: Orchestrator records C16 as done. Feature is ready.
