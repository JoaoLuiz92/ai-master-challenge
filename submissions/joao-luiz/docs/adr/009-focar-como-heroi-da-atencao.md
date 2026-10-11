# ADR-009: Focar é o herói da atenção; Acompanhar e Revisar colapsam

- **Data**: 2026-10-09
- **Status**: Accepted
- **Deciders**: João Luiz
- **Tags**: frontend, ia, ux

## Contexto e Problema

O job do vendedor é “quais ~8 deals trabalho esta semana”. A UI atual entrega um `<ol>` de cards idênticos: Focar e Acompanhar pesam igual; Revisar fica no fim da página. A spec do motor (LEAD-04 / LEAD-18) exige que a fila trabalhável e Revisar **existam** na estação — não que todas as linhas estejam expandídas na primeira pintura. Sem hierarquia, “Focar = top 20%” (ADR-007) é um rótulo, não uma decisão visível.

## Decision Drivers

- Sucesso do PRD: identificar os ~8 em segundos, com motivo e ação.
- Estados Focar / Acompanhar / Revisar são o **mesmo** job em três faixas, não três produtos (abas esconderiam o volume).
- Empty tem de ensinar o próximo gesto, não repetir `sem deals nesta visão`.

## Considered Options

- **A — Três faixas na mesma página: Focar aberta e dominante; Acompanhar e Revisar colapsadas com a conta no título; três densidades de linha; empty por caso**
- **B — Abas Focar | Acompanhar | Revisar**
- **C — Lista única, cards iguais (status quo)**

## Por quê

| | Opção | Por quê |
|---|--------|-------------------|
| **Tomada** | A — faixas + colapso + densidade | Ensina a IA (três estados, um job) e cumpre “~8 na cara”. |
| **Não tomada** | B — abas | Some o volume de Acompanhar/Revisar até clicar. |
| **Não tomada** | C — lista única | Foi o que tornou a ferramenta um dump. |

## Decision Outcome

Opção escolhida: **"A"**. Export continua a visão completa (CA9). Agente fantasma permanece no seletor (empty explícito, não omissão). Três densidades: Focar = card com ação em evidência; Acompanhar = linha compacta; Revisar = produto + motivo de estar parado + ação.

Empty por caso: fantasma → “este nome não tem carteira; escolha outro”; só Revisar → Focar vazio aponta os N em Revisar; gestor sem recorte → “nenhum vendedor neste gestor/escritório”.

### Consequências Positivas

- A home responde o job da segunda de manhã sem scroll de 40 cards iguais.
- Acompanhar e Revisar continuam na estação (um clique); a spec do motor não perde cobertura, só a primeira pintura.

### Consequências Negativas

- LEAD-04/LEAD-18 deixam de significar “lista inteira sempre expandida”. A apresentação passa a esta ADR e à spec `foco-ui`.
- Conteúdo colapsado exige teste de expansão, não só de snapshot da home.

## Pros and Cons of the Options

### A ✅ Escolhida

- ✅ Herói = Focar; estrutura do funil visível pelas contas
- ❌ Mais estados de UI para testar (aberto/fechado, empty por caso)

### B — Abas

- ✅ Tela limpa
- ❌ Esconde que existem 32 para acompanhar

### C — Lista única

- ✅ Um componente
- ❌ Não há herói; o top 20% é invisível

## Links

- PRD §2 (métrica ~8 deals); ADR-007 (Focar = top 20% da visão)
- [ADR-008](008-duas-estacoes-enderecaveis.md), [ADR-010](010-hierarquia-do-card-score-rebaixado.md)

## Nota posterior (2026-10-11)

Focar continua o herói de **Trabalhar**. **Decidir** é uma seção à parte (não colapsa com Acompanhar); não entra no top 20% ([ADR-015](015-fila-decidir-alem-da-parede.md)).
