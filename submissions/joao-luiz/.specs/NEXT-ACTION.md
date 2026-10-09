# Próxima ação

Fonte única do que fazer agora. Uma tarefa por janela. Ao fechar: gate → `tasks.md` → commit → reescrever o **Agora** abaixo. Decisões ficam em `STATE.md`. Não atualizar `AGENTS.md` ao avançar a fila.

## Agora

Feature `foco-ui`: Execute T1–T18 fechado. **Próximo:** faixa de validação do harness.

Disparar o subagente `validation-lane`. Contrato: `.cursor/rules/validation-lane.mdc`. Cenários de UI = Independent Tests da `spec.md`. Evidência em `.specs/features/foco-ui/ui-evidence/`. Motor 001–007 intocado; sem endpoint novo.

## Fila

1. Faixa de validação `foco-ui` (ui-tester Playwright MCP → spec-verifier)
2. `validation.md` com evidence-or-zero
