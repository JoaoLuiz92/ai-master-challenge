# ADRs — Foco da Semana

Decisões **deste** ciclo, na ordem em que foram fechadas (EDA → ranking → produto → spec). Fonte: números em `docs/analise-exploratoria.md` e `solution/eda.py`. Nada aqui deriva de outra submissão.

Cadeia v0 → v1 → v2 da fórmula (experimento `p̂` → lista × urgência → percentil por visão): [`docs/evolucao-do-score.md`](../evolucao-do-score.md).

Cada ADR traz **tomada** e **não tomadas** com o porquê. Resumo:

| # | Tomada | Por quê | Não tomadas | Por que não |
|---|--------|---------|-------------|-------------|
| [001](001-priorizar-por-valor-em-risco.md) | Lista × urgência, sem `p̂` | Valor varia 400×; AUC 0,478; Spearman 0,999 — `p̂` não reordena, urgência sim | B `p̂`×valor×urgência; C só conversão | B = mesma fila com ruído; C manda o time para MG Special |
| [002](002-fastapi-react-em-memoria.md) | FastAPI + React em memória | Precisa rodar e ser testável em 4–6h; durável = CSV | B Streamlit; C banco+login | B mistura score e UI; C atrasa o job da segunda |
| [003](003-idade-nao-exclui-da-fila.md) | Idade só badge/urgência; Revisar = dado ruim | Excluir por idade tira 89% (mediana Engaging 165d > máx Won 138d) | B cutoff de idade; C chutar Prospecting | B esvazia a ferramenta; C inventa urgência sem data |
| [004](004-ui-portugues-codigo-ingles.md) | UI PT / código e API EN | Vendedor lê PT; outro dev mantém EN | B tudo PT; C tudo EN | B rotas instáveis; C vendedor lê “cooling” |
| [005](005-ancora-temporal-2017-12-31.md) | `TODAY = 2017-12-31` | Snapshot acaba em 2017; data real zera a fila | B `date.today()`; C último evento da linha | B idade ~9 anos; C aberto ficaria com idade 0 |
| [006](006-sem-llm-no-caminho-critico.md) | Template + aritmética; LLM fora | RNF2 / CA3; o CSV já explica o deal | B LLM no score; C LLM só na copy | B não reproduz; C prosa muda a cada run |
| [007](007-score-percentil-por-visao.md) | Percentil da visão; Focar = top 20% | SCORE global mente ao filtrar (CA7) | B percentil na ingestão; C dólares crus | B filtro mentiroso; C GTK 500 sempre “ganha” na tela |
| [008](008-duas-estacoes-enderecaveis.md) | Path = papel (`/vendedor`, `/gestor`); query = recorte | Sem login, a visão tem de sobreviver ao F5 | B papel como filtro; C um canvas só | B mistura identidade e recorte; C gestor herda chrome do vendedor |
| [009](009-focar-como-heroi-da-atencao.md) | Focar aberto; Acompanhar/Revisar colapsam | O job são os ~8 da semana, não a lista inteira | B lista única; C abas | B esconde o top 20%; C esconde o volume |
| [010](010-hierarquia-do-card-score-rebaixado.md) | Ação → motivo; SCORE no canto; sem estágio na fila | Vendedor precisa do porquê, não de glossário | B SCORE herói; C mostrar PRIORIDADE | B jargão; C dois US$ na cara |
| [011](011-faixa-de-situacao-export-drill.md) | Faixa de KPIs da visão; drill do gestor; export = fila | Gestor olha gente, vendedor olha deals | B fila+rollup no mesmo canvas; C métrica inventada | B dois jobs; C dado que o CSV não tem |
| [012](012-tom-visual-mesa-operacional.md) | Mesa operacional, não dashboard de pitch | Hierarquia > decoração | B KPI gigante; C clonar portal de aprovação | B clichê; C job diferente (persistência) |
| [013](013-repasse-so-na-sessao.md) | Repasse só na sessão; restart = donos do CSV | AD-002 + snapshot reproduzível; “não perder” é unicidade na tela, não CRM | B overlay jsonl; C banco | B persiste escondido; C fora do teste |

Detalhes de produto que não são ADR (forma da curva de urgência, textos de ação, `ceil(0,20×N)`, aliases, coluna `sales_price`, `metadata.csv` ignorado) estão congelados em `.specs/features/lead-scorer/spec.md` § Assumptions.
