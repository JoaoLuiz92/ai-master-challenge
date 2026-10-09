# AGENTS.md — Submissão João Luiz (Lead Scorer)

Instruções para qualquer agente nesta pasta. O PR **só** altera `submissions/joao-luiz/`. Não mexer no resto do repositório (`.cursor/` da raiz incluso).

Prosa, commits, docs e este arquivo: **português**. Código, API e identificadores: **inglês** (ADR-004). UI do vendedor/gestor: **português**.

---

## Fonte da verdade

Em dúvida, **não inventar**. Reler nesta ordem: `spec.md` → `design.md` → ADRs / EDA. Se ainda faltar, parar e perguntar.

| Artefato | Caminho |
|----------|---------|
| Spec | `.specs/features/lead-scorer/spec.md` |
| Design | `.specs/features/lead-scorer/design.md` |
| Tasks | `.specs/features/lead-scorer/tasks.md` |
| Delivery | `.specs/features/lead-scorer/DELIVERY.md` |
| Validation-lane | `.specs/features/lead-scorer/validation-lane.md` |
| Estado / decisões | `.specs/STATE.md` |
| Fórmula (v0→v1→v2) | `docs/evolucao-do-score.md` |
| ADRs | `docs/adr/` |
| EDA | `docs/analise-exploratoria.md` |

Retomar sessão: ler `STATE.md` (Handoff + Decisions), conferir git e `tasks.md`. Evidência no disco ganha de snapshot velho.

---

## Fluxo e skills

Skill de planejamento/implementação: **`tlc-spec-driven`**.

```
Specify → Design → Tasks → Execute → validation-lane
```

| Fase | Skill / agente | Saída |
|------|----------------|-------|
| Specify | `tlc-spec-driven` | `spec.md` |
| **Spec fechada** | este harness | **criar `DELIVERY.md`** (obrigatório; não seguir sem ele) |
| Design | `tlc-spec-driven` | `design.md` |
| Tasks | `tlc-spec-driven` | `tasks.md` |
| Execute | `tlc-spec-driven` (um T por vez) | código + testes + commit atômico |
| **Última tarefa Execute concluída** | subagente **`validation-lane`** | `validation.md` |

Não narrar a fase. Fazer o artefato.

Execute: um commit por tarefa; gate da tarefa passa **antes** de marcar done; testes afirmam o AC da spec, não o código. Não pular, xfail ou enfraquecer asserção.

---

## Janela de contexto (Execute)

Limite **45%** da janela enquanto estiver em tasks.

- Carregar só o que a tarefa atual precisa (`STATE.md`, spec, design, a tarefa, código tocado).
- Se o uso **atingir 45% no meio de uma tarefa**: **terminar essa tarefa por completo** (implementar, testes, gate, marcar `tasks.md`, commit). Não abandonar no meio.
- A **próxima** tarefa **não** continua nesta janela. Abrir **nova janela via subagente**, com payload: número da tarefa, spec/design relevantes, `STATE.md`, gate, o que a anterior entregou.
- Não começar T(n+1) numa janela já no limite.

---

## Validation-lane (não validar no chat)

Gatilho: **terminou a última tarefa Execute** (T27 marcada done + commit), ou o usuário pediu validar / verificar / UAT / testes.

Não validar inline. Disparar o subagente `validation-lane`.

```
backend-tester  ∥  ui-tester   →   spec-verifier
   pytest                         (só se os dois PASS)
   Playwright MCP                 autor ≠ verificador
```

- UI: Playwright MCP (`browser_navigate`, `browser_snapshot`, refs). Independent Tests e CA8/CA9/RNF3. Vitest não substitui.
- MCP desconectado: **bloquear** a faixa de UI; pedir para ligar o plugin Playwright. Não usar Chrome DevTools no lugar.
- Verificador não escreve código de produto. Máx. 3 ciclos correção → re-verificar.

Workdir: `submissions/joao-luiz/solution`. Python: `solution\.venv\Scripts\python.exe`.

---

## Git

A raiz ignora `submissions/`. Entrar com `git add -f`.

Não versionar: `solution/.venv/`, `__pycache__/`, `node_modules/`, segredos.

Mensagem em português, Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`), corpo com o **porquê**. Um commit atômico por tarefa. **Não squash.** Não push sem pedido explícito.

Cadeia visível para o avaliador (não um único commit): harness/docs → EDA/ADRs → ingestão → score → API → UI → Docker → evidências.

---

## Produto (o que não negociar)

- `PRIORIDADE = sales_price × urgência`. SCORE = percentil **da visão**. `p̂` fora do ranking.
- Explainability por deal: **fator positivo**, **risco**, **ação** em português.
- Idade não tira da fila. Badge Esfriando se idade > 106d. `TODAY = 2017-12-31`.
- Em memória, sem LLM no caminho crítico. Alias `GTXPro` → `GTX Pro`.

## Evidências do PR

`process-log/` com transcripts reais, prints por papel (vendedor e gestor), auditoria independente (`validation.md` / spec-verifier). Evolução da fórmula em `docs/evolucao-do-score.md`.
