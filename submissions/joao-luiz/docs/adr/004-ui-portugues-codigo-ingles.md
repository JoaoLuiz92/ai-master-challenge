# ADR-004: UI em português; código e API em inglês

- **Data**: 2026-10-08
- **Status**: Accepted
- **Deciders**: João Luiz
- **Tags**: i18n, api, frontend

## Contexto e Problema

O usuário primário é vendedor/gestor brasileiro não-técnico (motivo e ação na fila). Quem mantém o código é outro dev, e o challenge cobra clareza de implementação. Misturar PT em identificadores e EN na tela (ou o contrário) quebra um dos dois.

## Decision Drivers

- RNF3: UI em português.
- RNF5: código limpo o suficiente para outro dev manter.
- Score e contratos HTTP precisam ser testáveis com nomes estáveis.

## Considered Options

- **A — Rótulos/copy da UI em PT; identificadores, código e JSON da API em inglês**
- **B — Tudo em português (API inclusa)**
- **C — Tudo em inglês (UI inclusa)**

## Por quê

| | Opção | Por quê |
|---|--------|-------------------|
| **Tomada** | A — UI PT / código e API EN | Vendedor não-técnico lê motivo/ação; outro dev e os testes precisam de identificadores estáveis. |
| **Não tomada** | B — tudo PT (API inclusa) | Uma língua, mas rotas e campos instáveis — pior de manter e de testar. |
| **Não tomada** | C — tudo EN (UI inclusa) | Código limpo; a tela fala “cooling” / “focus” para quem a ferramenta serve. |

## Decision Outcome

Opção escolhida: **"A"**. Tradução só na borda da UI (`DealCard`, badges, empty states). Campos da API: `score`, `estado` como valor de domínio já em PT (`Focar` / `Acompanhar` / `Revisar`) porque são copy de produto, não nomes de coluna.

### Consequências Positivas

- Vendedor lê “Esfriando” / “Avançar proposta” sem jargão.
- Testes de API e pytest ficam em inglês.

### Consequências Negativas

- Camada de rótulos para manter; risco de vazar chave técnica na tela se um componente renderizar o JSON cru.

## Pros and Cons of the Options

### A ✅ Escolhida

- ✅ Atende usuário e mantenedor
- ❌ Dois idiomas no repo

### B — Tudo PT

- ✅ Uma língua
- ❌ Identificadores e rotas instáveis; pior para outro dev

### C — Tudo EN

- ✅ Código uniforme
- ❌ Vendedor não-técnico lê “cooling” / “focus”

## Links

- PRD RNF3, RNF5; RF3
- [ADR-002](002-fastapi-react-em-memoria.md)
