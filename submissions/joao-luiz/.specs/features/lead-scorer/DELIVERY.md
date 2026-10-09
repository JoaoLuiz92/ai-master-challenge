# Delivery — Lead Scorer (“Foco da Semana”)

Criado ao fechar a spec. Contrato entre Specify e Execute / avaliador. Números e ACs não se reabrem aqui — estão em `spec.md`. Arquitetura em `design.md`. Fórmula v0→v1→v2 em `docs/evolucao-do-score.md`.

**Status da spec:** fechada (assumptions confirmadas, 33 LEAD-* mapeados).  
**Status do app:** Execute ainda não iniciado.

---

## O que entregar

Ferramenta que o vendedor abre e vê **onde focar**, com motivo e ação em português; o gestor vê valor na fila e deals bons esfriando.

| Camada | Entrega |
|--------|---------|
| Backend | FastAPI, 4 CSVs em memória uma vez no startup |
| Frontend | React: papel, filtros, fila, Revisar, badge, rollup, export |
| Setup | `docker compose up` + dois comandos locais documentados |
| Durável | CSV exportado da **visão atual** (nada persistido no servidor) |

Fora: ML no ranking, LLM no caminho crítico, login, banco, “já revisei”, redistribuir carteira.

---

## Fórmula congelada

```
VALOR      = sales_price do catálogo (após alias)
URGÊNCIA   = rampa 0–57d (0,5→1,0); platô até 106d; depois decai até piso 0,35
PRIORIDADE = VALOR × URGÊNCIA
SCORE      = percentil 0–100 de PRIORIDADE na visão filtrada
ESTADO     = Focar (ceil(0,20 × N), ≥1 se N>0) | Acompanhar | Revisar
CONFIANÇA  = min(completude, suporte)
```

`p̂` não entra. `TODAY = 2017-12-31`. Fila = Engaging **com** conta. Revisar = sem conta e/ou sem `engage_date`. Idade **nunca** remove da fila; > 106d → badge Esfriando.

---

## Papéis e explainability

**Vendedor:** fila ordenada, campos LEAD-04, motivo + ação PT, Focar/Acompanhar, Revisar separado, empty state se agente sem deals.

**Gestor:** rollup (contagem, soma VALOR, esfriando), destaque alto SCORE + Esfriando, mesmos filtros recalculam SCORE.

Cada card: **fator positivo** (valor / ciclo), **risco** (esfriando / dado incompleto), **ação** (avançar / reengajar / qualificar).

---

## Como Execute cumpre isto

1. Seguir `tasks.md` (T1–T27), um commit por tarefa, gate da tarefa antes de marcar done.
2. Dúvida de regra → `spec.md` e `design.md`, não reabrir EDA.
3. Última tarefa fechada → subagente `validation-lane` (não validar no chat).
4. Janela de contexto: ver `AGENTS.md` (limite 45%; fechar a tarefa atual; próxima em subagente).

Critérios de sucesso da spec (resumo): fila só Engaging+conta; 0 GTXPro sem preço; idade não exclui; filtro muda SCORE; export = visão; compose lista deals reais; UI em PT.

---

## Como o avaliador reproduz (quando o app existir)

A partir de `submissions/joao-luiz/solution/` — detalhe de comandos entra no README no Execute (T26/T33). Até lá, EDA:

```text
.venv\Scripts\python -m pip install -r requirements-eda.txt
.venv\Scripts\python eda.py
```
