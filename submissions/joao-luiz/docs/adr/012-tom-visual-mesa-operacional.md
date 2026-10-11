# ADR-012: Tom visual de mesa operacional, não dashboard de pitch

- **Data**: 2026-10-09
- **Status**: Accepted
- **Deciders**: João Luiz
- **Tags**: frontend, visual, ux

## Contexto e Problema

O v1 parece um documento beige: `Segoe UI`, cards brancos iguais, badge Esfriando sem peso, rollup desalinhado. Uma print de “Gestão de carteira” é mais legível — e é outro produto (aprovação, modelo de score, filtro Sinal). Copiar KPI gigante + grid 3×N de cards iguais reproduz o clichê de dashboard e o erro que já temos (tudo com o mesmo peso). A ferramenta é mesa de segunda de manhã, não slide de RevOps.

## Decision Drivers

- Intuitivo e organizado = hierarquia, não decoração.
- Não clonar a print (job diferente; ADR-008/009 já recusaram o workflow).
- Distinguir-se de UI genérica (gradiente, vidro, ícone por métrica, dark neon).
- Densidade da ADR-009 tem de caber sem “hero metric” por card.

## Considered Options

- **A — Mesa operacional: claro, denso, tipografia com hierarquia, pouco raio, faixa de situação como texto+número (sem ícone), zero vidro/gradiente**
- **B — Aproximar a print: KPIs grandes, grid de cards iguais, badges pastel**
- **C — Dark mode + acento neon**

## Por quê

| | Opção | Por quê |
|---|--------|-------------------|
| **Tomada** | A — mesa operacional | Organiza a atenção sem fingir outro software. |
| **Não tomada** | B — clonar a print | Você pediu para não copiar; B é copiar o chrome. |
| **Não tomada** | C — dark neon | Estética de template; zero a ver com vendedor de escritório. |

## Decision Outcome

Opção escolhida: **"A"**. O trilho (ADR-008) traz identidade da app + Vendedor | Gestor — sem sidebar de “modelo de score”. Focar / Acompanhar / Revisar diferem por densidade e tipo, não por um terceiro tema. Motion só para estado (abrir faixa, trocar rota), sem bounce.

### Consequências Positivas

- A hierarquia das ADRs 009–011 tem suporte visual: o herói **parece** herói.
- Menos superfície de “AI slop” na entrega do challenge.

### Consequências Negativas

- Não há design system pronto: o CSS global atual (`index.css`) vira responsabilidade desta feature, não um reskin de cor.
- Quem esperar o visual da print vai achar “menos dashboard” — é o ponto.

## Pros and Cons of the Options

### A ✅ Escolhida

- ✅ Serve o job; não copia o produto errado
- ❌ Exige decisão de tipo/espaço, não só paleta

### B — Print

- ✅ Referência visual pronta
- ❌ Job, verbos e métricas de outro sistema

### C — Dark neon

- ✅ “Moderno”
- ❌ Ilegível como mesa de trabalho; clichê

## Links

- ADR-004 (UI em PT); [ADR-008](008-duas-estacoes-enderecaveis.md), [ADR-009](009-focar-como-heroi-da-atencao.md), [ADR-011](011-faixa-de-situacao-export-drill.md)
