export type StripItem = {
  label: string;
  value: string;
  onActivate?: () => void;
};

export function SituationStrip({ items }: { items: StripItem[] }) {
  return (
    <ul className="situation-strip">
      {items.map((item) => (
        <li key={item.label}>
          {item.onActivate ? (
            <button type="button" onClick={item.onActivate}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </button>
          ) : (
            <div>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </div>
          )}
        </li>
      ))}
    </ul>
  );
}
