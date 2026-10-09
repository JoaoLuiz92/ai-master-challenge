import type { QueueItem } from "../api/client";

const COOLING_AFTER_DAYS = 106;

const LABELS = {
  product: "Produto",
  account: "Conta",
  value: "Valor",
  stage: "Estágio",
  days: "Dias no funil",
  score: "SCORE",
  estado: "Estado",
  confidence: "Confiança",
  reason: "Motivo",
  action: "Ação",
  cooling: "Esfriando",
} as const;

export function QueueList({ items }: { items: QueueItem[] }) {
  return (
    <ol>
      {items.map((item) => (
        <li key={item.opportunity_id}>
          <DealCard item={item} />
        </li>
      ))}
    </ol>
  );
}

export function DealCard({ item }: { item: QueueItem }) {
  return (
    <article>
      <h2>
        <span>{LABELS.product}</span> {item.product}
      </h2>
      <dl>
        <Field label={LABELS.account} value={item.account} />
        <Field label={LABELS.value} value={formatValue(item.value)} />
        <Field label={LABELS.stage} value={item.deal_stage} />
        <Field label={LABELS.days} value={String(item.age_days)} />
        <Field label={LABELS.score} value={String(item.score)} />
        <Field label={LABELS.estado} value={item.estado} />
        <Field label={LABELS.confidence} value={item.confidence} />
        <Field label={LABELS.reason} value={item.reason} />
        <Field label={LABELS.action} value={item.action} />
      </dl>
      {item.age_days > COOLING_AFTER_DAYS ? <span>{LABELS.cooling}</span> : null}
    </article>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}

function formatValue(value: number): string {
  return `US$ ${value.toLocaleString("pt-BR")}`;
}
