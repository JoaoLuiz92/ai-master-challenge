# ADR-008: Duas estações endereçáveis — rotas + trilho; papel não é filtro

- **Data**: 2026-10-09
- **Status**: Accepted
- **Deciders**: João Luiz
- **Tags**: frontend, ia, routing

## Contexto e Problema

O v1 mistura vendedor e gestor num único formulário: o `<select>` **Visão** senta ao lado de Vendedor, Gestor e Escritório. Papel vira filtro. O vendedor não-técnico não sabe em que lugar está; o gestor herda chrome do vendedor. Sem login (ADR-002), “quem sou eu” some no F5. Uma print de portal de aprovação mostrou o padrão certo (papel como identidade) no produto errado — não copiamos o job; copiamos o fato de que papel não compete com recorte.

## Decision Drivers

- Vendedor é primário; gestor é estação distinta, não um modo do mesmo canvas (PRD §3).
- Sem autenticação: a visão tem de ser reproduzível por URL (SCORE é da visão — ADR-007).
- Chrome de papel precisa existir; vendedor não edita a barra de endereço.

## Considered Options

- **A — Path = papel (`/vendedor`, `/gestor`); query = recorte (`agente`, `gestor`, `escritorio`); trilho à esquerda navega entre as paths; `/` redireciona para `/vendedor?agente=Anna+Snelling`**
- **B — Status quo: um `<select>` Visão no mesmo form dos filtros**
- **C — Só rotas, sem trilho; ou path aninhada `/gestor/anna-snelling`**

## Por quê

| | Opção | Por quê |
|---|--------|-------------------|
| **Tomada** | A — path + query + trilho | Papel é onde você está; recorte é o que você olha; F5 e link reproduzem a visão. |
| **Não tomada** | B — dropdown Visão | Barato, e foi o que deixou a ferramenta ilegível. |
| **Não tomada** | C — rotas sem chrome / slug | Sem trilho o papel some; slug quebra com nomes do CSV. |

## Decision Outcome

Opção escolhida: **"A"**. Na estação Vendedor o único recorte visível é **quem sou eu**. Na estação Gestor, **Gestor** e **Escritório**; vendedor só entra como linha do rollup (ADR-011). Não há `<select>` de visão.

### Consequências Positivas

- Trocar de papel é um gesto de navegação, não um filtro a mais.
- A mesma URL devolve o mesmo SCORE (ADR-007) e o mesmo export (quando houver fila — ADR-011).

### Consequências Negativas

- O front passa a ter router (hoje é um único `App` sem rotas).
- Query com nomes do CSV (`Anna+Snelling`) é feia; é o identificador estável que já temos.

## Pros and Cons of the Options

### A ✅ Escolhida

- ✅ Identidade ≠ recorte; visão bookmarkable
- ❌ Dependência de router e de serializar filtros na URL

### B — Dropdown Visão

- ✅ Zero rota
- ❌ Papel compete com filtro; F5 perde o recorte

### C — Rotas sem chrome / slug

- ✅ URL “de produto”
- ❌ Sem trilho o vendedor não descobre o gestor; slug frágil

## Links

- PRD §3, RF7, RF10; ADR-002 (sem login), ADR-007 (SCORE da visão)
- [ADR-009](009-focar-como-heroi-da-atencao.md), [ADR-011](011-faixa-de-situacao-export-drill.md)
