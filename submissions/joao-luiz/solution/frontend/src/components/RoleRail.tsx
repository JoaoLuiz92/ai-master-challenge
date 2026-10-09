import type { Station } from "../routing/route";

const ITEMS: { station: Station; label: string }[] = [
  { station: "vendedor", label: "Vendedor" },
  { station: "gestor", label: "Gestor" },
];

export function RoleRail({
  active,
  onNavigate,
}: {
  active: Station;
  onNavigate: (station: Station) => void;
}) {
  return (
    <nav className="role-rail" aria-label="Papel">
      <p className="role-rail__brand">Foco da Semana</p>
      <ul>
        {ITEMS.map((item) => (
          <li key={item.station}>
            <button
              type="button"
              aria-current={active === item.station ? "page" : undefined}
              onClick={() => onNavigate(item.station)}
            >
              {item.label}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}
