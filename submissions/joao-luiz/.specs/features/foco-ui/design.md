# Foco da Semana — Reorganização da UX (`foco-ui`) Design

**Spec**: `.specs/features/foco-ui/spec.md`
**Status**: Execute complete (T1–T18). `validation.md` ainda não existe.

---

## Architecture Overview

Feature **só de frontend**. Zero mudança no backend, no motor ou nos contratos de API (AD-001..007 intocados). A chave é inverter a fonte da verdade da UI: hoje `App.tsx` guarda `role` + `filter` em estado mutável de React; passa a derivar tudo da **URL** (path = estação, query = recorte). Um hook `useViewRoute` sincroniza URL ↔ estado via History API + `popstate`; um `useViewData` traduz a rota em chamadas aos endpoints **já existentes** e devolve o snapshot; as estações renderizam faixa de situação + bandas (vendedor) ou rollup + drill (gestor).

Os KPIs da faixa e o "Esfriando" são **derivados no cliente** do mesmo payload (`QueueResponse` / `RollupRow[]`), sem endpoint novo (ADR-011).

```mermaid
graph TD
    URL[URL: /vendedor|/gestor + query] <--> ROUTE[useViewRoute<br/>History API + popstate]
    ROUTE --> DATA[useViewData<br/>mapeia rota -> fetch]
    DATA -->|/api/queue| QAPI[(queue payload)]
    DATA -->|/api/rollup| RAPI[(rollup payload)]
    DATA -->|/api/agents| AAPI[(agents payload)]
    QAPI --> KPI[deriveSellerKpis]
    RAPI --> KPIT[deriveTeamKpis]
    ROUTE --> SHELL[AppShell: RoleRail + âncora + outlet]
    SHELL --> VST[VendedorStation]
    SHELL --> GST[GestorStation]
    KPI --> STRIP[SituationStrip]
    VST --> STRIP
    VST --> BANDS[BandList: Focar/Acompanhar/Revisar]
    BANDS --> CARD[DealCard variants + ReviewRow]
    GST --> KPIT
    GST --> ROLLUP[RollupTable clicável]
    ROLLUP -->|clique = ?agente=| DATA
    VST --> EXP[ExportButton contextual]
    GST --> EXP
```

Fluxo típico: trilho/clique muda a URL → `useViewRoute` emite nova rota → `useViewData` dispara `fetch` no endpoint certo → deriva KPIs → estação re-renderiza. Voltar/avançar do browser dispara `popstate`, mesma cadeia, sem reload.

---

## Code Reuse Analysis

### Existing Components to Leverage

| Component | Location | How to Use |
| --------- | -------- | ---------- |
| Tipos do payload (`QueueResponse`, `QueueItem`, `ReviewItem`, `RollupRow`, `AgentsResponse`, `ViewFilter`, `Role`) | `frontend/src/api/client.ts:1-72` | Reusar como contrato; a derivação de KPI e as estações consomem esses tipos sem alterá-los. |
| `queuePath` / `rollupPath` / `withParams` | `frontend/src/api/client.ts:118-143` | Reaproveitar a montagem de query para os `fetch` guiados pela rota. |
| Lógica de download do CSV (`exportCsvPath`, blob/anchor) | `frontend/src/components/ExportButton.tsx:5-41` | Base do novo `ExportButton` contextual + tratamento de erro (FOCO-32). |
| `formatValue` (US$ pt-BR) | `frontend/src/components/QueueList.tsx:62-64` | Extrair para util compartilhado e reusar na faixa, cards e rollup. |
| `DealCard` / `QueueList` | `frontend/src/components/QueueList.tsx` | Refatorar em variantes de densidade (Focar herói / Acompanhar compacto); reusar os rótulos PT. |
| `ReviewSection` / `EmptyState` | `frontend/src/components/ReviewSection.tsx` | Base para `ReviewRow` (com motivo de estar parado) e os `EmptyState` por caso. |
| `ManagerRollup` | `frontend/src/components/ManagerRollup.tsx` | Refatorar: corrigir o `<td>` "Bons esfriando" sem `<th>` (FOCO-27) e tornar linhas clicáveis (FOCO-24). |
| Padrão de teste Vitest + Testing Library | `frontend/src/**/*.test.tsx` | Mesma stack para os testes co-locados das novas unidades. |

### Integration Points

| System | Integration Method |
| ------ | ------------------ |
| Endpoints existentes (`/api/queue`, `/api/rollup`, `/api/agents`, `/api/export.csv`) | Consumidos sem alteração; a rota decide qual chamar e com quais params. |
| Backend / motor | Nenhuma mudança. A paridade de "Esfriando" (`age_days > 106`) espelha o `cooling` do motor. |
| Browser History API | `pushState`/`popstate` para navegação sem reload; jsdom cobre nos testes. |
| Nginx (`frontend/nginx.conf`) | SPA fallback: rotas `/vendedor` e `/gestor` devem servir `index.html` (verificar `try_files`). |

---

## Components

### useViewRoute (hook)

- **Purpose**: Fonte única da verdade da navegação: lê e escreve estação + recorte na URL.
- **Location**: `frontend/src/routing/useViewRoute.ts`
- **Interfaces**:
  - `useViewRoute(): { route: ViewRoute; navigate(next: ViewRoute): void }`
  - `parseLocation(pathname: string, search: string): ViewRoute` — pura, testável sem DOM.
  - `toUrl(route: ViewRoute): string` — pura, inverso de `parseLocation`.
- **Dependencies**: `window.history`, `window.location`, `popstate`, `useSyncExternalStore`.
- **Reuses**: `withParams` (padrão de query).

### useViewData (hook)

- **Purpose**: Traduzir `ViewRoute` em chamadas de API e devolver o snapshot + estado de carga/erro.
- **Location**: `frontend/src/routing/useViewData.ts`
- **Interfaces**:
  - `useViewData(route: ViewRoute): { snapshot: ViewSnapshot | null; status: "loading" | "ready" | "error" }`
- **Dependencies**: `fetch`, `queuePath`/`rollupPath`, `/api/agents`.
- **Reuses**: tipos e paths de `client.ts`. Substitui o `createViewClient` mutável por derivação pela rota (o client antigo some do caminho principal).

### kpis (util puro)

- **Purpose**: Derivar os números da faixa de situação.
- **Location**: `frontend/src/kpis/summary.ts`
- **Interfaces**:
  - `deriveSellerKpis(queue: QueueResponse): SellerKpis` — valorEmFocar, nFocar, esfriando, revisar.
  - `deriveTeamKpis(rows: RollupRow[]): TeamKpis` — valorTime, naFila, esfriando, bonsEsfriando.
- **Dependencies**: nenhuma.
- **Reuses**: tipos de `client.ts`. `esfriando` usa `age_days > 106`.

### AppShell + RoleRail

- **Purpose**: Chrome persistente: trilho de papel, âncora "Visão em 31/12/2017", slot da estação.
- **Location**: `frontend/src/components/AppShell.tsx`, `frontend/src/components/RoleRail.tsx`
- **Interfaces**: `AppShell({ route, children })`; `RoleRail({ active, onNavigate })`.
- **Dependencies**: `useViewRoute`.
- **Reuses**: —.

### SituationStrip

- **Purpose**: Faixa de texto+número; KPIs do vendedor ou do time; Focar/Revisar clicáveis, Esfriando/Bons esfriando não.
- **Location**: `frontend/src/components/SituationStrip.tsx`
- **Interfaces**: `SituationStrip({ items })` onde cada item tem `{ label, value, onActivate? }`.
- **Dependencies**: —.
- **Reuses**: `formatValue`.

### BandList + CollapsibleBand + DealCard (variantes) + ReviewRow

- **Purpose**: As três faixas; Focar expandida (card herói), Acompanhar/Revisar colapsadas com contagem; densidades distintas.
- **Location**: `frontend/src/components/BandList.tsx`, `CollapsibleBand.tsx`, refactor de `QueueList.tsx`.
- **Interfaces**:
  - `BandList({ items, revisar })` — separa `estado` Focar/Acompanhar e Revisar.
  - `CollapsibleBand({ title, count, defaultOpen, children })`.
  - `DealCard({ item, variant: "focar" | "acompanhar" })` — herói vs linha compacta.
  - `ReviewRow({ item })` — motivo de estar parado + ação, sem SCORE.
- **Dependencies**: —.
- **Reuses**: rótulos PT e `formatValue` do `QueueList` atual.

### RollupTable (refactor)

- **Purpose**: Tabela de pessoas, cabeçalhos alinhados, linhas clicáveis para o drill.
- **Location**: `frontend/src/components/RollupTable.tsx` (evolui `ManagerRollup.tsx`).
- **Interfaces**: `RollupTable({ rows, onSelectAgent })`.
- **Dependencies**: —.
- **Reuses**: `formatValue`.

### ExportButton (refactor contextual)

- **Purpose**: Exportar a fila da visão atual; só onde há fila; erro visível.
- **Location**: `frontend/src/components/ExportButton.tsx`.
- **Interfaces**: `ExportButton({ filter })` com estado de erro.
- **Dependencies**: `/api/export.csv`.
- **Reuses**: `exportCsvPath` + download atuais.

### VendedorStation / GestorStation

- **Purpose**: Compor faixa + bandas + export (vendedor); faixa + rollup + drill + export (gestor).
- **Location**: `frontend/src/stations/VendedorStation.tsx`, `GestorStation.tsx`.
- **Interfaces**: `VendedorStation({ snapshot, route, navigate })`; `GestorStation({ snapshot, route, navigate })`.
- **Dependencies**: componentes acima, `useViewData`.
- **Reuses**: tudo acima.

---

## Data Models

### ViewRoute (estado derivado da URL)

```typescript
type Station = "vendedor" | "gestor";

interface ViewRoute {
  station: Station;
  agente?: string;   // vendedor: quem sou eu; gestor: drill
  gestor?: string;   // só na estação gestor
  escritorio?: string;
}
```

**Relationships**: `station === "vendedor"` ou `station === "gestor"` com `agente` → `GET /api/queue?view=mine&agent=<agente>`. `station === "gestor"` sem `agente` → `GET /api/rollup?manager=<gestor>&office=<escritorio>`.

### SellerKpis / TeamKpis

```typescript
interface SellerKpis {
  valorEmFocar: number;  // soma value onde estado === "Focar"
  nFocar: number;        // contagem estado === "Focar"
  esfriando: number;     // contagem items com age_days > 106
  revisar: number;       // revisar.length
}

interface TeamKpis {
  valorTime: number;       // soma expected_value_sum
  naFila: number;          // soma queued_count
  esfriando: number;       // soma cooling_count
  bonsEsfriando: number;   // soma good_deals_cooling
}
```

**Relationships**: derivados de `QueueResponse` e `RollupRow[]` (client.ts), sem persistência.

---

## Error Handling Strategy

| Error Scenario | Handling | User Impact |
| -------------- | -------- | ----------- |
| Rota desconhecida | `parseLocation` cai para `station: "vendedor"`; `navigate` reescreve a URL | Usuário sempre aterrissa numa estação válida (FOCO-07). |
| Agente-fantasma (`empty`) ou `agente` desconhecido na query | `EmptyState` com copy "escolha outro vendedor" | Ensina o próximo gesto, não erro (FOCO-20, borda). |
| Fila trabalhável vazia com Revisar não-vazio | Focar vazio aponta N em Revisar | Caminho de recuperação claro (FOCO-21). |
| Recorte de gestor sem vendedores | `EmptyState` "nenhum vendedor neste gestor/escritório"; sem export | Mensagem específica (FOCO-22). |
| `fetch` da fila/rollup falha | `status: "error"`, mensagem no lugar do conteúdo | Sem tela branca; coerente com o alert atual, por estação. |
| Export falha (rede/status != 200) | `ExportButton` captura e exibe erro | Falha de export deixa de ser silenciosa (FOCO-23). |

---

## Risks & Concerns

| Concern | Location (file:line) | Impact | Mitigation |
| ------- | -------------------- | ------ | ---------- |
| Router caseiro (History API) pode divergir de `popstate`/SSR fallback do nginx | `frontend/src/routing/useViewRoute.ts` (novo), `frontend/nginx.conf` | Voltar/compartilhar link quebra; 404 em refresh de `/gestor` | `parseLocation`/`toUrl` puras e testadas; adicionar `try_files $uri /index.html` no nginx; teste de `popstate` em jsdom. |
| Bug atual: `<td>` "Bons esfriando" sem `<th>` desalinha a tabela | `frontend/src/components/ManagerRollup.tsx:29-33` | Colunas desalinhadas quando há destaque | `RollupTable` com `<th>` para toda coluna exibida (FOCO-27) + teste. |
| Export hoje lança `Error` sem captura na UI | `frontend/src/components/ExportButton.tsx:8-11` | Clique sem feedback em falha | Capturar e exibir estado de erro (FOCO-23/32). |
| `createViewClient` guarda `role/filter` mutável fora da URL | `frontend/src/api/client.ts:79-116` | Estado fora da URL quebra o "reproduzir pela URL" (FOCO-04) | Trocar por `useViewData(route)`; manter só os tipos/paths puros do client. |
| Derivação de "Esfriando" no cliente pode divergir do backend | `frontend/src/kpis/summary.ts` (novo) | KPI mente vs motor | Fixar `age_days > 106` idêntico ao `cooling`; teste de borda em 106 e 107. |
| Omitir estágio no card trabalhável conflita com RF2/LEAD-04 (texto antigo) | `.specs/features/lead-scorer/spec.md` (RF2) | Parecer regressão de spec | ADR-010 + nota de apresentação já no topo de `lead-scorer/spec.md`: estágio vive no payload/CSV, não no chrome. |

> Nenhum concern de segurança: feature de leitura, sem auth/entrada externa/segredos; superfície é o mesmo payload já exposto.

---

## Tech Decisions (only non-obvious ones)

| Decision | Choice | Rationale |
| -------- | ------ | --------- |
| Mecanismo de rota | Hook próprio sobre History API (sem `react-router`) | Duas rotas + query; evita dependência de runtime num app de deps mínimas; `parseLocation`/`toUrl` puras são triviais de testar. |
| Fonte da verdade da UI | URL (path+query), não estado mutável de React | Cumpre FOCO-04 (reproduzir pela URL) e simplifica drill/voltar. |
| KPIs e "Esfriando" | Derivados no cliente do payload existente | ADR-011: sem endpoint novo; números já vêm no payload. |
| Drill do gestor | `/api/queue?view=mine&agent=` reusado | Um herói por vez; a fila do vendedor já é exatamente isso. |
| Idioma de rotas/params | Português (`/vendedor`, `?agente=`) | URL é copy de produto, como os valores `Focar`/`Acompanhar`; ADR-004 preserva API/identificadores em inglês. |
| SPA fallback | `try_files $uri /index.html` no nginx | Refresh direto em `/gestor` não pode dar 404. |

> **Project-level decisions:** registradas em `.specs/STATE.md` como AD-008..AD-012 e em `docs/adr/008..012`. Este design conforma a elas; não supera nenhuma.
