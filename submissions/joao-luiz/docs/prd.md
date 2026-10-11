# PRD — Lead Scorer (Challenge 003)

- **Produto (nome de trabalho):** Foco da Semana — priorizador de pipeline para vendedores
- **Autor:** João Luiz
- **Data:** 2026-10-08 (motor vigente atualizado em 2026-10-11)
- **Status:** Produto no ar. O ranking v1 (lista × urgência) foi **substituído** por lista × CHANCE(idade) — ADR-014/015/016, feature `chance-por-idade`.
- **Fontes:** `docs/analise-exploratoria.md` (EDA), `docs/adr/` (001–016), `docs/evolucao-do-score.md`, `challenges/build-003-lead-scorer/README.md`

---

## 1. Problema

35 vendedores em escritórios regionais trabalham ~8.800 oportunidades e priorizam "no feeling". Resultado (palavras da Head de RevOps): gastam tempo em deals que não fecham e deixam oportunidades boas esfriar. Não existe uma visão única de **onde focar hoje**.

## 2. Objetivo

Uma ferramenta que o vendedor abre na segunda de manhã e, em segundos, sabe **quais deals abertos trabalhar e por quê** — e que o gestor usa para ver onde o time perde dinheiro.

### Métrica de sucesso (do produto, não do challenge)
- Vendedor identifica seus ~8 deals prioritários sem ler planilha.
- Toda prioridade vem com **motivo em português** e uma **ação**.
- Gestor vê, por vendedor, o **valor parado** em Decidir e o que ainda está em Trabalhar.

## 3. Usuários e jobs

| Usuário | Job-to-be-done |
|---|---|
| **Vendedor** (primário) | "Quais dos meus deals abertos trabalho esta semana, e por quê?" |
| **Gestor** (secundário) | "Onde meu time tem pipeline parado além da parede? Qual o valor em Trabalhar vs Decidir?" |

Fora do v1: RevOps/C-level com visão macro de BI.

## 4. Escopo da solução

Aplicação **FastAPI (backend) + React (frontend)**, dados dos 5 CSVs carregados em memória, seletor de papel (vendedor / gestor), sem login e sem banco. Export CSV é o artefato durável. Setup via `docker compose up` com fallback de dois comandos locais.

## 5. Lógica de priorização (vigente — ADR-014/015)

> **Âncora temporal "hoje" = 2017-12-31** (máxima data observada no pipeline).

```
VALOR      = preço de lista do produto (catálogo), após normalizar nome do produto
CHANCE     = tábua de sobrevivência por faixa de idade
             (Won ÷ deals da faixa; abertos = censurados);
             0 acima da parede (maior idade de um Won na coorte)
PRIORIDADE = VALOR × CHANCE
SCORE      = percentil 0–100 de PRIORIDADE só em Trabalhar da visão
CONFIANÇA  = min(completude, suporte)   → Alta | Média | Baixa
```

**Classificador `p̂` NÃO entra no ranking** (AUC 0,478; ADR-001). A urgência com piso (v1) saiu do caminho de ordenação.

### Regras de cesta

| Cesta / estado | Regra |
|---|---|
| **Trabalhar** | Engaging **com** conta e idade ≤ parede. Focar = top 20% de SCORE nesse conjunto; Acompanhar = resto |
| **Decidir** | Engaging **com** conta e idade **>** parede; ordem por preço desc; ação “Requalificar ou encerrar” |
| **Revisar** | sem `account` e/ou sem `engage_date` (Prospecting inteiro + Engaging sem conta) |
| Badge **Esfriando** | idade > 106 dias (p90 Won) — pista visual, **não** escolhe a cesta |

**Restrição crítica:** não **apagar** o deal do produto por idade (EDA §4: o corte esvazia 89%). Além da parede ele continua visível em Decidir. Na parede ainda é Trabalhar.

Histórico v1 (lista × urgência, idade só badge): ADR-001/003, `docs/evolucao-do-score.md`.

### Confiança

- **Completude:** produto mapeado (após alias), conta presente, datas válidas.
- **Suporte:** o produto tem volume histórico suficiente (ex.: GTK 500 tem só 25 fechados → suporte baixo, mas não rebaixa o **valor**).
- Deal sem conta e/ou sem `engage_date` → Confiança Baixa → ESTADO Revisar.

## 6. Qualidade de dados (gate obrigatório, da EDA)

A ingestão deve **normalizar e registrar** cada correção (nada some em silêncio):

| Pega-ratão | Correção | Impacto |
|---|---|---|
| `GTXPro` (1.480 linhas) ∉ catálogo `GTX Pro` | alias `GTXPro → GTX Pro` | sem isso, o produto que mais fatura fica sem preço e some |
| `technolgy` | `technology` | categoria fantasma de setor |
| `Philipines` | `Philippines` | idem localização |
| 1.425 abertos sem `account` | vão para Revisar | não entram na fila ordenada |
| 500 Prospecting sem `engage_date` | idade indefinida → Revisar | não chutar idade |
| 5 agentes sem deals | empty state no seletor | não listar como carteira real |

## 7. Requisitos funcionais

### Vendedor
- RF1: selecionar seu nome e ver **Trabalhar** ordenada por SCORE (desc), com Decidir e Revisar à parte.
- RF2: ver, por deal: produto, conta, valor estimado (lista), estágio, dias no funil, SCORE, ESTADO, CONFIANÇA.
- RF3: ver **motivo** em português (frase de chance em Trabalhar; frase da parede em Decidir) e **ação** sugerida.
- RF4: badge "Esfriando" quando idade > 106d (visual).
- RF5: seções Trabalhar, Decidir e Revisar distintas.
- RF6: exportar a visão atual em CSV, com coluna de fila (Trabalhar/Decidir/Revisar).

### Gestor
- RF7: alternar para visão de gestor (seletor de papel).
- RF8: rollup do time — por vendedor, contagem e valor em Trabalhar e em Decidir.
- RF9: destacar o **valor parado** (Decidir) como figura principal de limpeza.

### Transversais
- RF10: filtro por vendedor / manager / escritório regional.
- RF11: SCORE é percentil **recalculado em Trabalhar** da visão filtrada (meus deals vs. time).

## 8. Requisitos não-funcionais
- RNF1: rodar com `docker compose up` **e** com dois comandos locais (README).
- RNF2: determinístico — mesma entrada, mesma saída (sem chamadas externas no caminho crítico).
- RNF3: UI em português; código/API em inglês.
- RNF4: dados só em memória; nenhuma persistência.
- RNF5: código limpo o suficiente para outro dev manter (critério do challenge).

## 9. Fora de escopo (v1)

- **Probabilidade de conversão / ML no ranking** — sem sinal (ADR-001); vira experimento no process log.
- **LLM no caminho crítico** — o score é 100% aritmético sobre CSV; modelo no ranking quebraria RNF2 (ADR-006). Possível uso **futuro** só para texto não estruturado (motivo de perda, nota de reunião).
- **Redistribuição automática / fit / sugestão de colega** — o gestor escolhe; a ferramenta não ranqueia “passa para fulano”.
- **Repasse durável (arquivo ou banco)** — o gesto existe na sessão (ADR-013); restart recarrega os donos do CSV. Persistência seria CRM, não este desafio.
- **Login / SSO / RBAC** — dataset público de demonstração.
- **Persistência / banco / "já revisei"** — export CSV cobre o durável.

## 10. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Stakeholder achar o ranking "simples demais" | ADR-001 + process log mostram o `p̂` testado e descartado com números |
| Curva de chance mal calibrada | faixas e parede em `Settings`; parede derivada da coorte; backtest é o gate (ADR-016) |
| `.gitignore` da raiz ignora `submissions/` e `datasets/` | commit com `git add -f`; dados copiados para `solution/data/` |
| Fila de trabalho esvaziar | além da parede vai para Decidir, não some do produto |

## 11. Critérios de aceite (alto nível — a spec TLC detalha em EARS)

- CA1: a fila do vendedor contém **apenas** Engaging com conta; nenhum Won/Lost/Prospecting aparece como trabalhável.
- CA2: ordenar Trabalhar por SCORE desc coloca maior `valor × chance` no topo da visão.
- CA3: todo item exibe motivo + ação + ESTADO; Trabalhar traz a chance, Decidir a frase da parede.
- CA4: deal sem conta aparece em Revisar, nunca em Trabalhar nem Decidir.
- CA5: deal com idade > parede vai para Decidir, não some; badge Esfriando não escolhe a cesta.
- CA6: `GTXPro` é tratado como `GTX Pro` (0 deals sem preço após ingestão).
- CA7: trocar filtro (meus deals ↔ time) recalcula o percentil do SCORE.
- CA8: `docker compose up` sobe API + front e a UI lista deals reais dos CSVs.
- CA9: export CSV reflete a visão filtrada, com coluna de fila, na ordem da tela (Trabalhar, Decidir, Revisar).

## 12. Estado da spec

As quatro features fecharam Execute e faixa PASS. Motor vigente e filas: `.specs/features/chance-por-idade/`. Setup: `README.md`.
