# Submissão — João Luiz — Challenge 003 (Lead Scorer)

## Sobre mim

- **Nome:** João Luiz Da Rosa Junior
- **LinkedIn:** https://www.linkedin.com/in/joaoluiz92/
- **Challenge escolhido:** [003 — Lead Scorer](../../challenges/build-003-lead-scorer/README.md)

---

## Executive Summary

Vendedores priorizam "no feeling": o snapshot mostra win rate plano (~63%) e valor variando 400×. Construí uma ferramenta **FastAPI + React** que o vendedor abre na segunda de manhã e vê, em segundos, **onde focar** — a fila **Trabalhar** ordenada por **preço de lista × chance de fechar por idade**, cada deal com a frase de chance em português. Deal além da parede (nenhum Won da base fechou depois daquela idade) sai do trabalho e vai para **Decidir** (requalificar ou encerrar). `p̂` de classificador **não** entra no ranking (AUC 0,478). O gestor vê o **valor parado** por vendedor e pode **passar um deal para um colega do mesmo escritório**. Recomendação: `docker compose up --build`; o único artefato durável é o CSV exportado da visão atual.

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

# Backtest do motor v3 (sem leakage) — a partir de solution/
python backtest.py
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

Quatro features, todas com Execute concluído e faixa de validação **PASS**.

| Feature | O que faz | Validação |
|---------|-----------|-----------|
| **`lead-scorer`** — o motor | FastAPI carrega os 4 CSVs em memória no startup, normaliza, calcula PRIORIDADE/SCORE/ESTADO e serve `/api/queue`, `/api/rollup`, `/api/export.csv`. Score 100% aritmético, sem LLM no caminho crítico. | 68 pytest + verificador 38/38 — [`delivery.md`](.specs/features/lead-scorer/delivery.md) · [`validation.md`](.specs/features/lead-scorer/validation.md) |
| **`foco-ui`** — a mesa de trabalho | React. Estações endereçáveis `/vendedor` e `/gestor`, fila com Focar (herói) / Acompanhar / Revisar, card com motivo e ação, badge Esfriando, rollup do gestor, drill por vendedor, export da visão. Textos em português. | vitest 70 + verificador 38/38 + 8 cenários UI — [`validation.md`](.specs/features/foco-ui/validation.md) |
| **`repassar-deal`** — o repasse | No drill do gestor, "Passar para colega" move **um** `opportunity_id` para um colega do **mesmo escritório**. O deal continua único, sai de uma fila e entra na outra; o card de destino mostra "Veio de {dono anterior}". Só na sessão. | 96 pytest + verificador 19/19 + sensor 3/3 + 4 cenários UI — [`validation.md`](.specs/features/repassar-deal/validation.md) |
| **`chance-por-idade`** — chance e Decidir | Tábua de sobrevivência com censura; `PRIORIDADE = lista × CHANCE`; filas Trabalhar / Decidir / Revisar; rollup com valor parado. | 133 pytest + verificador 29/29 + sensor 3/3 + 4 cenários UI — [`validation.md`](.specs/features/chance-por-idade/validation.md) |

### Lógica de scoring — e o porquê

```text
PRIORIDADE = sales_price × CHANCE(idade)
CHANCE     = Won ÷ deals da faixa de idade (abertos = censurados); 0 além da parede
SCORE      = percentil 0–100 de PRIORIDADE só em Trabalhar
Filas      = Trabalhar | Decidir (preço desc) | Revisar
```

- **Valor × chance, não urgência com piso.** A tábua de sobrevivência conta os ainda abertos; sem isso a chance cresce com a idade. `p̂` de classificador continua fora (AUC 0,478). [ADR-014](docs/adr/014-chance-por-idade-com-censura.md) (substitui [ADR-001](docs/adr/001-priorizar-por-valor-em-risco.md)).
- **Parede derivada, não literal.** Maior idade de um Won na coorte, exposta em `Settings` (`chance_bands`, `wall_override`). Deal **acima** da parede vai para Decidir; na parede ainda é Trabalhar. [ADR-015](docs/adr/015-fila-decidir-alem-da-parede.md) (substitui [ADR-003](docs/adr/003-idade-nao-exclui-da-fila.md) — o deal não some do produto).
- **SCORE é de Trabalhar, na visão.** Percentil só nos deals trabalháveis do filtro. [ADR-007](docs/adr/007-score-percentil-por-visao.md).
- **Esfriando é pista visual.** O badge (>106d) não decide mais a cesta.
- **Gate de adoção.** `python backtest.py` — a troca só entra se a nova ordem capturar mais receita que ordenar por preço. [ADR-016](docs/adr/016-backtest-como-gate-do-motor.md).
- **Âncora temporal `TODAY = 2017-12-31`**. [ADR-005](docs/adr/005-ancora-temporal-2017-12-31.md).
- **Explainability sem LLM.** Frase de chance / frase da parede em português, números do dado. [ADR-006](docs/adr/006-sem-llm-no-caminho-critico.md).

Cadeia v0 → v1 → v2 → v3: [`docs/evolucao-do-score.md`](docs/evolucao-do-score.md). Decisões: [`docs/adr/`](docs/adr/README.md).

### Recomendações

- Começar pela estação do vendedor: a fila ordenada com motivo/ação resolve o job-to-be-done da segunda-feira sem planilha.
- O gestor usa o rollup para atacar o **valor parado** em Decidir e, no drill, repassar o deal para quem tem capacidade.
- O durável é o **CSV exportado** da visão atual — é o que o vendedor leva para fora da ferramenta.
- Para produção: trocar o estado em memória por CRM real (donos, histórico, "já revisei") mantendo o motor intacto.

### Limitações (de propósito)

- **Sem banco e sem arquivo de sessão.** Os CSVs entram na memória no startup. Recarregar a API (`docker compose down` / subir de novo) **volta o funil ao snapshot**. Não é falha: o desafio é um dataset público de demonstração; um banco faria cada restart deixar de ser o mesmo funil. O único artefato durável é o **CSV exportado**. [ADR-002](docs/adr/002-fastapi-react-em-memoria.md).
- **Repasse de deal vale só na sessão.** O botão "Passar para colega" está entregue e validado no drill do gestor, mas o movimento é **em memória**: só colega do **mesmo escritório**, o `opportunity_id` continua um só, e **restart devolve o dono do CSV**. Em produção isso viveria no CRM. [ADR-013](docs/adr/013-repasse-so-na-sessao.md).
- **Sem login.** Papel vendedor/gestor é a estação na URL, não SSO.
- **`p̂` não entra no ranking.** AUC 0,478; o classificador empurraria o time para deals irrelevantes (experimento descartado).
- **A maior parte do Engaging aberto cai em Decidir.** A mediana dos abertos (165d) passa da parede de Won (~138d): é o corte do snapshot, não cadáver escondido. Eles não saem do produto.
- **Curva global, não por produto.** Recalibrar por segmento fica para a v2 da chance.
- **Backtest de adoção.** Se `python backtest.py` emitir `adopted=false`, o motor v3 não se justifica e reverte para lista × urgência.

---

## Process Log — Como usei IA

> **Este bloco é obrigatório.** Sem ele, a submissão é desclassificada.
>
> Resumo aqui; narrativa por sessão em [`process-log/`](process-log/) ([EDA](process-log/eda-2026-10-08.md) · [motor v3](process-log/chance-por-idade-2026-10-11.md)). O git history é a outra evidência: um commit por tarefa.

### Ferramentas usadas

| Ferramenta | Para que usei |
|------------|--------------|
| Cursor (agente + skill `tlc-spec-driven`) | EDA, PRD, specs, ADRs e código, uma tarefa por vez |
| Subagentes do Cursor | Faixa de validação: backend, UI e verificador independente (autor ≠ verificador) |
| Playwright MCP | Browser real na faixa de UI: cliques, prints, export comparado à tela |

### Workflow

1. Do briefing saíram hipóteses para **testar**, não implementar (`p̂`, corte por idade, join de produto).
2. EDA nos CSVs como juiz; números congelados em [`docs/analise-exploratoria.md`](docs/analise-exploratoria.md).
3. PRD dividido em quatro features, cada uma com spec (critérios EARS), design e tarefas atômicas.
4. Cada prompt = uma tarefa, com critério de aceite e gate. Um commit por tarefa (82 no total).
5. Validação fora do chat pelo harness ([`docs/harness/`](docs/harness/README.md)). A fórmula iterou quatro vezes ([`docs/evolucao-do-score.md`](docs/evolucao-do-score.md)).

### Onde a IA errou e como corrigi

- Queria cortar deal velho da fila; a EDA mostrou que isso esvaziaria 89% do funil.
- Queria rankear por `p̂`; o holdout deu AUC 0,478.
- Juntava produto sem o alias `GTXPro`; 1.480 linhas ficariam sem preço.
- Fez o app num commit só, sem harness; desfiz e recomecei.
- Na validação: um mutante sobreviveu na `foco-ui` (`19adc75`) e o export da v3 saiu sem a coluna `fila` (`cb2f89f`).

Detalhe de cada caso nos logs de sessão.

### O que eu adicionei que a IA sozinha não faria

- Derrubar `p̂` e o corte por idade com números, contra a intuição de mercado.
- Autor ≠ verificador, com `file:line` por critério e mutantes que o teste tem de matar.
- Backtest como gate: a v3 só entra se capturar mais receita que ordenar por preço ([ADR-016](docs/adr/016-backtest-como-gate-do-motor.md)).
- Fechar uma tarefa antes de abrir a próxima, com a cadeia de commits legível.

---

## Evidências

- [x] Harness de agentes — raciocínio e contratos em [`docs/harness/`](docs/harness/README.md); `AGENTS.md` + `.specs/`
- [x] Narrativa da EDA e do motor v3 (`process-log/`)
- [x] Evolução da fórmula (`docs/evolucao-do-score.md`)
- [x] ADRs (`docs/adr/`)
- [x] Spec / design / tasks das quatro features (`.specs/features/`)
- [x] Capturas da UI (vendedor / gestor / repasse / chance) — `.specs/features/*/ui-evidence/`
- [x] Relatórios de validação independentes — `lead-scorer`, `foco-ui`, `repassar-deal` e `chance-por-idade` (`validation.md`)
- [x] Histórico git — cadeia de commits aberta por tarefa

---

## Mapa do repositório

- `solution/` — o app. `backend/` (FastAPI), `frontend/` (React), `data/` (CSVs), `docker-compose.yml`, `eda.py`.
- `.specs/` — spec, design, tasks, validação e estado do processo. Começar por [`.specs/NEXT-ACTION.md`](.specs/NEXT-ACTION.md).
- `docs/` — EDA, evolução da fórmula, ADRs e o [harness publicado](docs/harness/README.md).
- `process-log/` — narrativa por sessão de desenvolvimento.
- `AGENTS.md` — como qualquer agente trabalha nesta pasta.

_As quatro features fecharam Execute e faixa de validação. Registro em cada `.specs/features/<feature>/validation.md`._
