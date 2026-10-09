import { useState } from "react";

import type { QueueItem, ReviewItem } from "../api/client";
import { CollapsibleBand } from "../components/CollapsibleBand";
import { DealCard } from "../components/DealCard";
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
            items={queue.items}
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
  revisar,
  revisarKey = 0,
  openRevisar = false,
  onPass,
}: {
  items: QueueItem[];
  revisar: ReviewItem[];
  revisarKey?: number;
  openRevisar?: boolean;
  onPass?: (item: QueueItem) => void;
}) {
  const focar = items.filter((item) => item.estado === "Focar");
  const acompanhar = items.filter((item) => item.estado === "Acompanhar");

  return (
    <div className="deal-bands">
      <div id="band-focar">
        <CollapsibleBand title="Focar" count={focar.length} defaultOpen>
          {focar.length === 0 ? (
            <EmptyState kind="only-revisar" count={revisar.length} />
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
