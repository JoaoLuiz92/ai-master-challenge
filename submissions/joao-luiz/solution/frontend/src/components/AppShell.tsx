import type { ReactNode } from "react";

import type { Station, ViewRoute } from "../routing/route";
import { RoleRail } from "./RoleRail";

export const TEMPORAL_ANCHOR = "Visão em 31/12/2017";

export function AppShell({
  route,
  onNavigate,
  children,
}: {
  route: ViewRoute;
  onNavigate: (station: Station) => void;
  children: ReactNode;
}) {
  return (
    <div className="app-shell">
      <RoleRail active={route.station} onNavigate={onNavigate} />
      <div className="app-shell__main">
        <header>
          <p className="app-shell__anchor">{TEMPORAL_ANCHOR}</p>
        </header>
        {children}
      </div>
    </div>
  );
}
