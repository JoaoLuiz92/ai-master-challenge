import { useState } from "react";

import type { QueueItem, ReviewItem } from "../api/client";
import { CollapsibleBand } from "../components/CollapsibleBand";
import { DealCard } from "../components/DealCard";
import { DecidirSection } from "../components/DecidirSection";
import { EmptyState } from "../components/EmptyState";
import { ExportButton } from "../components/ExportButton";
import { ReviewRow } from "../components/ReviewRow";
import { SituationStrip } from "../components/SituationStrip";
import { formatValue } from "../format/money";
import { deriveSellerKpis } from "../kpis/summary";
import type { DataSnapshot } from "../routing/useViewData";
import type { ViewRoute } from "../routing/route";

const EMPTY_QUEUE = {
  view: null,
  items: [] as QueueItem[],
  trabalhar: [] as QueueItem[],
  decidir: [] as QueueItem[],
  revisar: [] as ReviewItem[],
  empty_message: null,
};

export function VendedorStation({
  snapshot,
  route,
  navigate,
}: {
  snapshot: DataSnapshot;
  route: ViewRoute;
  navigate: (next: ViewRoute) => void;
}) {
  const queue = snapshot.queue ?? EMPTY_QUEUE;
  const selected = snapshot.agents.agents.find((item) => item.sales_agent === route.agente);
  const ghost = selected?.empty === true;
  const kpis = deriveSellerKpis(queue);
  const [revisarKey, setRevisarKey] = useState(0);
  const [openRevisar, setOpenRevisar] = useState(false);

  function openBand(id: string, expandRevisar = false) {
    if (expandRevisar) {
      setOpenRevisar(true);
      setRevisarKey((value) => value + 1);
    }
    document.getElementById(id)?.scrollIntoView?.();
  }

  return (
    <section className="station station--vendedor">
      <label>
        Vendedor
        <select
          name="vendedor"
          value={route.agente ?? ""}
          onChange={(event) =>
            navigate({ station: "vendedor", agente: event.target.value || undefined })
          }
        >
          {snapshot.agents.agents.map((item) => (
            <option key={item.sales_agent} value={item.sales_agent}>
              {item.sales_agent}
            </option>
          ))}
        </select>
      </label>
      <ExportButton filter={{ agent: route.agente }} />
      {ghost ? (
        <EmptyState kind="ghost-agent" />
      ) : (
        <>
          <SituationStrip
            items={[
              { label: "Valor em Focar", value: formatValue(kpis.valorEmFocar) },
              {
                label: "Nº Focar",
                value: String(kpis.nFocar),
                onActivate: () => openBand("band-focar"),
              },
              { label: "Esfriando", value: String(kpis.esfriando) },
              {
                label: "Revisar",
                value: String(kpis.revisar),
                onActivate: () => openBand("band-revisar", true),
              },
            ]}
          />
          <DealBands
            items={queue.trabalhar ?? queue.items}
            decidir={queue.decidir ?? []}
            revisar={queue.revisar}
            revisarKey={revisarKey}
            openRevisar={openRevisar}
          />
        </>
      )}
    </section>
  );
}

export function DealBands({
  items,
  decidir = [],
  revisar,
  revisarKey = 0,
  openRevisar = false,
  onPass,
}: {
  items: QueueItem[];
  decidir?: QueueItem[];
  revisar: ReviewItem[];
  revisarKey?: number;
  openRevisar?: boolean;
  onPass?: (item: QueueItem) => void;
}) {
  const work = items.filter((item) => item.estado !== "Decidir");
  const focar = work.filter((item) => item.estado === "Focar");
  const acompanhar = work.filter((item) => item.estado === "Acompanhar");
  const parked = decidir.length > 0 ? decidir : items.filter((item) => item.estado === "Decidir");
  const workEmpty = work.length === 0;

  return (
    <div className="deal-bands">
      <div id="band-focar">
        <CollapsibleBand title="Focar" count={focar.length} defaultOpen>
          {focar.length === 0 ? (
            parked.length === 0 ? (
              <EmptyState kind="only-revisar" count={revisar.length} />
            ) : null
          ) : (
            <ol>
              {focar.map((item) => (
                <li key={item.opportunity_id}>
                  <DealCard
                    item={item}
                    variant="focar"
                    onPass={onPass ? () => onPass(item) : undefined}
                  />
                </li>
              ))}
            </ol>
          )}
        </CollapsibleBand>
      </div>
      <div id="band-acompanhar">
        <CollapsibleBand title="Acompanhar" count={acompanhar.length} defaultOpen={false}>
          <ol>
            {acompanhar.map((item) => (
                <li key={item.opportunity_id}>
                  <DealCard
                    item={item}
                    variant="acompanhar"
                    onPass={onPass ? () => onPass(item) : undefined}
                  />
                </li>
            ))}
          </ol>
        </CollapsibleBand>
      </div>
      <DecidirSection items={parked} workEmpty={workEmpty} />
      <div id="band-revisar">
        <CollapsibleBand
          key={revisarKey}
          title="Revisar"
          count={revisar.length}
          defaultOpen={openRevisar}
        >
          <ul>
            {revisar.map((item) => (
              <li key={item.opportunity_id}>
                <ReviewRow item={item} />
              </li>
            ))}
          </ul>
        </CollapsibleBand>
      </div>
    </div>
  );
}
