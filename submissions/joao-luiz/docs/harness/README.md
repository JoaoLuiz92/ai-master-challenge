# Harness de agentes — por que existe, e o que ele faz

Este diretório é a **cópia publicada** do harness que rodei no Cursor. Os arquivos vivos (`.cursor/agents`, `.cursor/rules`, `mcp.json`) ficam na máquina e **não entram no PR**: o avaliador não precisa da pasta do IDE para entender o raciocínio, e misturar config local com a submissão só gera ruído.

A evidência de que o harness existiu de verdade está aqui (contratos) + nos relatórios `.specs/features/<feature>/validation.md` + na cadeia de commits.

## O problema que o harness resolve

Um agente no mesmo chat que escreveu o código tende a validar o próprio trabalho: “os testes passaram, a spec está coberta”. Isso é o equivalente a o autor ser o QA.

O harness separa papéis:

| Papel | Agente | O que pode fazer | O que não pode |
|------|--------|------------------|----------------|
| Orquestrador | `validation-lane` | Disparar faixas, parar se uma falhar | Escrever produto |
| Backend | `backend-tester` | Rodar pytest da matriz da feature | Enfraquecer teste para passar |
| UI | `ui-tester` | Clicar no app real via Playwright MCP | Trocar MCP por vitest ou Chrome DevTools |
| Verificador | `spec-verifier` | AC → `file:line` + asserção; sensor de mutação | Herdar o que o autor “acha que cobriu” |

Regra de ouro: **não validar no chat**. A última tarefa Execute (ou um pedido de UAT) dispara o orquestrador. Quem escreveu não é quem assina o `validation.md`.

## Topologia

```text
                    validation-lane
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
      backend-tester              ui-tester
         (pytest)              (Playwright MCP)
              │                         │
              └────────────┬────────────┘
                           ▼
                    spec-verifier
                 (só se as faixas passaram)
                           │
                           ▼
              .specs/features/<feature>/validation.md
```

Backend e UI rodam **em paralelo** quando a feature exige os dois. Se pytest falha ou o MCP está desconectado, o verificador **não sobe** — senão o relatório mente.

A feature em escopo é a que o usuário nomeou; se ninguém nomeou, a do **Agora** em `.specs/NEXT-ACTION.md`. Não existe `validation-lane.md` por feature: o que muda está na `spec.md` e na `tasks.md`.

## Por que Playwright MCP, e não uma suite versionada

O challenge pede ferramenta que o vendedor **abre**. Vitest cobre componente. Não cobre “cliquei Focar, o card mostrou a ação, o export bateu com a fila”.

A faixa de UI usa o browser de verdade (`browser_navigate` → snapshot → clique pelos refs → print). Cada Independent Test da spec vira um cenário. Print mesmo quando passa: antes, depois do gesto, estado assertado — em `.specs/features/<feature>/ui-evidence/`.

MCP desligado **bloqueia** a faixa. Não inventar `@playwright/test` para “desbloquear”. Não usar Chrome DevTools no lugar.

## O que o verificador exige que um chat não exige

1. **Evidence-or-zero.** Cada critério de aceite da spec precisa de `file:line` + a expressão da asserção. Sem citação = não coberto. “Tem um teste em algum lugar” não conta.
2. **Sensor de discriminação.** 1–3 mutantes no comportamento central, em worktree isolada. O teste tem de **falhar**. Se o mutante sobrevive, a suíte não está assertando o que a spec diz.
3. Relatório no disco (`validation.md`), não um “LGTM” no chat.

As quatro features fecharam assim. Os números estão em cada `validation.md`.

## Como isso se relaciona com o produto

O harness **não pontua o score**. O score é aritmético (ADR-006). O harness pontua o processo: uma tarefa por janela, gate antes do checkbox, autor ≠ verificador.

Sem o harness, o primeiro commit desta branch ia ser um dump do app. Foi desfeito de propósito — falta de `AGENTS.md` e de faixa. Esse erro está no README, seção “Onde a IA errou”.

## Arquivos neste diretório

| Arquivo | Contrato |
|---------|----------|
| [validation-lane.md](validation-lane.md) | Orquestrador e regra da faixa (quando dispara, o que cada faixa lê, prints) |
| [backend-tester.md](backend-tester.md) | Pytest da matriz; parar no primeiro exit ≠ 0 |
| [ui-tester.md](ui-tester.md) | Cenários no browser; BLOCKED se MCP sumir |
| [spec-verifier.md](spec-verifier.md) | Evidence-or-zero + sensor; escreve `validation.md` |

Caminhos nos contratos abaixo estão relativos a `submissions/joao-luiz/`, que é a pasta da submissão.
