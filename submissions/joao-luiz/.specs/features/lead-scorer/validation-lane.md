# Lead Scorer — Faixa de validação

**Spec**: `.specs/features/lead-scorer/spec.md`
**Tasks**: `.specs/features/lead-scorer/tasks.md`
**Gatilho**: após a última tarefa Execute, ou quando o usuário pedir validar / verificar / UAT / testes
**Caminhos**: relativos a `submissions/joao-luiz/solution/`, salvo indicação em contrário

O produto é voltado ao usuário (FastAPI + React). Domínio e API passam por pytest. Fluxos que vendedor/gestor de fato clicam rodam na **faixa de UI via Playwright MCP** — não como specs `@playwright/test` versionadas, nem como testes de componente mockados.

---

## Topologia da faixa

```
Orquestrador  (.cursor/agents/validation-lane.md)
   │
   ├─ 1. backend-tester   pytest unit + integration + API e2e
   ├─ 2. ui-tester        Playwright MCP contra a UI em execução
   └─ 3. spec-verifier    independente (autor ≠ verificador): evidence-or-zero + sensor
```

As faixas 1 e 2 podem rodar **em paralelo**. A faixa 3 só começa depois que ambas retornam. O verificador nunca escreve código de produto.

---

## Quais testes são obrigatórios

Derivado dos ACs da spec, Independent Tests, casos de borda e da Matriz de Cobertura de Testes das tasks. Camada = onde a asserção vive, não onde o código vive.

### Faixa 1 — backend (pytest)

| Camada | Comando | Cobre |
| ----- | ------- | ------ |
| Unit (`backend/tests/unit`) | `.venv\Scripts\python -m pytest backend/tests/unit -q` | Scoring, filtro, percentil, estado, explain, rollup, aliases |
| Integration (`backend/tests/integration`) | `.venv\Scripts\python -m pytest backend/tests/integration -q` | CSVs reais, contagem de linhas, log de qualidade, determinismo |
| API e2e (`backend/tests/e2e`) | `.venv\Scripts\python -m pytest backend/tests/e2e -q` | `/api/agents`, `/api/queue`, `/api/rollup`, `/api/export.csv`, `/api/quality-log` |

Testes unitários de componentes do frontend (`npm --prefix frontend test -- --run`) ficam nos **gates das tarefas Execute** (T21–T25). Não são worker da faixa de validação: mockam fetch e não provam Independent Tests que dizem "abrir a UI".

### Faixa 2 — UI (Playwright MCP) — obrigatória

Necessária. Independent Tests e CA8/CA9/RNF3 só são observáveis no navegador:

| ID | Observável na UI | Por que MCP (não pytest / não vitest) |
| -- | -------------------- | --------------------------------- |
| LEAD-01, 04, 05, 31 | Selecionar vendedor → fila Engaging+conta, campos, motivo/ação em PT | Independent Test da fila P1 |
| LEAD-02 | Won / Lost / Prospecting nunca aparecem como trabalhável | Exclusão visual |
| LEAD-15, 18 | Revisar separado; empty state de agente-fantasma | Layout / copy |
| LEAD-19, 21 | Badge Esfriando; ESTADO Focar/Acompanhar | Badge + rótulos |
| LEAD-23, 24 | Trocar meus-deals ↔ time; filtros agent/manager/office | SCORE na tela muda |
| LEAD-25 | Export CSV == linhas/ordem/colunas exibidas | Comparar download com tabela visível |
| LEAD-26, 27 | Papel gestor → rollup + destaque "bons esfriando" | Independent Test P2 |
| LEAD-29 | UI lista deals reais do CSV após `docker compose up` (ou fallback local) | CA8 |
| Borda: visão vazia | Mensagem de empty state, não erro | Caso de borda da spec |

**Ferramentas:** Playwright MCP (`browser_navigate`, `browser_snapshot`, `browser_click`, `browser_select_option`, `browser_network_requests`, `browser_take_screenshot`). Fallback só se o MCP estiver desconectado: `playwright-skill`.

**Não** adicionar suite Playwright versionada a menos que Execute peça depois. Evidências do MCP vão em `validation.md`.

### Faixa 3 — verificador (sempre)

Checagem de resultado ancorada na spec (cada AC → `file:line` + asserção), sensor de discriminação em worktree scratch, redação de `validation.md`. Ver `tlc-spec-driven` / `validate.md`.

---

## Mapa AC → faixa

| Req | Resultado na spec (preciso) | Faixa 1 | Faixa 2 |
| --- | ---------------------- | ------ | ------ |
| LEAD-01 | Fila = Engaging + account, SCORE desc | API e2e T17 | UI: selecionar agente, lista bate |
| LEAD-02 | Won/Lost/Prospecting fora do trabalhável | unit T10 + API | UI: nenhum desses estágios na fila |
| LEAD-03 | Maior PRIORITY primeiro | unit T14 | — (ordem já na API; UI espelha) |
| LEAD-04 | product, account, value, stage, days, SCORE, ESTADO, CONFIANÇA | unit T14 + API | UI: campos do DealCard visíveis |
| LEAD-05 | Motivo + ação PT (ciclo / esfriando / Revisar) | unit T13 | UI: textos visíveis |
| LEAD-06 | PRIORITY = VALOR × URGÊNCIA | unit T7 | — |
| LEAD-07 | Nós de urgência 0/57/106 + piso 0.35 | unit T6 | — |
| LEAD-08 | TODAY = 2017-12-31 | unit T5 | — |
| LEAD-09 | SCORE = percentil 0–100 da visão; N=1 → 100; empates compartilham | unit T11 | — |
| LEAD-10 | Sem p̂ no ranking | unit T7 | — |
| LEAD-11 | GTXPro → GTX Pro; 0 deals sem preço por alias | unit T3/T4 + integration | — |
| LEAD-12 | Aliases technolgy/Philipines | unit T3 | — |
| LEAD-13 | Log de qualidade tipo + contagem de linhas | unit T3 + API T20 | — |
| LEAD-14 | Produto sem match → VALOR 0, CONFIANÇA Baixa | unit T4 | — |
| LEAD-15 | Agente com 0 deals → empty state, não carteira | API T16 | UI: copy de empty state |
| LEAD-16 | Sem account → Revisar, não fila | unit T10 + API | UI: seções separadas |
| LEAD-17 | Sem engage_date → Revisar, sem urgência | unit T5/T10 | — |
| LEAD-18 | Revisar apresentado separado | API T17 | UI: duas seções |
| LEAD-19 | Idade > 106 → badge Esfriando | unit T9 | UI: badge no card |
| LEAD-20 | Idade nunca remove da fila | unit T9/T14 | — |
| LEAD-21 | Focar = ceil(0.20×N) (≥1 se não vazio) | unit T12 | UI: rótulos Focar/Acompanhar |
| LEAD-22 | CONFIANÇA = min(completude, suporte) | unit T8 | — |
| LEAD-23 | Troca de visão recalcula SCORE | API T17 duas requisições | UI: mesmo deal, SCORE muda |
| LEAD-24 | Filtros agent/manager/office | unit T10 + API | UI: controles de filtro |
| LEAD-25 | CSV == visão filtrada, mesma ordem/colunas | API T19 vs /queue | UI: download vs linhas visíveis |
| LEAD-26 | Rollup: contagem, soma VALOR, contagem esfriando | unit T15 + API T18 | UI: tabela do gestor |
| LEAD-27 | Destaque alto SCORE + Esfriando | unit T15 | UI: destaque visível |
| LEAD-28 | Rollup/SCORE recalculam com filtro de gestor | API T18 | — |
| LEAD-29 | `docker compose up` → UI lista deals reais | build/manual | UI contra URL do compose |
| LEAD-30 | Entrada idêntica → saída idêntica; sem chamadas externas | integration T27 | — |
| LEAD-31 | UI em português; API em inglês | — | UI: rótulos PT |
| LEAD-32 | Sem persistência / só em memória | integration T27 | — |
| LEAD-33 | Dois comandos locais documentados | docs + T26 | UI contra URL local |
| Borda | Visão vazia → mensagem, não erro | unit T14 + API | UI: empty state |
| Borda | Idade == 106 → platô, sem badge | unit T6/T9 | UI: sem Esfriando em 106 |
| Borda | PRIORITY idêntica → mesmo SCORE | unit T11 | — |
| Borda | N=1 → SCORE 100 + Focar | unit T11/T12 | — |
| Borda | Suporte baixo reduz CONFIANÇA, não VALOR | unit T8 | — |

---

## Cenários de UI (Playwright MCP)

URL base: origem do frontend com a stack no ar (compose ou os dois comandos locais). Descobrir via servidores em execução; não fixar porta morta.

1. **Fila do vendedor** — escolher agente com Engaging+conta. Snapshot: só esses deals; cada card com campos LEAD-04 + motivo + ação em português; primeira linha é o maior SCORE.
2. **Exclusões** — nenhum Won/Lost/Prospecting na lista trabalhável; Revisar em seção separada.
3. **Esfriando / Focar** — deal com idade > 106 mostra badge `Esfriando` e permanece na lista; contagem Focar bate com ceil(0.20×N) da fila visível.
4. **Troca de visão** — registrar SCORE de um deal em "meus deals"; mudar para "time"; SCORE do mesmo deal muda.
5. **Export** — baixar CSV do filtro atual; linhas/ordem/colunas batem com a fila visível.
6. **Gestor** — trocar papel; tabela com contagem por agente, valor somado, contagem esfriando; bons-esfriando destacados.
7. **Vazio / fantasma** — agente sem deals mostra empty state explícito; filtro vazio mostra mensagem, não crash.
8. **Deals reais** — lista não vazia e valores vêm dos CSVs (não placeholders).

Screenshot só como evidência de falha. Interagir via refs do `browser_snapshot`.

---

## Contrato do orquestrador

1. Confirmar que as tarefas Execute T1–T27 estão marcadas como concluídas (ou informar quais não estão — então FAIL na faixa).
2. Disparar `backend-tester` e `ui-tester` em paralelo.
3. Se qualquer faixa falhar, parar; não disparar o verificador. Devolver falhas ranqueadas.
4. Disparar `spec-verifier` com os relatórios das duas faixas + spec.md + superfície do git diff.
5. Expor o resumo compacto do verificador. Lacunas → tarefas de correção (máx. 3 ciclos fix→re-verificar).

Diretório de trabalho para pytest/npm: `submissions/joao-luiz/solution`.
Python: `solution\.venv\Scripts\python.exe`.
Browsers Playwright: `$env:PLAYWRIGHT_BROWSERS_PATH = "$env:LOCALAPPDATA\ms-playwright"` no Windows.
