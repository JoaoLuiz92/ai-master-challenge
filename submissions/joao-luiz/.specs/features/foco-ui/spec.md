# Foco da Semana — Reorganização da UX (`foco-ui`) Specification

## Problem Statement

A UI atual é um documento único: um `<select>` de visão misturado a três filtros, um subtítulo que ensina estatística ("O SCORE é o percentil desta visão") e um `<ol>` de cards idênticos onde Focar e Acompanhar pesam igual e Revisar cai no fim. O vendedor não vê "os ~8 da semana"; vê scroll. O gestor recebe rollup **e** a fila do time no mesmo canvas — dois jobs, zero foco. Esta feature reorganiza a **apresentação** (não o motor) em duas estações endereçáveis, com hierarquia de atenção e vocabulário sem jargão, conforme os ADRs 008–012.

## Goals

- [ ] O vendedor abre a ferramenta e identifica os ~8 deals de Focar em segundos, com ação e motivo, sem ler uma lista de 40 cards iguais.
- [ ] Papel (vendedor/gestor) é navegação endereçável por URL; recarregar ou compartilhar o link reproduz a mesma visão e o mesmo SCORE.
- [ ] O gestor vê pessoas primeiro (rollup) e mergulha na fila de um vendedor com um clique, sem endpoint novo.
- [ ] Nenhuma dúvida silenciosa: SCORE rebaixado e explicado por tooltip, sem a palavra "percentil"; estados vazios ensinam o próximo gesto.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
| ------- | ------ |
| Qualquer mudança no motor de score, ingestão, ranking ou `p̂` | A apresentação não reabre AD-001..007; os cálculos ficam congelados. |
| Endpoint novo de API | ADR-011: KPIs e drill derivam do payload atual (`/api/queue`, `/api/rollup`, `/api/agents`, `/api/export.csv`). |
| Verbos de decisão (aprovar / delegar / recusar) | Sem persistência (ADR-002); seriam teatro. Recusados na fase de grilling. |
| Persistência de "já revisei" / histórico / login | Fora do v1 (AD-002); o durável continua o CSV. |
| Busca global, filtro "Sinal", sidebar de modelo de score | Pertencem a outro produto (print de referência), não ao job do vendedor. |
| CSV de rollup (exportar a tabela de pessoas) | ADR-011: export é artefato da fila de deals, não de gente. |

---

## Assumptions & Open Questions

Every ambiguity is resolved or recorded here - nothing is left silently unclear. As decisões de produto foram congeladas na fase de grilling e nos ADRs 008–012 / AD-008..012; as linhas abaixo registram o que a spec assume para implementar.

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| Mecanismo de rota | Hook próprio `useViewRoute` sobre History API + `popstate` (sem dependência nova de runtime) | Duas rotas + query; `react-router` seria peso extra num app de plain-CSS/mínimas deps; mantém determinismo e build offline (AGENTS.md) | y (ADR-008 fixa path+query+trilho; a lib é discrição de design) |
| Idioma das rotas e chaves de query (`/vendedor`, `/gestor`, `?agente=`, `?gestor=`, `?escritorio=`) | Português, como os valores de domínio `Focar`/`Acompanhar` | URL é copy voltada ao usuário, não contrato de API; ADR-004 mantém JSON/identificadores em inglês | y |
| Origem dos KPIs da faixa de situação | Derivados no cliente do payload já carregado (queue: `estado`, `value`, `age_days`; rollup: somas) | ADR-011: sem endpoint novo; números já existem no payload | y |
| Limiar de "Esfriando" no cliente | `age_days > 106` (estritamente), igual ao backend | Paridade com `cooling` do motor (LEAD-19); evita divergência UI↔API | y |
| Drill do gestor | Reusa `GET /api/queue?view=mine&agent=<A>` (fila daquele vendedor, percentil da visão dele) | ADR-011: um herói por vez, sem API nova | y |
| Landing `/` | Redireciona para `/vendedor?agente=Anna+Snelling` | Já é o default não-vazio da demo (`PREFERRED_AGENT`) | y |
| Erro de export | Passa a exibir mensagem ao usuário (hoje o `fetch` lança sem tratamento) | Estado de falha não pode ser silencioso; dimensão "failure state" | y |
| Rota desconhecida | Redireciona para `/vendedor` (default) | Sem 404 próprio num SPA de duas estações | y |

**Open questions:** none - all resolved or logged above (required before the spec is confirmed).

---

## User Stories

### P1: Duas estações endereçáveis + trilho ⭐ MVP

**User Story**: As a usuário, I want que vendedor e gestor sejam lugares distintos acessíveis por URL com um trilho de papel, so that eu saiba onde estou e consiga voltar à mesma visão depois de recarregar ou compartilhar o link.

**Why P1**: Sem separar papel de filtro, a ferramenta continua um formulário único — a raiz do problema.

**Acceptance Criteria** (each line is one EARS pattern):

1. WHEN a user opens `/` THEN the system SHALL redirect to `/vendedor?agente=Anna+Snelling`.  <!-- event-driven -->
2. WHEN a user activates the "Gestor" (or "Vendedor") control in the left rail THEN the system SHALL navigate to the corresponding `/gestor` (or `/vendedor`) path.  <!-- event-driven -->
3. The system SHALL encode the role in the URL path and the slice in the query string (`agente`, `gestor`, `escritorio`).  <!-- ubiquitous -->
4. WHEN a user reloads the page or opens a URL carrying a slice query THEN the system SHALL reproduce the same view and the same SCORE for that slice.  <!-- event-driven -->
5. The system SHALL NOT render a "Visão" `<select>` control.  <!-- ubiquitous -->
6. WHILE the station is "vendedor" the system SHALL expose only the "quem sou eu" (Vendedor) selector; WHILE the station is "gestor" the system SHALL expose only the Gestor and Escritório selectors.  <!-- state-driven -->
7. IF the URL path matches no known station THEN the system SHALL redirect to `/vendedor`.  <!-- unwanted-behavior -->

**Independent Test**: Navegar para `/`, confirmar o redirect; clicar no trilho Gestor e ver a URL virar `/gestor`; recarregar `/vendedor?agente=X` e ver a mesma fila/SCORE.

---

### P1: Estação Vendedor — faixa de situação e Focar como herói ⭐ MVP

**User Story**: As a vendedor, I want uma faixa de situação e a seção Focar em destaque, com Acompanhar e Revisar recolhidas, so that eu veja o dinheiro e os deals da semana sem rolar uma lista infinita.

**Why P1**: É o job-to-be-done primário; sem hierarquia de atenção a fila continua um dump.

**Acceptance Criteria**:

1. WHEN the vendedor station loads its queue THEN the system SHALL display a situation strip with "Valor em Focar", "Nº Focar", "Esfriando" and "Revisar", each derived from the loaded payload.  <!-- event-driven -->
2. The system SHALL display the "Focar" band expanded by default.  <!-- ubiquitous -->
3. The system SHALL display the "Acompanhar" and "Revisar" bands collapsed, each showing its item count in the band title.  <!-- ubiquitous -->
4. WHEN a user activates a collapsed band title THEN the system SHALL expand that band, and WHEN activated again THEN the system SHALL collapse it.  <!-- event-driven -->
5. WHEN a user activates the "Focar" or "Revisar" KPI THEN the system SHALL scroll to or expand the matching band.  <!-- event-driven -->
6. The system SHALL NOT turn the "Esfriando" KPI into a filter or action.  <!-- ubiquitous -->
7. The system SHALL compute "Esfriando" counts using `age_days > 106` strictly.  <!-- ubiquitous -->

**Independent Test**: Abrir `/vendedor?agente=X`, ver a faixa com os quatro números, Focar aberta, Acompanhar/Revisar fechadas com contagem; clicar no título de Acompanhar e vê-la expandir.

---

### P1: Hierarquia do card — ação primeiro, SCORE rebaixado, sem estágio ⭐ MVP

**User Story**: As a vendedor, I want cada card com a ação e o motivo na frente e os números técnicos no canto, so that eu entenda o que fazer sem decifrar jargão.

**Why P1**: "Não entendo o que vejo" vem da hierarquia achatada e do SCORE/estágio crus.

**Acceptance Criteria**:

1. The system SHALL render a Focar card with this vertical order: action, reason, value/age, then Estado and Esfriando.  <!-- ubiquitous -->
2. The system SHALL render SCORE as a secondary element carrying the tooltip "posição nesta visão, 0–100" and SHALL NOT use the word "percentil" anywhere in the chrome.  <!-- ubiquitous -->
3. The system SHALL NOT display the deal stage (e.g. "Engaging") on cards in the workable queue.  <!-- ubiquitous -->
4. The system SHALL NOT display PRIORIDADE as a second monetary figure on the card; the displayed value SHALL be the catalog list price.  <!-- ubiquitous -->
5. WHILE a deal's `age_days > 106` the system SHALL display the "Esfriando" badge as a distinct, styled element.  <!-- state-driven -->
6. The system SHALL render each "Acompanhar" item as a compact row (product, account, value, action) with SCORE kept in the corner.  <!-- ubiquitous -->
7. WHEN rendering a "Revisar" item THEN the system SHALL show the reason it is parked (missing account / missing date) and the action, and SHALL NOT show a SCORE.  <!-- event-driven -->

**Independent Test**: Num card de Focar, confirmar a ordem ação→motivo→valor/idade→Estado; SCORE pequeno com tooltip, sem "Engaging", sem segunda cifra; item de Revisar sem SCORE e com o motivo de estar parado.

---

### P1: Estados vazios que ensinam o próximo gesto

**User Story**: As a usuário, I want que telas vazias me digam o que fazer, so that eu não trave num "sem deals".

**Why P1**: Empty genérico é o mesmo dump, em branco.

**Acceptance Criteria**:

1. IF the selected agent has no portfolio (`empty` flag) THEN the system SHALL show an empty state instructing the user to pick another vendedor, not a generic alert.  <!-- unwanted-behavior -->
2. IF the workable queue is empty but there are Revisar items THEN the system SHALL show an empty "Focar" state pointing to the N items in Revisar.  <!-- unwanted-behavior -->
3. IF the manager slice returns no sellers THEN the system SHALL show the empty state "nenhum vendedor neste gestor/escritório".  <!-- unwanted-behavior -->
4. IF an export request fails THEN the system SHALL surface an error message instead of failing silently.  <!-- unwanted-behavior -->

**Independent Test**: Selecionar um agente-fantasma e ver a copy que manda escolher outro; abrir um recorte de gestor sem vendedores e ver a mensagem específica.

---

### P2: Estação Gestor — rollup como herói + KPIs do time

**User Story**: As a gestor, I want ver minha equipe como uma tabela de pessoas com os KPIs do time, so that eu enxergue onde o dinheiro está esfriando sem um feed de deals.

**Why P2**: Importante para o secundário; não bloqueia o MVP do vendedor.

**Acceptance Criteria**:

1. WHEN a user enters `/gestor` without an `agente` query THEN the system SHALL display the per-agent rollup table as the hero (na fila, valor, esfriando, bons esfriando).  <!-- event-driven -->
2. WHEN the gestor home loads THEN the system SHALL display a situation strip with "Valor do time", "Na fila", "Esfriando" and "Bons esfriando", summed from the rollup.  <!-- event-driven -->
3. WHILE the gestor home shows only the rollup the system SHALL NOT render the full team queue.  <!-- state-driven -->
4. The system SHALL render the rollup table with a header cell for every column it displays (including "Bons esfriando").  <!-- ubiquitous -->

**Independent Test**: Entrar em `/gestor`, ver a tabela por vendedor com cabeçalhos alinhados e a faixa com os quatro números do time; confirmar que não há a fila completa do time na home.

---

### P2: Drill do gestor para a fila de um vendedor

**User Story**: As a gestor, I want clicar num vendedor e ver a fila dele, so that eu investigue um caso sem trocar de papel.

**Why P2**: Completa o job do gestor reusando a fila do vendedor.

**Acceptance Criteria**:

1. WHEN a user activates a seller row in the rollup THEN the system SHALL replace the hero with that seller's queue (Focar/Acompanhar/Revisar bands) and SHALL set `agente` in the `/gestor` query.  <!-- event-driven -->
2. WHILE the drill is active the system SHALL make the situation strip reflect that seller's numbers.  <!-- state-driven -->
3. WHEN a user leaves the drill THEN the system SHALL clear `agente` and show the rollup again, and SHALL NOT navigate to `/vendedor`.  <!-- event-driven -->

**Independent Test**: No rollup, clicar num vendedor; ver a fila dele com as faixas e a URL `/gestor?agente=...`; voltar e reencontrar o rollup, ainda em `/gestor`.

---

### P2: Export contextual (só onde há fila de deals)

**User Story**: As a usuário, I want o Exportar CSV apenas onde há uma fila de deals na tela, so that eu não baixe algo que não estou vendo.

**Why P2**: Export de deals invisíveis é mágica; preserva CA9 do motor.

**Acceptance Criteria**:

1. The system SHALL show "Exportar CSV" only on surfaces that display a deal queue (vendedor station; gestor station after a drill).  <!-- ubiquitous -->
2. WHILE the gestor station shows only the rollup the system SHALL NOT offer "Exportar CSV".  <!-- state-driven -->
3. WHEN a user exports THEN the CSV SHALL reflect the current view's queue with the same order and columns.  <!-- event-driven -->

**Independent Test**: Na home do gestor, não há botão de export; após o drill, o export aparece e baixa o CSV daquele vendedor.

---

### P2: Tom visual de mesa operacional + âncora temporal

**User Story**: As a usuário, I want uma interface organizada de mesa de trabalho com a âncora de data visível, so that a ferramenta pareça intuitiva e não um dashboard genérico.

**Why P2**: Organizado é hierarquia, não decoração; a âncora evita que "165 dias" pareça bug.

**Acceptance Criteria**:

1. The system SHALL display the temporal anchor "Visão em 31/12/2017" in the chrome.  <!-- ubiquitous -->
2. The system SHALL NOT use decorative gradients, glassmorphism, or one icon per KPI; the situation strip SHALL be text + number.  <!-- ubiquitous -->
3. The system SHALL keep Portuguese user-facing labels while identifiers, JSON keys and API routes stay in English (ADR-004).  <!-- ubiquitous -->

**Independent Test**: Inspecionar o chrome e ver "Visão em 31/12/2017"; a faixa é texto+número, sem ícones/gradientes; rótulos em PT.

---

## Edge Cases

- IF the `agente` query names an unknown or ghost agent THEN the system SHALL show the teaching empty state rather than an error.
- WHEN a band has zero items THEN the system SHALL show its count as 0 in the title and render no rows when expanded.
- WHEN the vendedor has a single workable deal THEN the system SHALL show it in Focar (consistent with SCORE 100 / Focar from the engine).
- IF the rollup is empty for the current manager slice THEN the system SHALL show the "nenhum vendedor" empty state and SHALL NOT offer export.
- WHEN a user navigates back/forward in the browser THEN the system SHALL update the station and slice from the URL (popstate), without a full reload.

---

## Requirement Traceability

Each requirement gets a unique ID for tracking across design, tasks, and validation.

| Requirement ID | Story | Source (ADR/CA) | Phase | Status |
| -------------- | ----- | --------------- | ----- | ------ |
| FOCO-01 | P1: Estações + trilho | ADR-008 | Execute | Implementing |
| FOCO-02 | P1: Estações + trilho | ADR-008 | Execute | Implementing |
| FOCO-03 | P1: Estações + trilho | ADR-008 | Execute | Implementing |
| FOCO-04 | P1: Estações + trilho | ADR-008, ADR-007 | Execute | Implementing |
| FOCO-05 | P1: Estações + trilho | ADR-008 | Execute | Implementing |
| FOCO-06 | P1: Estações + trilho | ADR-008 | Design | Pending |
| FOCO-07 | P1: Estações + trilho | ADR-008 | Execute | Implementing |
| FOCO-08 | P1: Vendedor Focar herói | ADR-011 | Execute | Implementing |
| FOCO-09 | P1: Vendedor Focar herói | ADR-009 | Execute | Implementing |
| FOCO-10 | P1: Vendedor Focar herói | ADR-009 | Execute | Implementing |
| FOCO-11 | P1: Vendedor Focar herói | ADR-009 | Execute | Implementing |
| FOCO-12 | P1: Vendedor Focar herói | ADR-011 | Design | Pending |
| FOCO-13 | P1: Vendedor Focar herói | ADR-011 | Design | Pending |
| FOCO-14 | P1: Hierarquia do card | ADR-009, ADR-010 | Execute | Implementing |
| FOCO-15 | P1: Hierarquia do card | ADR-010 | Execute | Implementing |
| FOCO-16 | P1: Hierarquia do card | ADR-010, ADR-003 | Execute | Implementing |
| FOCO-17 | P1: Hierarquia do card | ADR-010 | Execute | Implementing |
| FOCO-18 | P1: Hierarquia do card | ADR-010 | Execute | Implementing |
| FOCO-19 | P1: Hierarquia do card | ADR-010 | Execute | Implementing |
| FOCO-20 | P1: Estados vazios | ADR-009 | Execute | Implementing |
| FOCO-21 | P1: Estados vazios | ADR-009 | Execute | Implementing |
| FOCO-22 | P1: Estados vazios | ADR-009 | Execute | Implementing |
| FOCO-23 | P1: Estados vazios | ADR-011 (failure) | Execute | Implementing |
| FOCO-24 | P2: Gestor rollup | ADR-011 | Execute | Implementing |
| FOCO-25 | P2: Gestor rollup | ADR-011 | Execute | Implementing |
| FOCO-26 | P2: Gestor rollup | ADR-011 | Design | Pending |
| FOCO-27 | P2: Gestor rollup | ADR-011 | Execute | Implementing |
| FOCO-28 | P2: Drill do gestor | ADR-011 | Design | Pending |
| FOCO-29 | P2: Drill do gestor | ADR-011 | Design | Pending |
| FOCO-30 | P2: Drill do gestor | ADR-011, ADR-008 | Design | Pending |
| FOCO-31 | P2: Export contextual | ADR-011, CA9 | Design | Pending |
| FOCO-32 | P2: Export contextual | ADR-011 | Design | Pending |
| FOCO-33 | P2: Export contextual | ADR-011, CA9/LEAD-25 | Execute | Implementing |
| FOCO-34 | P2: Mesa operacional | ADR-011, ADR-005 | Execute | Implementing |
| FOCO-35 | P2: Mesa operacional | ADR-012 | Execute | Implementing |
| FOCO-36 | P2: Mesa operacional | ADR-004 | Execute | Implementing |

**ID format:** `[CATEGORY]-[NUMBER]` (e.g., `FOCO-01`).

**Status values:** Pending → In Design → In Tasks → Implementing → Verified

**Coverage:** 36 total, mapped to tasks in `tasks.md` once Tasks is approved.

---

## Success Criteria

How we know the feature is successful:

- [ ] Um vendedor abre `/vendedor?agente=X` e vê a faixa de situação + Focar em destaque, com Acompanhar/Revisar recolhidas — sem scroll de cards iguais.
- [ ] Recarregar ou compartilhar qualquer URL reproduz a mesma estação, recorte e SCORE.
- [ ] O card lidera por ação e motivo; SCORE fica no canto com tooltip, sem "percentil", sem "Engaging", sem segunda cifra.
- [ ] `/gestor` mostra rollup de pessoas com cabeçalhos alinhados e KPIs do time; clicar num vendedor abre a fila dele e o export aparece só aí.
- [ ] Estados vazios ensinam o próximo gesto; erro de export é visível, não silencioso.
- [ ] Nenhum endpoint novo; o motor (AD-001..007) permanece intocado.
