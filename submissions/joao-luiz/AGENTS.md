# AGENTS.md

Instruções para qualquer agente em `submissions/joao-luiz/`.
> Documento perene. Só regras estáveis. O que muda a cada tarefa vive em `.specs/` (este arquivo só aponta).

## Como trabalhar

- **Spec-driven:** skill `tlc-spec-driven`. Ao retomar, ler `.specs/NEXT-ACTION.md` e executar só o **Agora**. Uma tarefa por janela. Antes de codar, a armadilha em `.specs/CONCERNS.md` que toca essa tarefa.
- **Não inventar.** Dúvida: `spec.md` → `design.md` → ADRs / EDA. Se ainda faltar, parar e perguntar.
- **Provar antes de marcar done.** O gate da tarefa passa antes do checkbox. Testes afirmam o AC da spec. Não pular, xfail ou enfraquecer asserção.
- **Contexto (45%):** no meio da tarefa, fechar essa tarefa por completo (implementar, testes, gate, `tasks.md`, commit, reescrever `NEXT-ACTION.md`). A próxima nasce em outra janela. Não compactar a janela para continuar.
- **Não narrar a fase.** Fazer o artefato.
- **Validar fora do chat.** Última tarefa Execute, ou pedido de validar / UAT / testes: disparar o subagente `validation-lane`. Contrato publicado: `docs/harness/`. A spec da feature diz o que assertar.

## Guard-rails

- O PR **só** altera `submissions/joao-luiz/`. Não mexer no resto do repositório. `.cursor/` desta pasta e o junction `.cursor` da raiz do monorepo são **locais**: não entram no git. O harness publicado está em `docs/harness/`.
- Prosa, commits e docs em **português**. Código, API e identificadores em **inglês**. UI do vendedor/gestor em **português** (ADR-004).
- A raiz ignora `submissions/`: entrar com `git add -f` nos caminhos da submissão, **sem** `.cursor/`, `.playwright-mcp/`, `solution/.venv/`, `node_modules/`, `__pycache__/`, segredos. Um commit atômico por tarefa, Conventional Commits, corpo com o porquê. Sem squash. Sem push sem pedido.
- `PRIORIDADE = sales_price × CHANCE(idade)`. SCORE = percentil **de Trabalhar** na visão. `p̂` fora do ranking. Relato: ADR-014.
- Idade **acima da parede** (máx. Won da coorte) sai de Trabalhar e vai para **Decidir** — não some do produto. Badge Esfriando (>106d) é só pista visual. `TODAY = 2017-12-31`. Relato: `.specs/CONCERNS.md`, ADR-015.
- Pytest do backend na imagem Docker (WDAC bloqueia pandas no host). Backtest: `python backtest.py` a partir de `solution/`.
- Alias `GTXPro` → `GTX Pro` antes do preço. Relato no mesmo arquivo.
- Em memória, sem LLM no caminho crítico. Trabalhar: frase de chance. Decidir: frase da parede + “Requalificar ou encerrar”. Revisar: dado ruim.
- Pin: `fastapi==0.112.4`, `pydantic==1.10.22`, `starlette==0.38.6`. Relato em `CONCERNS.md`.
- O bloco **Como usei IA** fica no README, com os quatro títulos do template. Relato em `CONCERNS.md`.
- Faixa de UI: Playwright MCP. Plugin desligado **bloqueia** a faixa. Não usar Chrome DevTools no lugar. Vitest não substitui. O verificador não escreve código de produto.

## Repositório

Ferramenta para o vendedor ver onde focar no pipeline, e para o gestor ver o valor parado em Decidir. Dados: CSVs do CRM, em memória.

- `solution/` — app. Cwd dos comandos abaixo. `backend/` (FastAPI), `data/` (CSVs), `eda.py` (análise, não é o app).
- `.specs/` — spec, design, tasks, fila, estado, erros que não voltam.
- `docs/` — EDA, evolução da fórmula, ADRs, harness publicado (`docs/harness/`).
- `process-log/` — narrativa de uma sessão de desenvolvimento. Um arquivo por sessão.

## Fonte da verdade (ponteiros — não duplicar)

- `.specs/NEXT-ACTION.md` — o que fazer agora (ler primeiro)
- `.specs/CONCERNS.md` — risco em aberto e armadilha que não volta
- `.specs/STATE.md` — decisões (AD-*)
- `.specs/features/<feature>/` — `spec.md` · `design.md` · `tasks.md` · `validation.md`. `delivery.md` só depois da última tarefa e da faixa, com o que a execução fez.
- `docs/harness/` — contratos da faixa (orquestrador, backend, UI, verificador). `.cursor/` e `.playwright-mcp/` são locais e não entram no git.
- `docs/evolucao-do-score.md` · `docs/adr/` · `docs/analise-exploratoria.md`

Evidência no disco ganha de snapshot velho.

## Commands

Cwd: `submissions/joao-luiz/solution`. Python: `.venv\Scripts\python.exe`.

```text
docker compose run --rm --no-deps -e PYTHONPATH=/app/backend -v "%CD%/backend:/app/backend" api python -m pytest /app/backend/tests -q

npm --prefix frontend test -- --run

python backtest.py
```

`docker compose up --build` e os dois comandos locais do app constam no README. No host Windows com WDAC, não rode pytest/pandas fora da imagem.

## Manutenção deste arquivo

Atualize o `AGENTS.md` só quando mudar algo estrutural e duradouro:

- Guard-rail novo, que vale para o resto do projeto.
- Stack, comando de teste, ou topologia de pastas.
- Ponteiro novo em `.specs/` ou `docs/`.

Não atualize aqui: tarefa atual, o que a última janela entregou, decisão recente, armadilha nova. Isso vai para `NEXT-ACTION.md`, `STATE.md` ou `CONCERNS.md`.
