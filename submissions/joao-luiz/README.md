# Submissão — João Luiz — Challenge 003 (Lead Scorer)

## Sobre mim

- **Nome:** João Luiz Da Rosa Junior
- **LinkedIn:** https://www.linkedin.com/in/joaoluiz92/
- **Challenge escolhido:** [003 — Lead Scorer](../../challenges/build-003-lead-scorer/README.md)

---

## Executive Summary

Vendedores priorizam "no feeling": o snapshot mostra win rate plano (~63%) e valor variando 400×. Construí uma ferramenta **FastAPI + React** que o vendedor abre na segunda de manhã e vê, em segundos, **onde focar** — a fila de deals abertos ordenada por **valor em risco** (preço de lista × urgência), cada um com **motivo e ação em português**. O achado que definiu o produto veio da EDA: um classificador de conversão não tem sinal neste dataset (AUC 0,478), então `p̂` **não** entra no ranking — mandaria o time para deals irrelevantes. O gestor tem uma visão de rollup por vendedor e pode **passar um deal esfriando para um colega do mesmo escritório**. Recomendação: rodar com `docker compose up --build` e usar a estação do vendedor; o único artefato durável é o CSV exportado da visão atual.

---

## Como rodar

Pré-requisito: Docker. Tudo roda a partir de `solution/`.

### Com Docker (recomendado)

```text
cd solution
docker compose up --build
```

- UI (vendedor/gestor): **http://127.0.0.1:8080**
- API: **http://127.0.0.1:8000** (ex.: `GET /api/agents`, `/api/queue?view=mine&agent=Anna+Snelling`, `/api/rollup`)
- Primeira tela: `/` redireciona para `/vendedor?agente=Anna+Snelling`. Trocar de papel pelo trilho à esquerda (`/vendedor` ↔ `/gestor`).
- Parar: `docker compose down`. **Reiniciar volta o funil ao snapshot** (dados só em memória; ver Limitações).

### Sem Docker (modo dev)

Dois serviços. A UI fica em http://127.0.0.1:5173 e chama a API via proxy `/api` (porta 8000).

```text
cd solution

python -m venv .venv
.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --app-dir backend --host 127.0.0.1 --port 8000

npm --prefix frontend install
npm --prefix frontend run dev
```

> Nota de ambiente: em máquinas Windows com WDAC/AppLocker, a extensão nativa do `pandas` pode ser bloqueada no host, travando a API local. Nesse caso use o caminho Docker, que é o suportado de ponta a ponta.

### Testes

```text
cd solution

# Backend (pytest) — roda dentro da imagem, por causa do bloqueio de pandas no host
docker compose run --rm --no-deps -e PYTHONPATH=/app/backend api python -m pytest /app/backend/tests -q

# Frontend (vitest)
npm --prefix frontend install
npm --prefix frontend test -- --run
```

### Reproduzir a EDA

```text
cd solution
.venv\Scripts\python.exe -m pip install -r requirements-eda.txt
.venv\Scripts\python.exe eda.py
```

O script imprime AUC, Spearman e as tabelas que sustentam a fórmula.

---

## A solução

### Abordagem

1. **EDA antes da fórmula.** Olhei os quatro CSVs antes de congelar qualquer lógica. O dado derrubou três intuições (abaixo).
2. **Spec fechada antes do app.** Cada feature tem `spec.md` → `design.md` → `tasks.md`, com critérios de aceite em EARS e contrato de entrega.
3. **Execute uma tarefa por janela**, com a cadeia de commits visível (harness → evidência → spec → tarefas), em vez de um dump único.
4. **Quem valida não é quem escreveu:** faixa de validação com subagentes separados (backend, UI em Playwright, verificador independente). Contratos: [`docs/harness/`](docs/harness/README.md).

### O que foi entregue

Três features, todas com Execute concluído e faixa de validação **PASS**:

| Feature | O que faz | Validação |
|---------|-----------|-----------|
| **`lead-scorer`** — o motor | FastAPI carrega os 4 CSVs em memória no startup, normaliza, calcula PRIORIDADE/SCORE/ESTADO e serve `/api/queue`, `/api/rollup`, `/api/export.csv`. Score 100% aritmético, sem LLM no caminho crítico. | 68 pytest + verificador 38/38 — [`delivery.md`](.specs/features/lead-scorer/delivery.md) · [`validation.md`](.specs/features/lead-scorer/validation.md) |
| **`foco-ui`** — a mesa de trabalho | React. Estações endereçáveis `/vendedor` e `/gestor`, fila com Focar (herói) / Acompanhar / Revisar, card com motivo e ação, badge Esfriando, rollup do gestor, drill por vendedor, export da visão. Textos em português. | vitest 70 + verificador 38/38 + 8 cenários UI — [`validation.md`](.specs/features/foco-ui/validation.md) |
| **`repassar-deal`** — o repasse | No drill do gestor, "Passar para colega" move **um** `opportunity_id` para um colega do **mesmo escritório**. O deal continua único, sai de uma fila e entra na outra; o card de destino mostra "Veio de {dono anterior}". Só na sessão. | 96 pytest + verificador 19/19 + sensor 3/3 + 4 cenários UI — [`validation.md`](.specs/features/repassar-deal/validation.md) |

### Lógica de scoring — e o porquê

```text
PRIORIDADE = sales_price × urgência(idade)        # atributo estável do deal
SCORE      = percentil 0–100 de PRIORIDADE na visão filtrada
ESTADO     = Focar (ceil(20% × N) da visão) | Acompanhar | Revisar
```

- **Valor em risco, não probabilidade.** `p̂` (chance de fechar) **não** entra no ranking: AUC 0,478 no holdout temporal e Spearman 0,999 entre a fila com e sem `p̂`. Quem reordena é o **valor** (varia 400×) junto com a **urgência**. [ADR-001](docs/adr/001-priorizar-por-valor-em-risco.md).
- **SCORE é da visão, não global.** Percentil calculado no conjunto filtrado (meus deals / time / filtros); percentil global mentiria ao filtrar. O SCORE da UI é "posição nesta visão, 0–100". [ADR-007](docs/adr/007-score-percentil-por-visao.md).
- **Idade modula, não exclui.** Excluir deal velho esvaziaria 89% do funil (mediana Engaging 165d > máx Won 138d, efeito de snapshot). Idade só muda a urgência; acima de **106 dias** (p90 de Won) ganha o badge **Esfriando**. Revisar = dado ruim (sem conta / sem `engage_date`). [ADR-003](docs/adr/003-idade-nao-exclui-da-fila.md).
- **Âncora temporal `TODAY = 2017-12-31`** (máxima data do pipeline); usar a data real zeraria a urgência de todo mundo. [ADR-005](docs/adr/005-ancora-temporal-2017-12-31.md).
- **Explainability sem LLM.** Cada deal traz fator positivo, risco e ação em português, por template aritmético — reproduzível a cada run. [ADR-006](docs/adr/006-sem-llm-no-caminho-critico.md).

Cadeia completa v0 → v1 → v2 da fórmula: [`docs/evolucao-do-score.md`](docs/evolucao-do-score.md). Todas as decisões: [`docs/adr/`](docs/adr/README.md).

### Recomendações

- Começar pela estação do vendedor: a fila ordenada com motivo/ação resolve o job-to-be-done da segunda-feira sem planilha.
- O gestor usa o rollup para achar valor esfriando e, no drill, repassar o deal para quem tem capacidade.
- O durável é o **CSV exportado** da visão atual — é o que o vendedor leva para fora da ferramenta.
- Para produção: trocar o estado em memória por CRM real (donos, histórico, "já revisei") mantendo o motor intacto.

### Limitações (de propósito)

- **Sem banco e sem arquivo de sessão.** Os CSVs entram na memória no startup. Recarregar a API (`docker compose down` / subir de novo) **volta o funil ao snapshot**. Não é falha: o desafio é um dataset público de demonstração; um banco faria cada restart deixar de ser o mesmo funil. O único artefato durável é o **CSV exportado**. [ADR-002](docs/adr/002-fastapi-react-em-memoria.md).
- **Repasse de deal vale só na sessão.** O botão "Passar para colega" está entregue e validado no drill do gestor, mas o movimento é **em memória**: só colega do **mesmo escritório**, o `opportunity_id` continua um só, e **restart devolve o dono do CSV**. Em produção isso viveria no CRM. [ADR-013](docs/adr/013-repasse-so-na-sessao.md).
- **Sem login.** Papel vendedor/gestor é a estação na URL, não SSO.
- **`p̂` não entra no ranking.** AUC 0,478; o score de conversão empurraria o time para deals irrelevantes (documentado como experimento descartado).

---

## Process Log — Como usei IA

> **Este bloco é obrigatório.** Sem ele, a submissão é desclassificada. Narrativa longa da EDA: [`process-log/eda-2026-10-08.md`](process-log/eda-2026-10-08.md).

### Ferramentas usadas

| Ferramenta | Para que usou |
|------------|--------------|
| Cursor | EDA, spec, ADRs, Execute, e o harness de agentes (faixa de validação) |
| Playwright MCP | Browser real na faixa de UI — cliques, prints, export vs. tela. Não é o produto. |

### Workflow

1. EDA nos CSVs antes de congelar a fórmula. O dado derrubou corte por idade e classificador.
2. Spec fechada, com contrato de entrega, antes de escrever o app.
3. Execute uma tarefa por vez, com a cadeia de commits visível (harness → evidência → spec → tarefas), em vez de um dump único.
4. Validação fora do chat: subagentes de backend, UI (Playwright MCP) e um verificador independente (autor ≠ verificador). Por que essa topologia existe: [`docs/harness/`](docs/harness/README.md).

### Onde a IA errou e como corrigi

O primeiro commit desta branch foi desfeito de propósito: faltava o harness. Sem `AGENTS.md`, o próximo agente reabria a spec ou empilhava tudo num único commit.

Na EDA, três hipóteses da IA não sobreviveram ao dado: cortar deal velho da fila (esvaziaria 89% do funil), rankear por `p̂` (AUC 0,478) e juntar produto sem o alias `GTXPro` (1.480 linhas, o produto que mais fatura, ficariam sem preço). Números: [`process-log/eda-2026-10-08.md`](process-log/eda-2026-10-08.md).

### O que eu adicionei que a IA sozinha não faria

- Cadeia de commits visível, em vez de um único commit com o app pronto.
- Teto de contexto no Execute: fechar a tarefa atual; a próxima abre em janela nova.
- Quem testa não é quem escreveu: faixa de validação com subagentes separados ([`docs/harness/`](docs/harness/README.md)). A pasta `.cursor/` desta máquina é local e não entra no PR.
- Decisão de negócio ancorada no dado (derrubar `p̂` e o corte por idade), não na intuição de mercado.

---

## Evidências

- [x] Harness de agentes — raciocínio e contratos em [`docs/harness/`](docs/harness/README.md); `AGENTS.md` + `.specs/`
- [x] Narrativa da EDA (`process-log/eda-2026-10-08.md`)
- [x] Evolução da fórmula (`docs/evolucao-do-score.md`)
- [x] ADRs (`docs/adr/`)
- [x] Spec / design / tasks das três features (`.specs/features/`)
- [x] Capturas da UI (vendedor / gestor / repasse) — `.specs/features/*/ui-evidence/`
- [x] Relatórios de validação independentes — `lead-scorer`, `foco-ui` e `repassar-deal` (`validation.md`)
- [x] Histórico git — cadeia de commits aberta por tarefa

---

## Mapa do repositório

- `solution/` — o app. `backend/` (FastAPI), `frontend/` (React), `data/` (CSVs), `docker-compose.yml`, `eda.py`.
- `.specs/` — spec, design, tasks, validação e estado do processo. Começar por [`.specs/NEXT-ACTION.md`](.specs/NEXT-ACTION.md).
- `docs/` — EDA, evolução da fórmula, ADRs e o [harness publicado](docs/harness/README.md).
- `process-log/` — narrativa por sessão de desenvolvimento.
- `AGENTS.md` — como qualquer agente trabalha nesta pasta.

_As três features fecharam Execute e faixa de validação. Registro em cada `.specs/features/<feature>/validation.md`._
