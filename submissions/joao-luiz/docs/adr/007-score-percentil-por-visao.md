# ADR-007: SCORE é percentil da visão filtrada; Focar = top 20%

- **Data**: 2026-10-08
- **Status**: Accepted
- **Deciders**: João Luiz
- **Tags**: scoring, query, product

## Contexto e Problema

PRIORIDADE (`lista × urgência`) é atributo estável do deal (ADR-001). O vendedor pergunta “onde **eu** foco esta semana”; o gestor pergunta “e o **time**?”. Um SCORE absoluto calculado na ingestão faria o mesmo deal parecer “82” no meu funil e no do escritório — o percentil mentiria ao filtrar (quebra CA7/RF11).

## Decision Drivers

- RF1 / RF11: percentil recalculado em meus deals vs. time vs. filtros.
- Focar precisa ser uma fatia da **visão atual**, não um recorte global.
- Empates e visão com N=1 têm de ser determinísticos.

## Considered Options

- **A — SCORE = percentil 0–100 de PRIORIDADE no conjunto filtrado; Focar = ceil(20% × N) dessa visão (≥1 se não vazia); cálculo na camada de query**
- **B — SCORE global na ingestão, filtros só escondem linhas**
- **C — SCORE = PRIORIDADE bruta (dólares), sem percentil**

## Por quê

| | Opção | Por quê (resumido) |
|---|--------|-------------------|
| **Tomada** | A — percentil da visão; Focar = top 20% local | “Onde **eu** foco” ≠ percentil do escritório. CA7 exige recálculo no filtro; Focar vazio em carteira pequena é inútil. |
| **Não tomada** | B — SCORE global na ingestão | Número estável, mas o filtro só esconde linhas: o 82 continua 82 e mente. |
| **Não tomada** | C — mostrar dólares crus | Transparente, mas GTK 500 sempre no topo visual; o vendedor não vê posição na **sua** fila. |

## Decision Outcome

Opção escolhida: **"A"**. Empates compartilham o percentil; N=1 → SCORE 100 e ESTADO Focar. A ingestão materializa PRIORIDADE; a query materializa SCORE e ESTADO.

### Consequências Positivas

- Trocar o filtro muda o SCORE do mesmo deal — comportamento correto.
- Focar nunca fica vazio numa carteira pequena.
- Testável com duas requests (`/api/queue`) na mesma oportunidade.

### Consequências Negativas

- Não dá para gravar o SCORE no CSV de ingestão; export tem de sair da visão (CA9).
- Comparar SCORE entre vendedores sem declarar a visão é inválido — o rollup do gestor usa contagem/valor/esfriando, não o percentil cruzado.

## Pros and Cons of the Options

### A ✅ Escolhida

- ✅ Honra CA7; Focar acionável por carteira
- ❌ SCORE não é comparável entre visões

### B — Percentil global

- ✅ Um número estável
- ❌ Filtro mente; top 20% global esvazia carteiras pequenas

### C — Dólares crus na UI

- ✅ Transparente
- ❌ GTK 500 sempre “ganha” visualmente; o vendedor não vê posição relativa

## Links

- PRD RF11, CA7; spec assumptions (fórmula do percentil e ceil)
- [ADR-001](001-priorizar-por-valor-em-risco.md), [ADR-003](003-idade-nao-exclui-da-fila.md)

## Nota posterior (2026-10-11)

SCORE e Focar calculam-se só em **Trabalhar** da visão. Decidir não entra no percentil ([ADR-015](015-fila-decidir-alem-da-parede.md)). PRIORIDADE passou a `lista × CHANCE` ([ADR-014](014-chance-por-idade-com-censura.md)). O rollup do gestor usa Trabalhar vs Decidir e o **valor parado**, não o percentil cruzado.
