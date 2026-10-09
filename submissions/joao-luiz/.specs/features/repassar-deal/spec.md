# Repassar deal — o gestor passa o negócio sem perdê-lo (`repassar-deal`) Specification

## Problem Statement

O gestor já vê, no drill, um negócio bom esfriando na carteira de alguém. Hoje ele não consegue passar esse negócio para um colega: o deal continua parado, ou uma transferência mal feita o apaga ou duplica. Esta feature deixa o gestor escolher o colega e mover **aquele** `opportunity_id` na sessão. O negócio continua um só, na fila de quem recebeu. Reiniciar a API devolve os donos do CSV (ADR-013) — não é perda na tela; é o snapshot reproduzível do desafio.

## Goals

- [ ] No drill do gestor, um deal da fila trabalhável passa para um colega do mesmo escritório em uma confirmação.
- [ ] O `opportunity_id` continua existindo uma única vez: sai da fila de origem e entra na fila de destino, com o mesmo produto, conta, valor de lista e idade.
- [ ] Recusa ou cancelamento deixam o dono original intacto.
- [ ] Reiniciar o processo recarrega os donos dos CSVs. Os CSVs de origem não são alterados.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
| ------- | ------ |
| Overlay `handoffs.jsonl`, banco ou qualquer dono gravado em disco | ADR-013 / AD-002: o snapshot tem de ser o mesmo a cada startup. Persistência é CRM, não este teste. |
| Sugestão automática de colega, fit ou ranking de redistribuição | O gestor escolhe. A ferramenta não indica "passa para fulano". |
| Repasse em lote | Um negócio por confirmação. Lote esconde qual deal sumiu se algo falhar. |
| Repasse feito pelo vendedor | Só a estação gestor, no drill. O vendedor não move a própria carteira. |
| Repasse entre escritórios | Colega de outro escritório sai da prestação de contas do gestor. |
| Repasse de Revisar, Won, Lost ou Prospecting | Revisar é dado ruim; fechado e prospecção não são a fila que se salva. |
| Mudança na fórmula de PRIORIDADE, urgência ou percentil | O motor (AD-001..007) só recalcula o SCORE na visão de destino, como já faz ao filtrar. |
| Login / SSO | AD-002. A trava é a regra do repasse, não um usuário logado. |
| Alterar os CSVs de origem | O snapshot continua reproduzível. |
| Notificação (e-mail, Slack) | Fora do job. O rastro fica na própria fila, na sessão. |

---

## Assumptions & Open Questions

Every ambiguity is resolved or recorded here - nothing is left silently unclear.

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| Quem recebe | Qualquer `sales_agent` do mesmo `regional_office` do deal, inclusive carteira vazia, exceto o dono atual | Capacidade ociosa é colega válido. Outro escritório quebra a conta do gestor. | y |
| O que pode ser repassado | Só item de Focar ou Acompanhar no drill (Engaging, com conta e com `engage_date`) | É a fila trabalhável. Revisar não vira "salvo" ao trocar de nome. | y |
| O que muda no deal | `sales_agent`; `manager` e `regional_office` passam a ser os da linha desse colega em `sales_teams` | Se o gestor/escritório ficarem do dono antigo, o deal some do rollup de quem recebeu. | y |
| O que não muda | `opportunity_id`, produto, conta, valor de lista, datas, idade, PRIORIDADE | "Não perder" é o mesmo negócio, não um clone com outro número. | y |
| SCORE depois do repasse | Recalculado como percentil da visão de destino (ADR-007) | O deal entra na fila de quem recebeu na posição dessa visão. | y |
| Durabilidade | Só memória. Restart = donos do CSV. Sem `handoffs.jsonl`, sem banco. | AD-002 + ADR-013. Gravá-lo desmentiria o teste e o snapshot. | y |
| Falha | Recusa de regra (alvo inválido) não muda o dono. Não há gravação em disco para falhar. | Sem overlay, o único erro é a regra. | y |
| Concorrência | Um processo. A chave é `opportunity_id`. Segundo clique no mesmo dono: "já está com essa pessoa". | Demo local, sem fila de workers. | y |
| Auth e limite de taxa | Sem SSO. A API recusa alvo inválido e deal fora da fila; o botão só existe no drill do gestor. Sem rate limit. | AD-002. | y |
| Rastro | `from_agent` no deal em memória. O card mostra "Veio de {from_agent}". Some no restart. | Sem isso o negócio parece novo. Sem arquivo. | y |
| Copy de recusa | "Colega não encontrado"; "Este negócio já está com essa pessoa"; "Colega de outro escritório"; "Este negócio não está na fila trabalhável" | Texto fixo, assertável. | y |
| Deal esfriando | Se `age_days > 106`, o diálogo de confirmação inclui "Este negócio está esfriando." | É o risco que motivou o repasse. O botão não fica restrito a esse badge. | y |
| Observabilidade além do rastro na sessão | N/A — sem métricas nem tracing | O "Veio de" na sessão é o rastro. | y |

**Open questions:** none - all resolved or logged above (required before the spec is confirmed).

---

## User Stories

### P1: Passar um negócio para um colega do mesmo escritório ⭐ MVP

**User Story**: As a gestor, I want escolher um colega e passar um deal da fila dele, so that o negócio continue existindo na carteira de quem pode trabalhar, em vez de esfriar parado.

**Why P1**: Sem o movimento, o rollup só mostra o risco. O gestor não consegue agir.

**Acceptance Criteria** (each line is one EARS pattern):

1. WHEN a user on `/gestor` with an `agente` drill activates "Passar para colega" on a Focar or Acompanhar deal THEN the system SHALL list `sales_agent` names that share that deal's `regional_office` and SHALL omit the current owner.  <!-- event-driven -->
2. WHEN the user confirms one listed colleague THEN the system SHALL assign that `opportunity_id` to the colleague and SHALL keep exactly one deal with that `opportunity_id`.  <!-- event-driven -->
3. WHEN the assignment succeeds THEN the system SHALL remove the deal from the previous agent's queue and SHALL show it on the colleague's queue with the same `opportunity_id`, product, account, list value, and `age_days`.  <!-- event-driven -->
4. WHEN the assignment succeeds THEN the system SHALL set `manager` and `regional_office` from that colleague's `sales_teams` row.  <!-- event-driven -->
5. WHEN the assignment succeeds THEN the system SHALL keep catalog list value and age unchanged and SHALL recompute SCORE as the percentile of the destination view.  <!-- event-driven -->
6. The system SHALL keep the total number of deals unchanged across a handoff.  <!-- ubiquitous -->
7. WHEN the user cancels the colleague list THEN the system SHALL leave `sales_agent` unchanged.  <!-- event-driven -->
8. The system SHALL show "Passar para colega" only on the gestor drill for Focar and Acompanhar deals, and SHALL NOT show it on the vendedor station or on Revisar items.  <!-- ubiquitous -->
9. WHILE the confirm dialog is open for a deal with `age_days > 106` the system SHALL include the text "Este negócio está esfriando."  <!-- state-driven -->

**Independent Test**: No drill de um vendedor, passar um deal de Focar para um colega do mesmo escritório; o id some da fila de origem, aparece na fila do colega com o mesmo produto, conta, valor e idade; a contagem global de deals não muda. Cancelar deixa o dono igual.

---

### P1: Recusa não apaga o negócio ⭐ MVP

**User Story**: As a gestor, I want que um alvo inválido não mova o deal, so that eu não perca o negócio ao errar o colega.

**Why P1**: "Não perder" falha se o erro deixar o deal sem dono.

**Acceptance Criteria**:

1. IF the target agent is unknown THEN the system SHALL reject the assignment, keep the original `sales_agent`, and show "Colega não encontrado".  <!-- unwanted-behavior -->
2. IF the target agent is the current owner THEN the system SHALL reject the assignment, keep the original `sales_agent`, and show "Este negócio já está com essa pessoa".  <!-- unwanted-behavior -->
3. IF the target agent belongs to a different `regional_office` THEN the system SHALL reject the assignment, keep the original `sales_agent`, and show "Colega de outro escritório".  <!-- unwanted-behavior -->
4. IF the opportunity is Won, Lost, Prospecting, or has no account or no `engage_date` THEN the system SHALL reject the assignment, keep the original `sales_agent`, and show "Este negócio não está na fila trabalhável".  <!-- unwanted-behavior -->
5. The system SHALL NOT modify `accounts.csv`, `products.csv`, `sales_teams.csv`, or `sales_pipeline.csv`.  <!-- ubiquitous -->

**Independent Test**: Pedir repasse para agente inexistente, para o próprio dono, para outro escritório e para um deal de Revisar; em todos, o dono original permanece e a mensagem é a da spec.

---

### P1: Restart devolve o snapshot ⭐ MVP

**User Story**: As a avaliador, I want that restarting the API restores CSV owners, so that the public snapshot stays reproducible and the limitation is honest.

**Why P1**: Sem isso, ou o restart “perde” o deal em silêncio, ou alguém grava overlay e desmente a AD-002.

**Acceptance Criteria**:

1. WHEN the API process starts THEN the system SHALL own every deal as in the source CSVs.  <!-- event-driven -->
2. WHEN the same `opportunity_id` is passed to a second colleague in the same process THEN the system SHALL still store exactly one deal with that id.  <!-- event-driven -->
3. The system SHALL NOT write `handoffs.jsonl` or any other owner overlay on disk.  <!-- ubiquitous -->

**Independent Test**: Passar um deal, confirmar que a fila mudou; criar um novo processo da API e ver o dono do CSV de volta. Nenhum arquivo novo em `data/` além dos CSVs de origem.

---

### P2: Rastro na fila

**User Story**: As a gestor, I want ver de quem o negócio veio, so that a fila do colega não pareça um deal novo nem um deal desaparecido.

**Why P2**: O movimento já está seguro no P1. O rastro evita a dúvida de quem olha a fila **nesta sessão**.

**Acceptance Criteria**:

1. WHEN a passed deal is rendered THEN the system SHALL show "Veio de {from_agent}" using the previous owner.  <!-- event-driven -->
2. The system SHALL keep `from_agent` only on the in-memory deal for the current process.  <!-- ubiquitous -->

**Independent Test**: Depois do repasse, o card na fila do colega mostra "Veio de {nome do dono anterior}". Reiniciar some o selo junto com o dono novo.

---

## Edge Cases

- IF the colleague list for that office has no other agent THEN the system SHALL show "Nenhum colega neste escritório" and SHALL NOT change `sales_agent`.
- WHEN the user confirms the same colleague twice for the same deal THEN the system SHALL still store one deal and SHALL show "Este negócio já está com essa pessoa" on the second attempt.
- WHEN a deal with `age_days` equal to 106 is confirmed THEN the system SHALL NOT include "Este negócio está esfriando." (`age_days > 106` is strict, as in the cooling rule).
- IF the current owner has no `regional_office` THEN the system SHALL reject the assignment, keep the original `sales_agent`, and show "Colega de outro escritório".

---

## Requirement Traceability

Each requirement gets a unique ID for tracking across design, tasks, and validation.

| Requirement ID | Story | Phase | Status |
| -------------- | ----- | ----- | ------ |
| REPA-01 | P1: Passar para colega | Execute | Implementing |
| REPA-02 | P1: Passar para colega | Execute | Implementing |
| REPA-03 | P1: Passar para colega | Execute | Implementing |
| REPA-04 | P1: Passar para colega | Execute | Implementing |
| REPA-05 | P1: Passar para colega | Execute | Implementing |
| REPA-06 | P1: Passar para colega | Execute | Implementing |
| REPA-07 | P1: Passar para colega | Specify | Pending |
| REPA-08 | P1: Passar para colega | Specify | Pending |
| REPA-09 | P1: Passar para colega | Specify | Pending |
| REPA-10 | P1: Recusa não apaga | Execute | Implementing |
| REPA-11 | P1: Recusa não apaga | Execute | Implementing |
| REPA-12 | P1: Recusa não apaga | Execute | Implementing |
| REPA-13 | P1: Recusa não apaga | Execute | Implementing |
| REPA-14 | P1: Recusa não apaga | Execute | Implementing |
| REPA-15 | P1: Restart = snapshot | Execute | Implementing |
| REPA-16 | P1: Restart = snapshot | Execute | Implementing |
| REPA-17 | P1: Restart = snapshot | Execute | Implementing |
| REPA-18 | P2: Rastro na fila | Execute | Implementing |
| REPA-19 | P2: Rastro na fila | Execute | Implementing |

**ID format:** `REPA-NN`.

**Status values:** Pending → In Design → In Tasks → Implementing → Verified

**Coverage:** 19 total, 16 implementing (T1–T6), 3 pending (REPA-07, REPA-08, REPA-09).

---

## Success Criteria

How we know the feature is successful:

- [ ] No drill do gestor, um deal de Focar ou Acompanhar passa para um colega do mesmo escritório e continua com o mesmo `opportunity_id`, produto, conta, valor e idade.
- [ ] A contagem global de deals não muda. O deal sai da fila de origem e entra na de destino.
- [ ] Alvo inválido ou cancelamento deixam o dono original e mostram a mensagem da spec.
- [ ] Reiniciar a API devolve os donos do CSV. Os quatro CSVs de origem ficam intactos. Nenhum overlay em disco.
- [ ] O card do destino mostra "Veio de {dono anterior}" nesta sessão.
