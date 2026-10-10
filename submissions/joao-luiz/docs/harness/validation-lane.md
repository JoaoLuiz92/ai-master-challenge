# validation-lane — orquestrador e regra da faixa

Cópia publicada. No Cursor isto vive como regra `.cursor/rules/validation-lane.mdc` + agente `.cursor/agents/validation-lane.md`.

## Quando

Depois da última tarefa Execute, ou quando o usuário pedir validar / verificar / UAT / testes.

Não validar no chat. Não criar `validation-lane.md` dentro de `.specs/features/<feature>/`. O que muda por feature está na `spec.md` e na `tasks.md`.

## Topologia

1. `backend-tester` — só se a matriz de cobertura da feature tiver pytest.
2. `ui-tester` — Playwright MCP, se a spec tiver Independent Test observável no navegador.
3. `spec-verifier` — só depois que as faixas disparadas passarem. Autor ≠ verificador. Não escreve código de produto.

As faixas 1 e 2 rodam em paralelo quando as duas existem. A 3 espera o retorno delas.

## O que cada faixa lê

Feature ativa: a que o usuário nomeou; se não nomeou, a do **Agora** em `.specs/NEXT-ACTION.md`.

- Backend: comandos pytest da matriz e dos Gate Check Commands em `tasks.md`. Cwd `solution/`. Python `solution/.venv/Scripts/python.exe` (no host). No Docker: `docker compose run --rm --no-deps -e PYTHONPATH=/app/backend api python -m pytest /app/backend/tests -q`.
- UI: cada Independent Test da `spec.md` que manda abrir a UI vira um cenário, na ordem da spec. Vitest não substitui essa faixa.
- Verificador: cada AC → `file:line` + asserção. Relatório em `.specs/features/<feature>/validation.md`.

## UI (Playwright MCP)

Ferramentas: `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_select_option`, `browser_network_requests`, `browser_take_screenshot`. Interagir pelos refs do snapshot.

URL: stack no ar (compose ou os dois comandos locais do README). Descobrir a porta em execução; não fixar porta morta.

MCP desconectado: bloquear a faixa de UI. Não substituir por Chrome DevTools. Não criar suite `@playwright/test` versionada.

Prints, inclusive quando o cenário passa: a tela antes de interagir, a tela depois de cada clique, seleção ou troca de filtro, e a tela do estado assertado. PNG, página inteira. Pasta: `.specs/features/<feature>/ui-evidence/`. Nome: `NN-slug-passo.png`. Falha também gera print, com sufixo `-falha`.

## Contrato do orquestrador

1. Confirmar que as tarefas Execute da feature estão concluídas. Se não estiverem, FAIL na faixa, salvo pedido explícito de faixa parcial.
2. Disparar só as faixas que a feature exige.
3. Se alguma falhar ou a UI bloquear, não disparar o verificador. Devolver falhas ranqueadas.
4. Disparar `spec-verifier` com os relatórios, a spec e o diff da feature.
5. Expor o resumo compacto. Lacunas viram tarefa de correção. No máximo 3 ciclos de correção e nova verificação.

Testes afirmam o resultado da spec. Não pular, marcar xfail ou enfraquecer asserção para passar o gate.

## Saída compacta

```text
## Validation lane: <feature> — [PASS | FAIL | BLOCKED]

Backend: [N passed / fail summary / skipped]
UI (Playwright MCP): [scenarios pass/fail]
Verifier: [PASS/FAIL] — report path
Ranked gaps: ...
```
