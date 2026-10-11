# ADR-010: Hierarquia do card — ação primeiro; SCORE rebaixado; sem estágio na fila

- **Data**: 2026-10-09
- **Status**: Accepted
- **Deciders**: João Luiz
- **Tags**: frontend, copy, explainability

## Contexto e Problema

O card atual empilha Produto, Conta, Valor, Estágio (`Engaging` em inglês), Dias, SCORE, Estado, Confiança, Motivo e Ação com o mesmo peso. O subtítulo ensina estatística (“O SCORE é o percentil desta visão”). PRIORIDADE — o número que de fato ordena — nem aparece; SCORE é percentil da visão (ADR-007), não “nota de IA”. Todo deal trabalhável é Engaging: o campo é ruído e fura ADR-004. O vendedor precisa da **ação** e do **porquê**, não de um glossário.

## Decision Drivers

- RF3: motivo em português e ação acionável.
- LEAD-04: SCORE continua **visível** (não some para o CSV/auditoria).
- RNF3 / ADR-004: nada de inglês de CRM na cara do vendedor.
- Não introduzir um segundo dinheiro (PRIORIDADE) ao lado do preço de lista — duas cifras US$ confundem mais que o percentil.

## Considered Options

- **A — Ordem no card: ação → motivo → valor/idade → Estado/Esfriando; SCORE e Confiança no canto; tooltip “posição nesta visão, 0–100” sem a palavra percentil; estágio omitido na fila trabalhável; Revisar mostra o motivo de estar parado (sem conta / sem data)**
- **B — SCORE grande e chrome que ensina percentil (status quo reforçado)**
- **C — Esconder SCORE; ou mostrar PRIORIDADE como “valor em risco”**

## Por quê

| | Opção | Por quê |
|---|--------|-------------------|
| **Tomada** | A — ação na cara, SCORE no canto | Cumpre LEAD-04 sem transformar a home em aula de estatística. |
| **Não tomada** | B — ensinar percentil | É o que deixou a ferramenta “de engenheiro”. |
| **Não tomada** | C — omitir SCORE / dois US$ | C quebra LEAD-04 ou cria a próxima dúvida (“qual valor?”). |

## Decision Outcome

Opção escolhida: **"A"**. Badge Esfriando é chrome de verdade (não um `<span>` perdido). Estágio continua no payload/CSV; some só do card trabalhável. Motivo e ação seguem templates (ADR-006), não prosa de LLM.

### Consequências Positivas

- A leitura do card é “o que eu faço” → “por quê” → fatos.
- Revisar deixa de parecer uma fila pobre: explica a sujeira.

### Consequências Negativas

- RF2 da spec do motor pedia estágio na fila; a apresentação deixa de renderizá-lo no card trabalhável (campo permanece no export).
- Quem vier procurar “percentil” na UI não encontra a palavra — o conceito vive no tooltip e nos docs.

## Pros and Cons of the Options

### A ✅ Escolhida

- ✅ Job na cara; SCORE auditável; ADR-004 honrado
- ❌ RF2/LEAD-04 precisam ser lidos com esta ADR (campo ≠ chrome)

### B — SCORE como herói

- ✅ Transparente para quem já leu a EDA
- ❌ Vendedor não-técnico lê jargão antes da ação

### C — Omitir SCORE ou mostrar PRIORIDADE

- ✅ Menos número, ou o ranking “honesto”
- ❌ Quebra LEAD-04, ou dois US$ no mesmo card

## Links

- PRD RF2–RF4; ADR-004, ADR-006, ADR-007
- [ADR-009](009-focar-como-heroi-da-atencao.md)

## Nota posterior (2026-10-11)

O motivo do card em Trabalhar é a frase de chance; em Decidir, a frase da parede + “Requalificar ou encerrar”. A hierarquia ação → motivo permanece. Badge Esfriando continua visual.
