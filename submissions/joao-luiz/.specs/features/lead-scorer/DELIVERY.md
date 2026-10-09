# Delivery — Lead Scorer ("Foco da Semana")

Registro do que a execução entregou. Os critérios continuam em `spec.md`. O veredito com evidência está em `validation.md`.

**Status:** Execute T1–T27 fechado. Faixa de validação PASS em 2026-10-09.

## O que subiu

Ferramenta em que o vendedor vê a fila de Engaging com conta, ordenada por percentil de preço de lista × urgência, com motivo e ação em português. O gestor vê o rollup e o destaque de bons deals esfriando. O CSV exportado é a visão filtrada, não um segundo ranking.

| Camada | Onde |
|--------|------|
| Backend | `solution/backend/` — FastAPI, quatro CSVs em memória no startup |
| Frontend | `solution/frontend/` — fila, Revisar, badge, rollup, export |
| Setup | `solution/docker-compose.yml` — UI em http://127.0.0.1:8080 |
| Durável | o CSV baixado. Nada fica gravado no servidor |

Como subir, com Docker e sem Docker: `README.md`, seção "Como rodar".

## Fórmula que rodou

`PRIORIDADE = sales_price × urgência`. SCORE é o percentil dessa prioridade na visão. `p̂` não entra. `TODAY = 2017-12-31`. Idade não tira deal da fila. Acima de 106 dias, badge Esfriando.

## Validação

Faixa independente (quem escreveu não é quem verificou):

- Backend: 68 pytest (51 unit, 7 integration, 10 e2e)
- UI no Playwright, origem http://127.0.0.1:8080: 8 cenários. Prints em `ui-evidence/`
- Verificador: 38/38 critérios, sensor 3/3 mutações mortas. Relatório: `validation.md`
- Diff coberto: `4aed364..a0f481e`
