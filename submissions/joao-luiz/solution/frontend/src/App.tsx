import { useEffect, useRef, useState } from "react";

import {
  createViewClient,
  type AgentOption,
  type Role,
  type ViewFilter,
  type ViewSnapshot,
} from "./api/client";
import { ExportButton } from "./components/ExportButton";
import { ManagerRollup } from "./components/ManagerRollup";
import { QueueLayout } from "./components/ReviewSection";

const PREFERRED_AGENT = "Anna Snelling";

export function App() {
  const clientRef = useRef(createViewClient());
  const [state, setState] = useState<ViewSnapshot | null>(null);
  const [seller, setSeller] = useState(PREFERRED_AGENT);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    loadInitial(clientRef.current)
      .then((next) => {
        if (!active) {
          return;
        }
        setSeller(next.filter.agent ?? PREFERRED_AGENT);
        setState(next);
      })
      .catch(() => {
        if (active) {
          setError("Não foi possível carregar a fila");
        }
      });
    return () => {
      active = false;
    };
  }, []);

  if (error) {
    return (
      <main>
        <p role="alert">{error}</p>
      </main>
    );
  }

  if (!state) {
    return (
      <main>
        <p>Carregando a fila</p>
      </main>
    );
  }

  const agents = state.agents.agents;
  const selected = agents.find((item) => item.sales_agent === seller);

  async function apply(role: Role, filter: ViewFilter) {
    const client = clientRef.current;
    if (role !== client.getState()?.role) {
      await client.setRole(role);
    }
    setState(await client.setFilter(filter));
  }

  return (
    <main>
      <header>
        <h1>Foco da Semana</h1>
        <p>Fila por valor em risco. O SCORE é o percentil desta visão.</p>
      </header>
      <form>
        <label>
          Visão
          <select
            name="visao"
            value={state.role}
            onChange={(event) => {
              const role = event.target.value as Role;
              void apply(role, filterForRole(role, seller, selected, state.filter.office));
            }}
          >
            <option value="seller">Meus deals</option>
            <option value="manager">Time</option>
          </select>
        </label>
        <label>
          Vendedor
          <select
            name="vendedor"
            value={seller}
            onChange={(event) => {
              const name = event.target.value;
              setSeller(name);
              const agent = agents.find((item) => item.sales_agent === name);
              void apply(
                state.role,
                state.role === "seller"
                  ? { agent: name, office: state.filter.office }
                  : {
                      agent: name,
                      manager: agent?.manager ?? state.filter.manager,
                      office: state.filter.office,
                    },
              );
            }}
          >
            {agents.map((item) => (
              <option key={item.sales_agent} value={item.sales_agent}>
                {item.sales_agent}
              </option>
            ))}
          </select>
        </label>
        <label>
          Gestor
          <select
            name="gestor"
            value={state.filter.manager ?? ""}
            onChange={(event) => {
              const manager = event.target.value || undefined;
              void apply(state.role, {
                agent: state.role === "seller" ? seller : undefined,
                manager,
                office: state.filter.office,
              });
            }}
          >
            <option value="">Todos</option>
            {state.agents.managers.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Escritório
          <select
            name="escritorio"
            value={state.filter.office ?? ""}
            onChange={(event) => {
              const office = event.target.value || undefined;
              void apply(state.role, {
                agent: state.role === "seller" ? seller : state.filter.agent,
                manager: state.filter.manager,
                office,
              });
            }}
          >
            <option value="">Todos</option>
            {state.agents.offices.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </label>
        <ExportButton filter={state.filter} />
      </form>
      {state.role === "manager" ? <ManagerRollup rows={state.rollup.rows} /> : null}
      <QueueLayout
        items={state.queue.items}
        revisar={state.queue.revisar}
        emptyMessage={state.queue.empty_message}
        ghostAgent={selected?.empty === true && state.role === "seller"}
      />
    </main>
  );
}

function filterForRole(
  role: Role,
  seller: string,
  selected: AgentOption | undefined,
  office: string | undefined,
): ViewFilter {
  if (role === "manager") {
    return { manager: selected?.manager ?? undefined, office };
  }
  return { agent: seller, office };
}

async function loadInitial(
  client: ReturnType<typeof createViewClient>,
): Promise<ViewSnapshot> {
  let lastError: unknown;
  for (let attempt = 0; attempt < 8; attempt += 1) {
    try {
      const loaded = await client.load();
      const preferred =
        loaded.agents.agents.find(
          (item) => item.sales_agent === PREFERRED_AGENT && !item.empty,
        ) ?? loaded.agents.agents.find((item) => !item.empty);
      if (!preferred) {
        return loaded;
      }
      return client.setFilter({ agent: preferred.sales_agent });
    } catch (error) {
      lastError = error;
      await delay(400);
    }
  }
  throw lastError;
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}
