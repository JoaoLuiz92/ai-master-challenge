# STATE

## Decisions

### AD-001
- **Decision**: Priorizar o funil por valor em risco — PRIORIDADE = `sales_price` (lista) × urgência(idade) — e manter a probabilidade de conversão (`p̂`) fora do ranking.
- **Reason**: EDA com holdout temporal mostrou `p̂` sem sinal (AUC 0,478) e Spearman 0,999 entre a fila com e sem `p̂`; o valor varia 400× e é o que reordena junto com a urgência. Ver `docs/adr/001-priorizar-por-valor-em-risco.md` e `docs/analise-exploratoria.md`.
- **Trade-off**: Abre mão de "prever quem fecha" e de ML visível; `p̂` fica documentado como experimento descartado no process log.
- **Scope**: Motor de score e qualquer feature futura que ordene/prioritize deals.
- **Date**: 2026-10-08
- **Status**: active

### AD-002
- **Decision**: Stack FastAPI (backend) + React (frontend) com todos os dados dos CSVs carregados em memória, sem banco, sem login, sem persistência além do export CSV.
- **Reason**: Time budget de 4–6h, dataset público de demonstração, requisito de reprodutibilidade (`docker compose up`); persistência/auth não agregam ao v1. Ver `docs/adr/002-fastapi-react-em-memoria.md`.
- **Trade-off**: Nenhum estado durável server-side; "já revisei" e histórico ficam de fora; o durável é o CSV exportado.
- **Scope**: Arquitetura de toda a solução.
- **Date**: 2026-10-08
- **Status**: active

### AD-003
- **Decision**: A idade de um deal nunca o remove da fila; idade só modula a urgência e, acima de 106 dias (p90 de Won), gera o badge "Esfriando". Revisar = dado ruim (sem conta / sem engage_date).
- **Reason**: A mediana dos Engaging abertos (165d) excede o máximo histórico de Won (138d) por efeito de snapshot; excluir por idade esvaziaria 89% do funil (EDA §4). Ver `docs/adr/003-idade-nao-exclui-da-fila.md`.
- **Trade-off**: A fila contém deals muito velhos; a urgência (não a exclusão) é quem os despromove.
- **Scope**: Motor de urgência e regras de ESTADO.
- **Date**: 2026-10-08
- **Status**: active

### AD-004
- **Decision**: UI em português; código, identificadores e API em inglês.
- **Reason**: Usuário final é vendedor/gestor brasileiro não-técnico; manutenção por outro dev. Ver `docs/adr/004-ui-portugues-codigo-ingles.md`.
- **Trade-off**: Camada de rótulos/tradução na borda da UI.
- **Scope**: Frontend e contrato da API.
- **Date**: 2026-10-08
- **Status**: active

### AD-005
- **Decision**: Âncora temporal "hoje" = 2017-12-31 (máxima data observada no pipeline) para todo cálculo de idade.
- **Reason**: Usar a data real tornaria todo deal ~9 anos velho; o snapshot termina nessa data (EDA §2.3). Ver `docs/adr/005-ancora-temporal-2017-12-31.md`.
- **Trade-off**: Valor fixo em código; precisa ser ajustado se o dataset mudar.
- **Scope**: Motor de urgência e cálculo de idade.
- **Date**: 2026-10-08
- **Status**: active

### AD-006
- **Decision**: Score 100% aritmético sobre CSV; LLM fora do caminho crítico.
- **Reason**: Ranking é conta exata (alias, idade, lista × urgência, percentil); chamada externa quebraria RNF2. Ver `docs/adr/006-sem-llm-no-caminho-critico.md`.
- **Trade-off**: Motivo/ação são template, não prosa gerada.
- **Scope**: Ingestão, motor de score, textos de explain.
- **Date**: 2026-10-08
- **Status**: active

### AD-007
- **Decision**: SCORE é o percentil 0–100 de PRIORIDADE na visão filtrada; Focar = ceil(20% × N) dessa visão; cálculo na camada de query.
- **Reason**: Percentil global mentiria ao filtrar (CA7). Ver `docs/adr/007-score-percentil-por-visao.md`.
- **Trade-off**: SCORE não é comparável entre visões; export tem de sair da visão atual.
- **Scope**: ViewQueryService, API `/queue` `/export` `/rollup`.
- **Date**: 2026-10-08
- **Status**: active

## Handoff

- **Feature**: lead-scorer (`.specs/features/lead-scorer/`)
- **Phase / Task**: Execute Phase 1 / T1 concluída
- **Completed**: T1 (scaffold FastAPI + constantes congeladas)
- **In-progress** (file:line): none
- **Next step**: T2 CSV loader (`backend/app/ingestion/loader.py`). Nova janela via subagente se o contexto desta já passou de 45%. Gate T2: pytest integration nos CSVs reais. Dúvida → spec.md + design.md.
- **Blockers**: Windows WDAC bloqueia `pydantic-core` (Rust); backend pinado em FastAPI 0.112.4 + Pydantic 1.10.22. Frontend ainda não existe — metade npm do gate Build só vale a partir de T21/T26.
- **Uncommitted files**: none (após o commit da T1)
- **Branch**: submission/joao-luiz
