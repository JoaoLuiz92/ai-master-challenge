# CONCERNS — riscos e armadilhas

A regra de uma linha mora nos guard-rails de `AGENTS.md`. O relato fica aqui.

Dívida ainda aberta entra na tabela. Armadilha já corrigida, que não pode voltar, entra na seção de baixo. Não se corrige nada neste arquivo.

## Em aberto

Nenhuma. Quando aparecer: o que é, a severidade, e onde será endereçada (`tasks.md` ou um ADR). Não inventar linha para parecer completo.

## Armadilhas

### Idade não apaga o deal do produto

A regra combinada no questionamento era: deal muito além do ciclo de Won sai para Revisar. A EDA mediu mediana Engaging = 165 dias contra máximo Won = 138. O corte **do produto** esvazia 89% do funil. É artefato de snapshot.

Não excluir. Além da parede o deal vai para **Decidir** (requalificar ou encerrar), não some e não mistura com Revisar. Badge Esfriando (>106d) é pista visual, não regra de cesta. Revisar = sem conta e/ou sem `engage_date`. Relato: ADR-015.

### `p̂` fora do ranking

O plano era um classificador com piso AUC 0,55. No holdout temporal deu 0,478. Spearman contra lista × urgência = 0,999.

`PRIORIDADE = sales_price × CHANCE(idade)` (ADR-014). `p̂` de classificador não entra no score, na ordenação nem na explainability. A urgência com piso saiu do ranking.

### Alias `GTXPro` antes do preço

1.480 linhas (o produto que mais fatura) não batem no catálogo sem alias. O app sobe, os testes de “carregou CSV” passam, e o valor some.

Aplicar `GTXPro` → `GTX Pro` (e `technolgy` / `Philipines`) antes do join de preço. Logar a correção com a contagem. Zero deals GTXPro sem preço.

### Não atualizar FastAPI nem Pydantic

Nesta máquina o WDAC bloqueia `pydantic-core` (extensão Rust). FastAPI recente puxa Pydantic v2 e o import quebra.

Manter o pin de `solution/backend/requirements.txt`: `fastapi==0.112.4`, `pydantic==1.10.22`, `starlette==0.38.6`. Warning de versão não autoriza upgrade.

### Repasse não grava disco

A primeira versão da spec gravava `handoffs.jsonl` para o restart “não perder” o dono. Isso desmente a AD-002 e deixa o snapshot diferente a cada `compose up`.

`POST /api/handoff` só `replace` na tupla em memória. Restart = donos do CSV. Nenhum overlay em `data/`. Relato: ADR-013.

### O bloco de processo fica no README

O primeiro commit da branch foi desfeito porque faltava o harness. Numa edição seguinte, o bloco do README (“Onde a IA errou” / “O que eu adicionei”) foi trocado por um ponteiro para `process-log/eda-2026-10-08.md`. Sem esses quatro títulos no README o processo do MVP fica ilegível.

Os quatro títulos do template permanecem no README (ferramentas, fluxo, onde a IA errou, o que eu acrescentei). `process-log/` é um arquivo por sessão.

## Como usar

- Ao retomar, ler a armadilha que toca o código da tarefa. Não reler o arquivo inteiro se a tarefa não passa por ali.
- Erro que chegou a código ou doc, foi corrigido, e um agente repetiria: nova armadilha aqui. Se a regra for permanente, uma linha nos guard-rails de `AGENTS.md`.
- Decisão de produto já congelada na spec não se reabre aqui.
