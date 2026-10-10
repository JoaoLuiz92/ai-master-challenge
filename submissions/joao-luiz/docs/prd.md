# PRD — Lead Scorer (Challenge 003)

- **Produto (nome de trabalho):** Foco da Semana — priorizador de pipeline para vendedores
- **Autor:** João Luiz
- **Data:** 2026-10-08
- **Status:** Aprovado para spec (entra no TLC-SPEC-DRIVEN)
- **Fontes:** `docs/analise-exploratoria.md` (EDA), `docs/adr/` (001–007), `challenges/build-003-lead-scorer/README.md`

---

## 1. Problema

35 vendedores em escritórios regionais trabalham ~8.800 oportunidades e priorizam "no feeling". Resultado (palavras da Head de RevOps): gastam tempo em deals que não fecham e deixam oportunidades boas esfriar. Não existe uma visão única de **onde focar hoje**.

## 2. Objetivo

Uma ferramenta que o vendedor abre na segunda de manhã e, em segundos, sabe **quais deals abertos trabalhar e por quê** — e que o gestor usa para ver onde o time perde dinheiro.

### Métrica de sucesso (do produto, não do challenge)
- Vendedor identifica seus ~8 deals prioritários sem ler planilha.
- Toda prioridade vem com **motivo em português** e uma **ação**.
- Gestor vê, por vendedor, quanto valor está **esfriando**.

## 3. Usuários e jobs

| Usuário | Job-to-be-done |
|---|---|
| **Vendedor** (primário) | "Quais dos meus deals abertos trabalho esta semana, e por quê?" |
| **Gestor** (secundário) | "Onde meu time está deixando deal bom esfriar? Qual o pipeline por vendedor?" |

Fora do v1: RevOps/C-level com visão macro de BI.

## 4. Escopo da solução

Aplicação **FastAPI (backend) + React (frontend)**, dados dos 5 CSVs carregados em memória, seletor de papel (vendedor / gestor), sem login e sem banco. Export CSV é o artefato durável. Setup via `docker compose up` com fallback de dois comandos locais.

## 5. Lógica de priorização (congelada pela EDA — ver ADR-001)

> **Âncora temporal "hoje" = 2017-12-31** (máxima data observada no pipeline).

```
VALOR      = preço de lista do produto (catálogo), após normalizar nome do produto
URGÊNCIA   = curva(idade do deal vs. ciclo de Won):
             sobe até a mediana de Won (57 dias),
             alta até o p90 de Won (106 dias),
             decai depois (deal esfriando)
PRIORIDADE = VALOR × URGÊNCIA           (dólares, auditável)
SCORE      = percentil 0–100 de PRIORIDADE entre os deals abertos DA VISÃO ATUAL
             (meus deals / meu time)
CONFIANÇA  = min(completude, suporte)   → Alta | Média | Baixa
ESTADO     = Focar | Acompanhar | Revisar
```

**Probabilidade de conversão (`p̂`) NÃO entra no ranking.** Motivo: AUC temporal 0,478; Spearman da fila com/sem `p̂` = 0,999 (ADR-001). O experimento fica documentado no process log, não no produto.

### Regras de estado

| ESTADO | Regra | Volume aprox. |
|---|---|---|
| **Revisar** | oportunidade sem `account` (todos os 500 Prospecting + 925 Engaging sem conta) | ~1.425 |
| **Fila trabalhável** | Engaging **com** conta | ~664 |
| **Focar** | top 20% de PRIORIDADE **na visão atual** | — |
| **Acompanhar** | resto da fila | — |
| Badge **Esfriando** | idade > 106 dias (p90 Won) — **não remove** da fila, só sinaliza | maioria da fila |

**Restrição crítica (ADR / EDA):** **não excluir** deal da fila por idade > ciclo de Won. A mediana dos Engaging abertos (165d) é maior que o **máximo** histórico de Won (138d) por efeito de snapshot; excluir por idade esvaziaria 89% do funil. Idade só modula urgência e gera o badge.

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
| 500 Prospecting sem `engage_date` | idade indefinida → Revisar | não chutar urgência |
| 5 agentes sem deals | empty state no seletor | não listar como carteira real |

## 7. Requisitos funcionais

### Vendedor
- RF1: selecionar seu nome e ver **sua** fila ordenada por SCORE (desc).
- RF2: ver, por deal: produto, conta, valor estimado (lista), estágio, dias no funil, SCORE, ESTADO, CONFIANÇA.
- RF3: ver **motivo** em linguagem de negócio (ex.: "GTX Pro · US$ 4.821 · 40 dias no funil · dentro do ciclo") e **ação** sugerida.
- RF4: badge "Esfriando" quando idade > 106d.
- RF5: seção Revisar separada da fila trabalhável.
- RF6: exportar a visão atual em CSV.

### Gestor
- RF7: alternar para visão de gestor (seletor de papel).
- RF8: rollup do time — pipeline por vendedor (nº de deals na fila, valor esperado somado, nº esfriando).
- RF9: destaque "deals bons esfriando por vendedor" (alto SCORE + badge Esfriando).

### Transversais
- RF10: filtro por vendedor / manager / escritório regional.
- RF11: SCORE é percentil **recalculado na visão filtrada** (meus deals vs. time).

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
| Curva de urgência mal calibrada | parâmetros (57/106d) saem da EDA, documentados e ajustáveis em código |
| `.gitignore` da raiz ignora `submissions/` e `datasets/` | commit com `git add -f`; dados copiados para `solution/data/` |
| Fila esvaziar | regra explícita: idade nunca exclui, só modula |

## 11. Critérios de aceite (alto nível — a spec TLC detalha em EARS)

- CA1: a fila do vendedor contém **apenas** Engaging com conta; nenhum Won/Lost/Prospecting aparece como trabalhável.
- CA2: ordenar por SCORE desc coloca maior `valor × urgência` no topo da visão.
- CA3: todo item da fila exibe motivo + ação + ESTADO + CONFIANÇA.
- CA4: deal sem conta aparece em Revisar, nunca na fila ordenada.
- CA5: nenhum deal é removido por idade; idade > 106d apenas recebe badge "Esfriando".
- CA6: `GTXPro` é tratado como `GTX Pro` (0 deals sem preço após ingestão).
- CA7: trocar filtro (meus deals ↔ time) recalcula o percentil do SCORE.
- CA8: `docker compose up` sobe API + front e a UI lista deals reais dos CSVs.
- CA9: export CSV reflete exatamente a visão filtrada.

## 12. Próximo passo

TLC-SPEC-DRIVEN em `submissions/joao-luiz/.specs/`: Specify (EARS a partir dos CA acima) → Design (arquitetura API/React, módulos de ingestão/score/visão) → Tasks (quebra atômica). Rodado por subagente Opus 4.8.
