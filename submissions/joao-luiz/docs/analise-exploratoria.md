# Análise exploratória — Challenge 003 Lead Scorer

**Data da análise:** 2026-10-08  
**Script:** `solution/eda.py`  
**Âncora temporal (“hoje”):** 2017-12-31 (máximo de `close_date` / `engage_date`)  
**Este documento congela números. A spec TLC vem depois, em cima disto — não o contrário.**

---

## Veredito em uma página

1. **Win rate quase não varia.** Produto, setor e porte da conta giram todos em ~60–65%. Um score de “chance de fechar” **não tem sinal**.
2. **Valor varia 400×.** MG Special lista US$ 55; GTK 500 lista US$ 26.768. Esforço está no barato.
3. **Plano B obrigatório.** Holdout temporal AUC = **0,478** (piso combinado: 0,55). `p̂` só anda de 0,57 a 0,71. Spearman da fila `p̂ × VALOR × URGÊNCIA` vs `VALOR × URGÊNCIA` = **0,999**. O modelo é enfeite. A fila do v1 ordena por **preço de lista × urgência**.
4. **Não excluir deal por idade.** Won nunca passou de 138 dias; a mediana dos Engaging abertos é **165 dias**. Se “mais velho que o ciclo de Won” = Revisar, sobram ~220 deals e a ferramenta esvazia — artefato do snapshot, não cadáver real.
5. **Pega-ratão de join:** `GTXPro` (1.480 linhas, 17% do pipeline) **não existe** no catálogo (`GTX Pro`). Sem alias, o preço some e o score zera.

---

## 1. Universo

| Tabela | Linhas | Chave |
|---|---|---|
| `sales_pipeline` | 8.800 | `opportunity_id` |
| `accounts` | 85 | `account` |
| `products` | 7 | `product` |
| `sales_teams` | 35 | `sales_agent` |

| Estágio | N | Interpretação |
|---|---|---|
| Won | 4.238 | treino / calibração |
| Lost | 2.473 | treino / calibração |
| Engaging | 1.589 | fila (se tiver conta) |
| Prospecting | 500 | cadastro — sem conta, sem data |
| **Abertos** | **2.089** | o que o vendedor ainda pode mexer |
| **Fechados** | **6.711** | win rate geral **63,2%** |

Receita total Won: **US$ 10.005.534**.

---

## 2. Pega-ratões de qualidade

### 2.1 Produto `GTXPro` vs `GTX Pro`

- Pipeline usa `GTXPro` (sem espaço): **1.480 linhas**.
- Catálogo só tem `GTX Pro`.
- Sem normalizar: 1.480 deals ficam **sem preço de lista** → valor esperado zero → somem da fila (incluindo GTX Pro, o produto que mais fatura).
- **Correção obrigatória:** alias `GTXPro` → `GTX Pro`. Depois do alias, `list_price` nulo = 0.

### 2.2 Conta vazia nos abertos

- `account` nulo: **1.425** linhas — **todas abertas**. Fechados têm conta 100%.
- Quebra: 500 Prospecting + 925 Engaging.
- Conta órfã (nome que não existe em `accounts`): **0**. Quando tem nome, o join funciona.

### 2.3 Datas

| Estágio | `engage_date` nulo | `close_date` nulo |
|---|---|---|
| Prospecting | 500 / 500 | 500 / 500 |
| Engaging | 0 | 1.589 / 1.589 (aberto, esperado) |
| Won / Lost | 0 | 0 |

Prospecting **não tem como calcular idade**. Confiança baixa + estado Revisar (qualificar), não chute de urgência.

**Hoje = 2017-12-31.** Usar a data real de 2026 faria todo deal ter ~9 anos.

### 2.4 Typos em `accounts`

| Cru | Normalizado | N contas |
|---|---|---|
| `technolgy` | `technology` | 12 |
| `Philipines` | `Philippines` | 1 |

Não muda win rate (setor já é plano), mas evita categoria fantasma se um dia o setor entrar em filtro.

### 2.5 Time comercial

- 35 agentes no cadastro, **5 sem nenhum deal:** Carl Lin, Carol Thompson, Elizabeth Anderson, Mei-Mei Johns, Natalya Ivanova. O seletor da UI não deve listá-los como carteira vazia “de verdade” — ou lista com empty state explícito.
- Escritórios: East 12, West 12, Central 11. Seis gestores.

### 2.6 `close_value` vs lista (Won)

Razão mediana por produto ≈ **1,00** (desvio ~10%). Preço de lista é proxy honesto do valor do aberto. Não precisamos modelar desconto.

---

## 3. A armadilha do esforço (números que mudam o score)

Fechados, por produto:

| Produto | N | Win rate | Receita Won | Esforço | Share receita | Lista |
|---|---|---|---|---|---|---|
| GTX Pro | 1.147 | 63,6% | 3.510.578 | 17,1% | **35,1%** | 4.821 |
| GTX Plus Pro | 745 | 64,3% | 2.629.651 | 11,1% | 26,3% | 5.482 |
| MG Advanced | 1.084 | 60,3% | 2.216.387 | 16,2% | 22,2% | 3.393 |
| GTX Plus Basic | 1.051 | 62,1% | 705.275 | 15,7% | 7,0% | 1.096 |
| GTX Basic | 1.436 | 63,7% | 499.263 | **21,4%** | 5,0% | 550 |
| GTK 500 | 25 | 60,0% | 400.612 | 0,4% | 4,0% | **26.768** |
| MG Special | 1.223 | **64,8%** | 43.768 | **18,2%** | **0,4%** | 55 |

**MG Special + GTX Basic = 39,6% do esforço e 5,4% da receita.**  
MG Special tem o **maior** win rate da carteira. Score de probabilidade mandaria o time exatamente para aí.

GTK 500 quase não aparece (n=25) mas paga ~US$ 16k por deal fechado — 400× um MG Special.

### Setor e porte: não preveem conversão

Win rate por setor: 61,2% (finance) a 64,8% (marketing). Esforço ≈ share de receita.  
Quartis de funcionários: 61,4–64,1%. Quartis de receita da conta: 61,3–65,9%. Nada acionável para `p̂`.

---

## 4. Tempo no funil

Won, dias `engage → close`:

| | dias |
|---|---|
| Mediana | **57** |
| p90 | **106** |
| p95 | **116** |
| máximo | **138** |

Lost: mediana 14 (muitos morrem cedo), máximo também 138 — o teto idêntico a Won é cheiro de **artefato da base**, não regra de negócio. Não usar “138 = morto” como verdade física.

Engaging abertos (n=1.589, todos com `engage_date`):

| | dias até 2017-12-31 |
|---|---|
| Mediana | **165** |
| p90 | 319 |
| máximo | 423 |

Comparado ao ciclo de Won:

- idade ≥ 106d (p90 Won): 1.434 Engaging  
- idade ≥ 116d (p95 Won): 1.400  
- idade ≥ 138d (max Won): **1.301**  

A maioria do funil “aberto” já é mais velha do que **qualquer** Won da história. Isso é snapshot (a base termina e o deal nunca recebeu `close_date`), não evidência de que 1.300 deals devam sair da ferramenta.

### Implicação para ESTADO (muda o grilling)

A regra combinada era: *Revisar = dado ruim **ou** idade >> ciclo de Won, fora da fila.*

Aplicada ao pé da letra:

- Revisar: **1.869 / 2.089** (89%)
- Fila trabalhável: **~220**

A ferramenta morre. **A EDA veta o cutoff de idade como exclusão.**

**Regra proposta para a spec (ainda não escrita):**

| ESTADO | Quem | N aprox. |
|---|---|---|
| **Revisar** | sem `account` (Prospecting inteiro + Engaging sem conta) | 1.425 |
| **Fila** | Engaging **com** conta | ~664 |
| **Focar** | top 20% de `VALOR × URGÊNCIA` **na visão** (eu / time) | — |
| **Acompanhar** | resto da fila | — |
| Badge **Esfriando** | idade > 106d (p90 Won) — **não tira da fila**, só explica | a maioria da fila |

Urgência: sobe até a mediana de Won (57d), fica alta até p90 (106d), **decai depois** — deal velho de GTK 500 ainda pode ganhar de MG Special fresco, mas perde para o mesmo produto mais novo.

### 4.1 Curva de sobrevivência e a parede (feature posterior)

A §4 veta **apagar** o deal velho do produto. A feature `chance-por-idade` não apaga: separa **Trabalhar** de **Decidir**.

- **Idade de um Won** = `close_date − engage_date` (ciclo). **Aberto** = censurado: idade `TODAY − engage_date`, desfecho não-Won.
- **CHANCE da faixa** = Won ÷ deals cuja idade cai na faixa. Sem os censurados, a chance sobe com a idade (só quem já fechou entra).
- **Parede** = maior idade de um Won na coorte (no snapshot, 138d). Não é literal no motor; deriva no load. Acima dela, CHANCE = 0.
- Faixas em config: 0–29, 30–59, 60–89, 90+.
- A maioria dos Engaging abertos no corte 2017-12-31 já passou da parede — vão para Decidir. Isso é o artefato da §4, agora com cesta própria.

Gate: `python backtest.py` (captura top‑N / 90d vs. preço, sem leakage).

---

## 5. Modelo `p̂` — holdout temporal

- Treino: `close_date` ≤ 2017-09-29 (n=4.702, win 64,2%)  
- Teste: depois (n=2.009, win 60,6%)  
- Features: produto, setor, log(employees), log(revenue da conta), tem matriz  
- Sem vendedor, sem `close_value`, sem estágio (Won/Lost **é** o rótulo)

| Modelo | AUC teste |
|---|---|
| produto + setor + porte | **0,478** |
| só produto | 0,486 |
| só setor | 0,485 |
| + vendedor (proibido no `p̂`) | 0,511 |

Piso combinado: **0,55**. **Falha.**  
`p̂` no teste: 0,57–0,71 (p10–p90: 0,61–0,67). Quase constante.

Vendedor tem spread de win rate 55%–70% (n≥30), mas o AUC continua ~0,50. Não entra no score. Pode aparecer na visão do gestor como contexto, não como ranking.

### Plano B (ativado, não hipotético)

Nos 664+ abertos com conta e preço:

- Spearman (`p̂ × VALOR × URGÊNCIA` vs `VALOR × URGÊNCIA`) = **0,999**  
- Overlap top-20: **19/20**  
- vs só VALOR (sem urgência): Spearman 0,926, overlap top-20 **7/20**

**Conclusão:** `p̂` não muda a fila. **Urgência muda** (7 dos top-20 de valor puro saem quando a idade entra). O v1 **não treina classificador**. Motor:

```
PRIORIDADE = list_price × urgência(idade)
SCORE      = percentil 0–100 dessa prioridade na visão atual
```

A probabilidade histórica (63%) pode aparecer como texto (“nesta carteira ~2 em 3 fecham”), não como fator que reordena.

---

## 6. Confiança

| Sinal | Completude | Suporte |
|---|---|---|
| Produto mapeado (após alias) | 100% | GTK 500 tem só 25 fechados — suporte baixo se um dia voltarmos a `p̂` |
| Conta | falha em 1.425 abertos | 85 contas, ok quando existe |
| Idade | falha em 500 Prospecting | ciclo de Won n=4.238, suporte alto |
| Vendedor | 100% nos deals | 5 agentes fantasma no cadastro |

`CONFIANÇA = min(completude, suporte)` no v1:

- Alta: Engaging com conta + produto mapeado  
- Baixa: sem conta e/ou sem `engage_date` → ESTADO Revisar  

GTK 500: suporte de conversão é frágil (n=15 Won), mas o **valor** não depende disso. Não rebaixamos o deal caro só porque fecha pouco.

---

## 7. O que a spec TLC deve congelar (input, não spec ainda)

| Decisão | Valor vindo da EDA |
|---|---|
| Hoje | 2017-12-31 |
| Alias produto | `GTXPro` → `GTX Pro` |
| Alias setor/país | `technolgy`, `Philipines` |
| Fila | só Engaging **com** conta |
| Revisar | `account` nulo (1.425), fora da ordenação |
| Motor de prioridade | `sales_price × urgência` — **sem `p̂`** |
| Pico de urgência | mediana Won = 57d |
| Início do decaimento | p90 Won = 106d |
| Badge Esfriando | idade > 106d |
| **Não excluir** por idade > 116/138/200 | esvazia a ferramenta |
| SCORE | percentil na visão (vendedor / time) |
| Focar | top 20% da fila da visão |
| VALOR | `sales_price` do catálogo |
| `p̂` | fora do ranking; documentar AUC 0,478 no process log |
| UI gestor | rollup + Engaging com conta e idade > 106d (“esfriando”) |

---

## 8. Como reproduzir

A partir de `submissions/joao-luiz/solution/`:

```text
.venv\Scripts\python -m pip install pandas numpy scikit-learn
.venv\Scripts\python eda.py
```

Dados: `solution/data/*.csv`.

---

## 9. O que esta EDA não responde (e não deve fingir)

- Uplift (“se o vendedor ligar, fecha?”) — não há atividade.  
- Stage histórico de um Won (era Engaging no dia 30?) — só o rótulo final.  
- Por que Lost fecha mais rápido (mediana 14d) — sem motivo de perda.  
- Qual o “hoje” verdadeiro da empresa — só o snapshot.

Próximo passo: **Specify TLC** com estes números como assumptions e critérios de aceite testáveis.
