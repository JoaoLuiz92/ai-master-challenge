# ADR-011: Faixa de situação, export só com fila visível, drill do gestor

- **Data**: 2026-10-09
- **Status**: Accepted
- **Deciders**: João Luiz
- **Tags**: frontend, ia, api

## Contexto e Problema

A home atual não resume a visão: o vendedor cai na lista; o gestor ganha uma tabela **e** a fila do time no mesmo canvas — dois jobs, zero foco. Uma print de portal de gerente tinha KPIs e uma fila de **aprovação**. Não copiamos os verbos (aprovar/delegar/recusar exigem persistência — ADR-002) nem métricas que não existem (“última tentativa”). Precisamos de números que o payload **já** entrega (`/api/queue`, `/api/rollup`) e de um gesto de gestor que olhe gente, não um feed.

## Decision Drivers

- Q3 da feature: re-IA sem endpoint novo e sem verbo de negócio novo.
- PRD do gestor: pipeline por vendedor **e** deals bons esfriando.
- CA9: export é a fila da visão, não uma tabela de pessoas.
- Âncora “hoje” = 2017-12-31 (ADR-005): sem isso na cara, “165 dias no funil” parece bug em 2026.

## Considered Options

- **A — Faixa derivada do payload; gestor home = rollup; clique no vendedor substitui o herói pela fila dele; export só onde há deals na tela; âncora visível; KPI só clica se for faixa**
- **B — Fila do time na home do gestor + export mesmo sem lista visível + KPIs copiados da print**
- **C — Sem faixa de situação**

## Por quê

| | Opção | Por quê |
|---|--------|-------------------|
| **Tomada** | A — números do payload + um herói por vez | Responde os dois jobs do gestor sem teatro de aprovação e sem API nova. |
| **Não tomada** | B — dump do time + export fantasma | É a home atual; exportaria o que o usuário não vê. |
| **Não tomada** | C — sem faixa | A lista volta a ser o único sinal. |

## Decision Outcome

Opção escolhida: **"A"**.

**Vendedor (e gestor depois do drill):** Valor em Focar · Nº Focar · Esfriando · Revisar. Cálculo no cliente a partir de `items` (`estado`, `value`, `age_days > 106`) e `revisar`.

**Gestor home (sem `agente` na query):** Valor do time · Na fila · Esfriando · Bons esfriando — somas do rollup.

**Drill:** `?agente=` na path `/gestor`. Some o rollup; entram as faixas da ADR-009; KPIs viram os do vendedor. Voltar limpa `agente`. Não navega para `/vendedor`.

**Export:** só na estação Vendedor e no drill do gestor. Home do gestor não exporta.

**KPI clicável:** só Focar e Revisar (abrem/rolam a faixa). Esfriando e Bons esfriando não viram filtro.

**Chrome:** texto discreto “Visão em 31/12/2017”.

### Consequências Positivas

- Situação da visão cabe em quatro números já existentes.
- Gestor gere gente; o detalhe de deals é um clique, a mesma API.

### Consequências Negativas

- Home do gestor deixa de ter export (o durável só existe depois do drill ou na estação vendedor).
- Contagens de Esfriando no cliente precisam da mesma regra `age_days > 106` do backend — teste de paridade, não um campo novo.

## Pros and Cons of the Options

### A ✅ Escolhida

- ✅ Sem API nova; um herói; CA9 honesto
- ❌ Export some da home do gestor; Esfriando é derivado no cliente

### B — Fila do time + export fantasma

- ✅ Sempre há o que exportar
- ❌ Dois heróis; CSV de deals invisíveis

### C — Sem faixa

- ✅ Menos chrome
- ❌ A pergunta “o que está acontecendo?” só se responde lendo a lista

## Links

- PRD RF6–RF9; ADR-002, ADR-005, ADR-007
- [ADR-008](008-duas-estacoes-enderecaveis.md), [ADR-009](009-focar-como-heroi-da-atencao.md)

## Nota posterior (2026-10-11)

A home do gestor ganhou o **valor parado** (soma de Decidir) como figura de limpeza acima da tabela ([ADR-015](015-fila-decidir-alem-da-parede.md)). A faixa ainda mostra Valor do time / Na fila / Esfriando / Bons esfriando. O export inclui a coluna `fila` e as três cestas (CHANCE-28).
