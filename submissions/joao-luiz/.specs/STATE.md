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

### AD-008
- **Decision**: Duas estações endereçáveis — path `/vendedor` e `/gestor`, recorte na query, trilho à esquerda troca o papel; `/` redireciona para `/vendedor?agente=Anna+Snelling`. Papel não é filtro.
- **Reason**: O `<select>` Visão misturava identidade e recorte; sem login a visão tem de sobreviver ao F5 (SCORE é da visão, ADR-007). Ver `docs/adr/008-duas-estacoes-enderecaveis.md`.
- **Trade-off**: O front passa a ter router; nomes do CSV na query.
- **Scope**: Chrome da UI (feature `foco-ui`). Motor intocado.
- **Date**: 2026-10-09
- **Status**: active

### AD-009
- **Decision**: Focar é o herói (faixa aberta); Acompanhar e Revisar colapsam com a conta no título; três densidades de linha; empty ensina o próximo gesto.
- **Reason**: O job são os ~8 da semana; lista única de cards iguais esconde o top 20% (ADR-007). Ver `docs/adr/009-focar-como-heroi-da-atencao.md`.
- **Trade-off**: LEAD-04/18 deixam de exigir a fila inteira expandida na primeira pintura; testes precisam do estado aberto/fechado.
- **Scope**: Estação vendedor e drill do gestor (`foco-ui`).
- **Date**: 2026-10-09
- **Status**: active

### AD-010
- **Decision**: Hierarquia do card: ação → motivo → valor/idade → Estado/Esfriando; SCORE e Confiança no canto (tooltip “posição nesta visão, 0–100”, sem a palavra percentil); estágio omitido na fila trabalhável; Revisar explica a sujeira; PRIORIDADE não aparece no card.
- **Reason**: SCORE grande + `Engaging` em inglês são jargão; dois US$ (lista e PRIORIDADE) confundem. Ver `docs/adr/010-hierarquia-do-card-score-rebaixado.md`.
- **Trade-off**: RF2/LEAD-04: estágio e SCORE continuam no payload/CSV; o chrome não os trata como herói.
- **Scope**: DealCard / Revisar / copy (`foco-ui`).
- **Date**: 2026-10-09
- **Status**: active

### AD-011
- **Decision**: Faixa de situação só com números do payload; gestor home = rollup (gente); drill `?agente=` substitui o herói pela fila; export só onde há deals na tela; KPI clicável só Focar/Revisar; chrome “Visão em 31/12/2017”.
- **Reason**: Sem endpoint novo, sem verbo de aprovação; export fantasma fura CA9. Ver `docs/adr/011-faixa-de-situacao-export-drill.md`.
- **Trade-off**: Home do gestor não exporta; Esfriando é derivado no cliente (`age_days > 106`).
- **Scope**: KPIs, rollup, export, drill (`foco-ui`).
- **Date**: 2026-10-09
- **Status**: active

### AD-012
- **Decision**: Tom visual de mesa operacional — claro, denso, faixa como texto+número, sem vidro/gradiente/ícone-por-KPI, sem clonar a print de aprovação.
- **Reason**: Organizado ≠ dashboard de pitch; a print é outro produto. Ver `docs/adr/012-tom-visual-mesa-operacional.md`.
- **Trade-off**: `index.css` vira trabalho desta feature, não um reskin de cor.
- **Scope**: Visual da UI (`foco-ui`).
- **Date**: 2026-10-09
- **Status**: active

### AD-013
- **Decision**: O gestor passa um deal da fila trabalhável para um colega do mesmo escritório **só em memória**. Reiniciar a API devolve os donos dos CSVs. Sem `handoffs.jsonl`, sem banco. Os quatro CSVs de origem não são escritos.
- **Reason**: “Não perder o deal” é o negócio continuar um só na tela (mesmo `opportunity_id`, sai de um e entra no outro). Gravar overlay ou banco contradiz AD-002, quebra a reprodução do snapshot e infla o desafio. Ver `docs/adr/013-repasse-so-na-sessao.md`.
- **Trade-off**: Quem mata o processo perde o repasse; está escrito no README como limitação, não como bug.
- **Scope**: Feature `repassar-deal`. Não altera o motor (AD-001..007). AD-002 permanece active.
- **Date**: 2026-10-09
- **Status**: active

## Handoff

- **Feature**: `chance-por-idade`
- **Phase / Task**: Execute C7 feito. **Agora:** C8 (frases PT).
- **Completed**: C1–C7. Features anteriores Execute + faixa PASS. PR #182 aberto.
- **In-progress** (file:line): none.
- **Next step**: C8 — `explain.py` chance/parede. Ver `.specs/NEXT-ACTION.md`.
- **Blockers**: WDAC no host bloqueia `pandas._libs.internals`. Pytest sobe na imagem `solution-api` com `backend/` montado. Pin FastAPI 0.112.4 + Pydantic 1.10.22.
- **Uncommitted files**: none after this commit.
- **Branch**: submission/joao-luiz
