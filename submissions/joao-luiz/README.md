# Submissão — João Luiz — Challenge 003 (Lead Scorer)

## Sobre mim

- **Nome:** João Luiz
- **LinkedIn:** _(a preencher)_
- **Challenge escolhido:** [003 — Lead Scorer](../../challenges/build-003-lead-scorer/README.md)

---

## Visão geral

Vendedores priorizam no feeling; o snapshot mostra win rate plano (~63%) e valor variando 400×. Um score de conversão (AUC 0,478) mandaria o time para MG Special. A fila ordena por **preço de lista × urgência**; o SCORE na UI é o **percentil dessa prioridade na visão** (meus deals / time / filtros).

| Camada | Papel |
|--------|--------|
| Backend | FastAPI. Quatro CSVs em memória no startup. Score aritmético, sem LLM no caminho crítico. |
| Frontend | React. Papel vendedor/gestor, fila, Revisar, badge, rollup, export. Textos em português. |
| Dados | CSVs em `solution/data/`. O durável é o CSV exportado da visão atual. |

Fórmula e o porquê de cada versão: [`docs/evolucao-do-score.md`](docs/evolucao-do-score.md). O registro do que foi entregue (`delivery.md`) entra só no fechamento da spec.

---

## Processo

O como o agente trabalha (spec, uma tarefa por janela, validação) vive em [`AGENTS.md`](AGENTS.md) e em [`.specs/`](.specs/NEXT-ACTION.md). Esta seção não copia esse fluxo.

Foco atual: [`.specs/NEXT-ACTION.md`](.specs/NEXT-ACTION.md).

---

## Como rodar

A partir de `solution/`.

Com Docker, a API fica em http://127.0.0.1:8000 e a UI em http://127.0.0.1:8080:

```text
docker compose up --build
```

Sem Docker, dois comandos. A UI fica em http://127.0.0.1:5173 e chama a API em `/api`:

```text
.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --app-dir backend --host 127.0.0.1 --port 8000
npm --prefix frontend run dev
```

Para repetir a EDA:

```text
.venv\Scripts\python.exe -m pip install -r requirements-eda.txt
.venv\Scripts\python.exe eda.py
```

---

## Registro de processo — Como usei IA

> **Este bloco é obrigatório.** Sem ele, a submissão é desclassificada. Narrativa longa da EDA: [`process-log/eda-2026-10-08.md`](process-log/eda-2026-10-08.md).

### Ferramentas usadas

| Ferramenta | Para que usou |
|------------|--------------|
| Cursor | EDA, spec, ADRs, harness do agente e o Execute |

### Fluxo de trabalho

1. EDA nos CSVs antes de congelar a fórmula. O dado derrubou corte por idade e classificador.
2. Spec fechada, com contrato de entrega, antes de escrever o app.
3. Execute uma tarefa por vez, com a cadeia de commits visível (harness → evidência → spec → tarefas), em vez de um dump único.

### Onde a IA errou e como corrigi

O primeiro commit desta branch foi desfeito de propósito: faltava o harness. Sem `AGENTS.md`, o próximo agente reabria a spec ou empilhava tudo num único commit.

Na EDA, três hipóteses da IA não sobreviveram ao dado: cortar deal velho da fila (esvaziaria 89% do funil), rankear por `p̂` (AUC 0,478) e juntar produto sem o alias `GTXPro` (1.480 linhas, o produto que mais fatura, ficariam sem preço). Números: `process-log/eda-2026-10-08.md`.

### O que eu adicionei que a IA sozinha não faria

- Cadeia de commits visível, em vez de um único commit com o app pronto.
- Teto de contexto no Execute: fechar a tarefa atual; a próxima abre em janela nova.
- Quem testa não é quem escreveu: faixa de validação com subagentes separados.
- Fila da tarefa corrente e memória de erro já corrigido fora deste README, para o processo do agente não se misturar com o relato do MVP.

---

## Evidências

- [x] Harness de agentes (`AGENTS.md` + `.specs/`)
- [x] Narrativa da EDA (`process-log/eda-2026-10-08.md`)
- [x] Evolução da fórmula (`docs/evolucao-do-score.md`)
- [x] ADRs (`docs/adr/`)
- [x] Spec / design / tasks
- [x] Capturas da UI (vendedor / gestor) — `.specs/features/lead-scorer/ui-evidence/`
- [ ] Exportações de chat — depois do Execute
- [x] Histórico git — cadeia aberta

---

_Execute e a faixa de validação fecharam. O registro está em [`.specs/features/lead-scorer/delivery.md`](.specs/features/lead-scorer/delivery.md)._
