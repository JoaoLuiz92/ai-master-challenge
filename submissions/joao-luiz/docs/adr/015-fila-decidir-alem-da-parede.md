# ADR-015: Deal além da parede sai de Trabalhar e entra em Decidir

- **Data**: 2026-10-11
- **Status**: Accepted
- **Deciders**: João Luiz
- **Tags**: product, scoring, estado
- **Supersedes**: [ADR-003](003-idade-nao-exclui-da-fila.md)

## Contexto e Problema

A ADR-003 vetou **excluir** o deal velho do produto: o corte esvaziaria 89% do funil (mediana Engaging 165d > máx Won 138d). Isso continua verdade — o deal não some.

O que mudou: a Head quer o vendedor **fora** desse pipeline parado. Badge Esfriando + urgência com piso deixavam o deal na fila de trabalho. A parede da ADR-014 dá um critério honesto para separar esforço de decisão.

## Decision Drivers

- Não apagar o pipeline parado (o gestor precisa vê-lo).
- Não misturar com Revisar (dado ruim continua sendo dado ruim).
- Ordenar a decisão pelo que vale mais.

## Considered Options

- **A — Três cestas: Trabalhar (idade ≤ parede), Decidir (idade > parede, preço desc), Revisar (sem conta/data)**
- **B — Manter o deal velho em Trabalhar com badge** (ADR-003)
- **C — Excluir idade > parede do produto**

## Por quê

| | Opção | Por quê |
|---|--------|-------------------|
| **Tomada** | A — Decidir separado | O vendedor trabalha o que ainda fecha; o gestor requalifica ou encerra o parado. Revisar inalterado. |
| **Não tomada** | B — só badge | A Head continua vendo esforço gasto no que não fecha. |
| **Não tomada** | C — exclusão | A ferramenta some (89%); contradiz o achado da EDA §4. |

## Decision Outcome

Opção escolhida: **A**. Na parede (idade = wall) o deal ainda é Trabalhar. Só **acima** vai para Decidir. Ação: "Requalificar ou encerrar". Esfriando permanece como pista visual, não como regra de fila.

### Consequências Positivas

- O valor parado vira a figura de limpeza do gestor (CHANCE-25/26).
- Revisar não vira arquivo morto.

### Consequências Negativas

- Muitos vendedores abrem a segunda com Trabalhar vazio e Decidir cheio — é o snapshot, não um bug.

## Links

- [ADR-003](003-idade-nao-exclui-da-fila.md) (texto original intacto), [ADR-014](014-chance-por-idade-com-censura.md)
- Spec `.specs/features/chance-por-idade/spec.md`
