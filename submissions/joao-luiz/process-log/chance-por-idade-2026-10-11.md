# Process log — chance-por-idade 2026-10-11

## O que rodei

Execute C1–C16 da feature `chance-por-idade` em `submissions/joao-luiz/`. Motor v3 no ar: `PRIORIDADE = sales_price × CHANCE(idade)`, cestas Trabalhar / Decidir / Revisar, rollup com valor parado.

Faixa de validação (autor ≠ verificador): 133 pytest, 4 cenários UI, 29/29 ACs, sensor 3/3. Relatório: `.specs/features/chance-por-idade/validation.md`.

Pytest no host quebra (WDAC bloqueia pandas). Gate na imagem `solution-api` com `backend/` montado.

## Onde a IA quase errou (e o dado / o teste corrigiu)

1. **Apagar o deal velho.** A EDA já vetou o corte do produto (89%). A tentação desta feature era “então tira da fila”. A regra certa: além da parede vai para **Decidir**, não some e não mistura com Revisar.
2. **Export só de Trabalhar.** CHANCE-28 pede a visão da tela. CSV sem coluna `fila` e sem Revisar falhou na faixa; o export passou a listar Trabalhar, depois Decidir, depois Revisar.
3. **Imagem Docker velha.** A UI da faixa lia um `solution-api` de ~2h atrás e negava o export novo. Rebuild da API (`docker compose up --build -d api`) antes de revalidar.
4. **Docs ainda falando urgência com piso.** README, PRD e AGENTS descreviam o motor v1 como vigente. Os ADRs 001/003 ficam com o texto original (superseded); o que o avaliador lê como regra atual aponta para ADR-014/015.

## O que o dado confirmou

A maior parte do Engaging aberto no snapshot 2017-12-31 já passou da parede (~138d). Isso é o mesmo artefato da EDA §4, agora com cesta própria. Anna Snelling abre com Trabalhar pequeno e Decidir cheio — não é bug.

Gate `python backtest.py`: adotar só se a captura top‑N / 90d da nova ordem superar ordenar por preço (ADR-016).

## Iterações

- 16 tarefas (C1–C16), um commit cada, mais um `fix` do export (`cb2f89f`).
- Faixa de validação em três rodadas: a primeira reprovou o export (CHANCE-28), a segunda pegou a imagem Docker velha, a terceira passou.
- Fórmula: esta é a quarta versão (v0 `p̂` → v1 urgência → v2 percentil por visão → v3 chance). Cadeia em `docs/evolucao-do-score.md`.

## Depois desta sessão

Feature fechada. Sem próxima Execute (`.specs/NEXT-ACTION.md`). Não fazer push sem pedido.

O bloco de processo (ferramentas, onde a IA errou, o que eu acrescentei) fica no README. Armadilhas permanentes: `.specs/CONCERNS.md`.
