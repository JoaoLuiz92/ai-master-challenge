# Submissão — João Luiz — Challenge 003 (Lead Scorer)

## Sobre mim

- **Nome:** João Luiz
- **LinkedIn:** _(a preencher)_
- **Challenge escolhido:** [003 — Lead Scorer](../../challenges/build-003-lead-scorer/README.md)

---

## Resumo executivo

Vendedores priorizam no feeling; o snapshot mostra win rate plano (~63%) e valor variando 400×. Um score de conversão (AUC 0,478) mandaria o time para MG Special. A fila do v1 ordena por **preço de lista × urgência**; o SCORE na UI é o **percentil dessa prioridade na visão** (meus deals / time / filtros).

Este commit é só o **harness** da submissão (`AGENTS.md`, `DELIVERY.md`, este README). EDA, ADRs, spec e o app entram nos commits seguintes — não neste.

---

## Harness (este commit)

| Artefato | Para que serve |
|----------|----------------|
| [`AGENTS.md`](AGENTS.md) | Regras para qualquer agente nesta pasta: fonte da verdade, Execute um T por vez, validation-lane, git (`add -f`), produto congelado |
| [`DELIVERY.md`](.specs/features/lead-scorer/DELIVERY.md) | Contrato Specify → Execute / avaliador: o que entregar, fórmula, papéis, explainability |
| Este README | Identidade, tese do produto e cadeia de commits visível |

O PR **só** altera `submissions/joao-luiz/`. Prosa e commits em português; código/API em inglês (ADR-004).

---

## Solução

Ainda não há código de produção neste commit. A cadeia prevista:

1. Harness (AGENTS + DELIVERY + README) — **aqui**
2. EDA + CSVs + `process-log/eda-*`
3. ADRs + `docs/evolucao-do-score.md`
4. `.specs` (spec / design / tasks / validation-lane)
5. Execute T1–T27, um commit atômico por tarefa

Fórmula congelada (detalhe no DELIVERY e, depois, em `docs/evolucao-do-score.md`): `PRIORIDADE = sales_price × urgência`; SCORE = percentil da visão; `p̂` fora; idade não exclui; `TODAY = 2017-12-31`.

### Como o avaliador reproduz (quando o app existir)

A partir de `solution/` — comandos de `docker compose` e setup local entram no Execute (T26). Até lá, nada para subir.

---

## Registro de processo — Como usei IA

> **Este bloco é obrigatório.** Sem ele, a submissão é desclassificada.

### Ferramentas usadas

| Ferramenta | Para que usou |
|------------|--------------|
| Cursor | Spec TLC, harness (`AGENTS.md` / `DELIVERY.md`), EDA e ADRs nas sessões seguintes |

### Fluxo de trabalho

1. Spec fechada → `DELIVERY.md` obrigatório antes do Execute.
2. `AGENTS.md` como ponto de entrada de qualquer agente (pasta, idioma, lane, git).
3. Execute ainda não começou; um commit por tarefa a partir de T1.

### Onde a IA errou e como corrigi

O primeiro commit desta branch foi desfeito de propósito: faltava o harness. Sem `AGENTS.md`, o próximo agente reabria spec ou empilhava tudo num único commit.

### O que eu adicionei que a IA sozinha não faria

Cadeia de commits visível para o avaliador (harness → evidência → spec → T1–T27), em vez de um dump único.

---

## Evidências

- [x] Harness de agentes (`AGENTS.md`, `DELIVERY.md`)
- [ ] Narrativa da EDA (`process-log/eda-*.md`) — commit 2
- [ ] Evolução da fórmula (`docs/evolucao-do-score.md`) — commit 3
- [ ] ADRs (`docs/adr/`) — commit 3
- [ ] Spec / design / tasks — commit 4
- [ ] Capturas da UI (vendedor / gestor) — depois do Execute
- [ ] Exportações de chat — depois do Execute
- [x] Histórico git — este commit abre a cadeia

---

_Submissão em andamento. Primeiro commit: harness, não o app._
