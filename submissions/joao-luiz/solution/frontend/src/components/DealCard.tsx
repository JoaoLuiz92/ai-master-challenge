import type { QueueItem } from "../api/client";
import { formatValue } from "../format/money";

const COOLING_AFTER_DAYS = 106;

export const SCORE_TOOLTIP = "posição nesta visão, 0–100";

const LABELS = {
  product: "Produto",
  account: "Conta",
  value: "Valor",
  days: "Dias no funil",
  score: "SCORE",
  estado: "Estado",
  cooling: "Esfriando",
} as const;

export function DealCard({
  item,
  variant,
}: {
  item: QueueItem;
  variant: "focar" | "acompanhar";
}) {
  if (variant === "acompanhar") {
    return (
      <article className="deal-card deal-card--acompanhar">
        <span>{item.product}</span>
        <span>{item.account}</span>
        <span>{formatValue(item.value)}</span>
        <span>{item.action}</span>
        <Score score={item.score} />
        {item.age_days > COOLING_AFTER_DAYS ? (
          <span className="badge-cooling">{LABELS.cooling}</span>
        ) : null}
      </article>
    );
  }

  return (
    <article className="deal-card deal-card--focar">
      <h2 className="deal-card__action">{item.action}</h2>
      <p className="deal-card__reason">{item.reason}</p>
      <dl className="deal-card__facts">
        <div>
          <dt>{LABELS.value}</dt>
          <dd>{formatValue(item.value)}</dd>
        </div>
        <div>
          <dt>{LABELS.days}</dt>
          <dd>{String(item.age_days)}</dd>
        </div>
        <div>
          <dt>{LABELS.estado}</dt>
          <dd>{item.estado}</dd>
        </div>
      </dl>
      {item.age_days > COOLING_AFTER_DAYS ? (
        <span className="badge-cooling">{LABELS.cooling}</span>
      ) : null}
      <Score score={item.score} />
    </article>
  );
}

function Score({ score }: { score: number }) {
  return (
    <p className="deal-card__score" title={SCORE_TOOLTIP}>
      {LABELS.score} {score}
    </p>
  );
}
