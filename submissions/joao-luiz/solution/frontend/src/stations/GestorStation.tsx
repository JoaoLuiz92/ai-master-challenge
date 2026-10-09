import type { RollupRow } from "../api/client";
import { EmptyState } from "../components/EmptyState";
import { ExportButton } from "../components/ExportButton";
import { RollupTable } from "../components/RollupTable";
import { SituationStrip } from "../components/SituationStrip";
import { formatValue } from "../format/money";
import { deriveSellerKpis, deriveTeamKpis } from "../kpis/summary";
import type { ViewRoute } from "../routing/route";
import type { DataSnapshot } from "../routing/useViewData";
import { DealBands } from "./VendedorStation";

export function GestorStation({
  snapshot,
  route,
  navigate,
}: {
  snapshot: DataSnapshot;
  route: ViewRoute;
  navigate: (next: ViewRoute) => void;
}) {
  const drilling = Boolean(route.agente);
  const rows = snapshot.rollup?.rows ?? [];

  return (
    <section className="station station--gestor">
      <label>
        Gestor
        <select
          name="gestor"
          value={route.gestor ?? ""}
          onChange={(event) =>
            navigate({
              station: "gestor",
              gestor: event.target.value || undefined,
              escritorio: route.escritorio,
            })
          }
        >
          <option value="">Todos</option>
          {snapshot.agents.managers.map((name) => (
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
          value={route.escritorio ?? ""}
          onChange={(event) =>
            navigate({
              station: "gestor",
              gestor: route.gestor,
              escritorio: event.target.value || undefined,
            })
          }
        >
          <option value="">Todos</option>
          {snapshot.agents.offices.map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </select>
      </label>
      {drilling ? (
        <DrillView snapshot={snapshot} route={route} navigate={navigate} />
      ) : (
        <HomeView
          rows={rows}
          onSelectAgent={(agente) =>
            navigate({
              station: "gestor",
              agente,
              gestor: route.gestor,
              escritorio: route.escritorio,
            })
          }
        />
      )}
    </section>
  );
}

function HomeView({
  rows,
  onSelectAgent,
}: {
  rows: RollupRow[];
  onSelectAgent: (agent: string) => void;
}) {
  const kpis = deriveTeamKpis(rows);
  if (rows.length === 0) {
    return <EmptyState kind="no-sellers" />;
  }
  return (
    <>
      <SituationStrip
        items={[
          { label: "Valor do time", value: formatValue(kpis.valorTime) },
          { label: "Na fila", value: String(kpis.naFila) },
          { label: "Esfriando", value: String(kpis.esfriando) },
          { label: "Bons esfriando", value: String(kpis.bonsEsfriando) },
        ]}
      />
      <RollupTable rows={rows} onSelectAgent={onSelectAgent} />
    </>
  );
}

function DrillView({
  snapshot,
  route,
  navigate,
}: {
  snapshot: DataSnapshot;
  route: ViewRoute;
  navigate: (next: ViewRoute) => void;
}) {
  const queue = snapshot.queue ?? { view: null, items: [], revisar: [], empty_message: null };
  const kpis = deriveSellerKpis(queue);
  return (
    <>
      <button
        type="button"
        onClick={() =>
          navigate({
            station: "gestor",
            gestor: route.gestor,
            escritorio: route.escritorio,
          })
        }
      >
        Voltar ao time
      </button>
      <ExportButton filter={{ agent: route.agente }} />
      <SituationStrip
        items={[
          { label: "Valor em Focar", value: formatValue(kpis.valorEmFocar) },
          { label: "Nº Focar", value: String(kpis.nFocar) },
          { label: "Esfriando", value: String(kpis.esfriando) },
          { label: "Revisar", value: String(kpis.revisar) },
        ]}
      />
      <DealBands items={queue.items} revisar={queue.revisar} />
    </>
  );
}
