# ADR-001: Priorizar o funil por valor em risco (lista × urgência), não por probabilidade de conversão

- **Data**: 2026-10-08
- **Status**: Superseded by [ADR-014](014-chance-por-idade-com-censura.md)
- **Deciders**: João Luiz (AI Master candidate), apoiado por análise exploratória (`docs/analise-exploratoria.md`)
- **Tags**: scoring, modeling, data, product

## Contexto e Problema

O challenge pede uma ferramenta que diga ao vendedor **onde focar** no pipeline aberto (~2.089 oportunidades Prospecting/Engaging). A intuição de mercado — e o baseline que uma IA gera ao receber o brief — é construir um **score de probabilidade de conversão** e ordenar por ele.

Antes de aceitar essa fórmula, medimos se os dados sustentam previsão de conversão. Resultado da EDA sobre os 6.711 negócios fechados:

- Win rate é **praticamente plano**: 60–65% em todos os produtos, setores e portes de conta.
- Modelo calibrado (logística) com **holdout temporal**: **AUC = 0,478** (pior que o acaso). `p̂` varia só de 0,57 a 0,71.
- O **valor**, ao contrário, varia **400×**: MG Special lista US$ 55, GTK 500 lista US$ 26.768.
- MG Special tem o **maior** win rate (64,8%) e **0,4%** da receita. MG Special + GTX Basic = **39,6% do esforço, 5,4% da receita**.

Ou seja: um score de conversão mandaria o time para o produto barato de alto win rate — exatamente a dor que a Head de RevOps descreveu.

## Decision Drivers

- O score precisa refletir **dinheiro em risco**, não só chance de fechar.
- Precisa ser **explicável** para um vendedor não-técnico ("por que este deal?").
- Precisa ser **reprodutível** em qualquer máquina (sem modelo frágil nem dependência externa).
- Time budget de 4–6h: regra + heurística bem apresentada > ML sem interface (dica explícita do challenge).
- Honestidade estatística: não embarcar um classificador AUC ~0,50 fingindo sinal.

## Considered Options

- **A — Prioridade = preço de lista × urgência(idade)** (determinístico, sem `p̂`)
- **B — Valor esperado = probabilidade calibrada × valor × urgência** (modelo no centro, valor blinda a armadilha)
- **C — Probabilidade de conversão pura** como eixo de ordenação

## Por quê

| | Opção | Por quê |
|---|--------|-------------------|
| **Tomada** | A — lista × urgência | Valor varia 400× e é o que muda a fila; `p̂` não tem sinal (AUC 0,478) nem reordena (Spearman 0,999). Urgência sim (overlap top-20 vs. só valor = 7/20). Lista é proxy honesto (close/lista ≈ 1,0). |
| **Não tomada** | B — `p̂` × valor × urgência | Mesma fila da A com ruído, mais bug e menos reprodutibilidade. |
| **Não tomada** | C — só probabilidade | Win rate plano; mandaria o time para MG Special (maior win rate, 0,4% da receita) — a armadilha da Head. |

## Decision Outcome

Opção escolhida: **"A — preço de lista × urgência(idade)"**, porque a EDA provou que `p̂` não tem sinal (AUC 0,478) e não altera a fila: a correlação de Spearman entre `p̂ × valor × urgência` e `valor × urgência` é **0,999** (19 dos top-20 idênticos). A probabilidade é enfeite caro; a **urgência**, sim, reordena (overlap com "só valor" cai para 7/20). Mantemos o valor como preço de lista do catálogo (o `close_value` só existe depois de fechar; a razão close/lista é ~1,0, então lista é proxy honesto).

### Consequências Positivas

- Fila ordenada por **retorno por hora de vendedor**, não por chance de um ticket de US$ 55.
- 100% **determinística e auditável**: roda offline; `docker compose up` reproduz a mesma fila.
- Explicação trivial em português ("GTX Pro · US$ 4.821 · 40 dias · esfriando").
- Evita o erro central que reprovaria a entrega (premiar MG Special).

### Consequências Negativas

- Abrimos mão de "predizer quem fecha" — mas os dados não sustentam isso de qualquer forma.
- Depende de **urgência** bem calibrada (curva de idade vs. ciclo de Won); se a curva estiver ruim, a fila perde qualidade.
- Quem olhar só o ranking pode achar "simples demais" sem ler a justificativa estatística — por isso o `p̂` e seu AUC ficam documentados no process log como tentativa descartada, não escondida.

## Pros and Cons of the Options

### A — Lista × urgência ✅ Escolhida

- ✅ Determinístico, reprodutível, explicável
- ✅ Alinhado ao achado de negócio (valor >> probabilidade)
- ✅ Cabe no time budget
- ❌ Não entrega "machine learning" visível (mitigado: `p̂` documentado como experimento)

### B — Valor esperado com `p̂` calibrado

- ✅ Parece mais sofisticado; mantém porta aberta para sinal futuro
- ❌ `p̂` mede AUC 0,478 → multiplicar por ele adiciona ruído, não informação
- ❌ Spearman 0,999 vs. opção A: mesma fila, mais superfície de bug e menos reprodutibilidade

### C — Probabilidade de conversão pura

- ✅ É o que a maioria faz (familiar)
- ❌ Ordena o time para o produto barato de alto win rate — a armadilha descrita pela Head
- ❌ AUC ~0,50: ranking sem fundamento

## Links

- Índice do ciclo: [README](README.md)
- Baseia-se em: `docs/analise-exploratoria.md` (EDA 2026-10-08, holdout temporal e Spearman)
- Irmãs (mesmo dia, outras decisões): [002](002-fastapi-react-em-memoria.md) stack · [003](003-idade-nao-exclui-da-fila.md) idade/Revisar · [004](004-ui-portugues-codigo-ingles.md) idioma · [005](005-ancora-temporal-2017-12-31.md) âncora · [006](006-sem-llm-no-caminho-critico.md) sem LLM no score · [007](007-score-percentil-por-visao.md) percentil por visão
- Challenge: `challenges/build-003-lead-scorer/README.md`
