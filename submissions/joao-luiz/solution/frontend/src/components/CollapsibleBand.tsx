import { useState, type ReactNode } from "react";

export function CollapsibleBand({
  title,
  count,
  defaultOpen,
  children,
}: {
  title: string;
  count: number;
  defaultOpen: boolean;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <section className="collapsible-band">
      <h2>
        <button type="button" aria-expanded={open} onClick={() => setOpen((current) => !current)}>
          {title} ({count})
        </button>
      </h2>
      {open ? children : null}
    </section>
  );
}
