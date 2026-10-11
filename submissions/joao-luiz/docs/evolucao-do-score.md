# Evolução da fórmula de scoring

Narrativa única de **o que mudou e por quê**. Números congelados em `analise-exploratoria.md`. Decisões formais nos ADRs. Este arquivo existe para um novo membro do time seguir a cadeia sem abrir sete documentos.

**Motor atual (v3):**

```
PRIORIDADE = sales_price × CHANCE(idade)
CHANCE     = tábua de sobrevivência por faixa (censura dos abertos); 0 além da parede
SCORE      = percentil 0–100 de PRIORIDADE só em Trabalhar
Filas      = Trabalhar (idade ≤ parede) | Decidir (idade > parede) | Revisar
```

`p̂` (classificador de conversão) **não entra** no ranking. A urgência com piso saiu do caminho de ordenação.

---

## Linha do tempo

| Versão | Quando | Fórmula | O que quebrou | O que entrou no lugar |
|--------|--------|---------|---------------|------------------------|
| **v0** | Briefing / questionamento, antes da EDA | Ordenar por chance de fechar (`p̂`) | Hipótese de mercado, sem evidência neste snapshot | Experimento com holdout temporal |
| **v1** | EDA 2026-10-08 | `PRIORIDADE = lista × urgência`; `p̂` fora | AUC 0,478; Spearman 0,999 vs. lista × urgência | Valor em risco; urgência reordena, `p̂` não |
| **v2** | Spec / ADR-007, mesmo ciclo | SCORE = percentil **da visão**; idade não exclui | Percentil global mente ao filtrar; corte por idade esvazia 89% da fila | A consulta recalcula SCORE/ESTADO; badge Esfriando |
| **v3** | Feature `chance-por-idade`, ADR-014/015/016 | `lista × CHANCE(idade)`; Decidir além da parede | Urgência com piso mantinha deal morto em Trabalhar | Tábua com censura; backtest vs. preço como gate |

---

## v0 — ranking por probabilidade (descartado)

Intuição padrão: treinar um classificador Won/Lost e ordenar o aberto pelo `p̂`.

Medimos nos 6.711 fechados, holdout temporal (`close_date` ≤ 2017-09-29 vs. depois):

- Win rate **plano** (~60–65%) em produto, setor e porte.
- AUC teste = **0,478** (piso combinado era 0,55).
- `p̂` só anda de 0,57 a 0,71.

Um score de conversão mandaria o time para **MG Special** (maior win rate, 0,4% da receita) — a armadilha que a Head descreveu.

Registro: `docs/analise-exploratoria.md` §5, `process-log/eda-2026-10-08.md`.

---

## v1 — valor em risco, sem `p̂` (ADR-001)

Nos abertos com conta e preço:

- Spearman (`p̂ × VALOR × URGÊNCIA` vs `VALOR × URGÊNCIA`) = **0,999** (19 dos 20 primeiros iguais).
- vs. só VALOR, sem urgência: Spearman 0,926, interseção dos 20 primeiros **7/20**.

Conclusão: o modelo é enfeite; a **urgência** é quem reordena. Valor = `sales_price` do catálogo (close/lista ≈ 1,0).

```
PRIORIDADE = list_price × urgência(idade)
```

Urgência (nós da EDA, ciclo Won): sobe até **57d** (mediana), fica alta até **106d** (p90), decai depois com piso 0,35. Deal velho de GTK 500 ainda pode ganhar de MG Special fresco.

**Não tomadas:** (B) `p̂ × valor × urgência` = mesma fila com ruído; (C) só conversão = MG Special no topo.

ADR: `docs/adr/001-priorizar-por-valor-em-risco.md`.

---

## v2 — SCORE relativo à visão; idade não exclui (ADR-003 + ADR-007)

Duas correções de produto em cima do motor v1.

### Percentil por visão, não na ingestão

PRIORIDADE é atributo do deal. SCORE é resposta à pergunta “onde **eu** foco?”. Percentil global calculado no load faria o mesmo deal parecer 82 no meu funil e no do escritório — o filtro só esconderia linhas (quebra CA7).

- SCORE = percentil 0–100 de PRIORIDADE **no conjunto filtrado**.
- Focar = `ceil(0,20 × N)` dessa visão (≥1 se não vazia).
- Empates compartilham o percentil; N=1 → SCORE 100 e Focar.
- Ingestão materializa PRIORIDADE; a query materializa SCORE e ESTADO.
- Export sai da visão atual — não há SCORE gravado no CSV de ingestão.

ADR: `docs/adr/007-score-percentil-por-visao.md`.

### Idade modula, não remove

Regra tentada no questionamento inicial: “mais velho que o ciclo de Won → Revisar / fora da fila”.

Números do snapshot:

- Won máximo **138d**; Engaging aberto mediana **165d**.
- Aplicar o corte: 1.869 / 2.089 (89%) iam para Revisar; sobrariam ~220.

É artefato de base que **termina** (sem `close_date`), não cadáver. Fila = Engaging **com** conta. Revisar = dado ruim (sem conta / sem `engage_date`). Idade > 106d → badge **Esfriando**, deal permanece.

Âncora `TODAY = 2017-12-31` (ADR-005): `date.today()` em 2026 zeraria a urgência de todo mundo.

ADRs: `003-idade-nao-exclui-da-fila.md`, `005-ancora-temporal-2017-12-31.md`.

---

## v3 — chance por idade; Decidir além da parede (ADR-014/015/016)

A urgência com piso (v1/v2) **não tirava** o deal parado da fila de trabalho. A Head pediu o contrário: o vendedor só trabalha o que ainda fecha.

- **CHANCE** por faixa = Won ÷ deals cuja idade cai na faixa, contando abertos como não-Won. Sem censura a curva sobe (viés de sobrevivência).
- **Parede** = maior idade de um Won na coorte (derivada no load, `Settings.wall_override` se precisar pinar). Acima dela, CHANCE = 0.
- **Trabalhar** = Engaging + conta + idade ≤ parede, ordenado por `valor × chance`. SCORE/Focar só neste conjunto.
- **Decidir** = Engaging + conta + idade > parede, ordenado por preço desc. Não é exclusão (ADR-003 continua certa em não apagar o pipeline); é outra cesta.
- **Revisar** inalterado (LEAD-16/17).
- **Gate:** `python backtest.py` — adota só se a mediana da captura nova − preço for > 0 nos cortes. Senão, reverte para v2 (CHANCE-23).

ADRs: `014-chance-por-idade-com-censura.md`, `015-fila-decidir-alem-da-parede.md`, `016-backtest-como-gate-do-motor.md`.

---

## O que a fórmula v3 **não** é

- Não é ML no caminho crítico (ADR-006): ranking 100% aritmético sobre CSV.
- Não compara SCORE entre visões (o rollup do gestor usa contagem e valor em Trabalhar vs Decidir; o destaque é o **valor parado**).
- Não usa `close_value` do aberto (só existe depois de fechar).

---

## Como reproduzir o experimento descartado

A partir de `submissions/joao-luiz/solution/`:

```text
.venv\Scripts\python -m pip install -r requirements-eda.txt
.venv\Scripts\python eda.py
```

O script imprime AUC, Spearman e as tabelas que alimentam este documento.
