# ADR-013: Repasse de deal vale só na sessão; sem overlay e sem banco

- **Data**: 2026-10-09
- **Status**: Accepted
- **Deciders**: João Luiz
- **Tags**: architecture, persistence, product, handoff

## Contexto e Problema

O gestor precisa passar um negócio da fila trabalhável para um colega do mesmo escritório, **na tela**, sem apagar, duplicar ou deixar o deal sem dono. “Não perder o deal” no briefing da Head é negócio esfriando com quem não trabalha — não “sumiu quando o processo reiniciou”.

A AD-002 já fechou: CSVs em memória, sem login, sem banco; o durável é o CSV exportado. Um arquivo `handoffs.jsonl` (ou um banco) salvaria o dono novo no restart, mas desmentiria essa decisão, quebraria a reprodução do snapshot e inflaria um desafio de 4–6 h com CRM.

## Decision Drivers

- O snapshot do Kaggle precisa continuar igual a cada `docker compose up`.
- Time budget e critério do challenge: ferramenta de foco, não operação de carteira em produção.
- Um `opportunity_id` continua um só **enquanto a sessão está no ar**.

## Considered Options

- **A — Repasse só em memória; restart recarrega os donos do CSV; CSVs intactos**
- **B — Overlay `handoffs.jsonl` relido no startup**
- **C — Banco + login; dono novo sobrevive de verdade**

## Por quê

| | Opção | Por quê |
|---|--------|-------------------|
| **Tomada** | A — sessão; restart = CSV | Cumpre AD-002 e RNF4. O avaliador sobe o mesmo funil toda vez. “Não perder” é unicidade na tela (mesmo id, mesma conta, sai de um e entra no outro). |
| **Não tomada** | B — jsonl durável | Parece barato; na prática é persistência escondida. Contradiz o README/ADR-002 (“nada fica gravado”). Um segundo `compose up` deixa de ser o dataset público. |
| **Não tomada** | C — banco | Fora do teste. Auth e schema não resolvem “onde focar na segunda”. |

## Decision Outcome

Opção escolhida: **"A"**. O `POST /api/handoff` troca `sales_agent` (e gestor/escritório do colega) na tupla em memória. Reiniciar a API devolve o dono do `sales_pipeline.csv`. Não existe `handoffs.jsonl`.

### Consequências Positivas

- `docker compose up` continua determinístico: mesma fila, mesmos donos.
- AD-002 permanece ativa; não há segunda verdade de “às vezes gravamos”.
- Falha de disco some do caminho: não há arquivo para corromper.

### Consequências Negativas

- Um avaliador que passa o deal e mata o container **não** vê o colega no restart. Isso é a limitação, não um bug — está no README e nesta ADR.
- O rastro “Veio de” vale só até o processo cair.

## Pros and Cons of the Options

### A ✅ Escolhida

- ✅ Snapshot reproduzível; alinhada ao desafio
- ❌ Repasse não sobrevive ao restart

### B — Overlay JSONL

- ✅ Demo sobrevive ao `compose down`
- ❌ Persistência disfarçada; CSVs deixam de ser a fonte única

### C — Banco

- ✅ Comportamento de CRM
- ❌ Fora do escopo e do time budget

## Links

- [ADR-002](002-fastapi-react-em-memoria.md); PRD §9; README § Limitações
- Spec `.specs/features/repassar-deal/spec.md`
