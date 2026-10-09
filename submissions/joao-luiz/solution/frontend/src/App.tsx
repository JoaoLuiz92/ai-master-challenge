import { useEffect } from "react";

import { AppShell } from "./components/AppShell";
import type { Station } from "./routing/route";
import { useViewData } from "./routing/useViewData";
import { useViewRoute } from "./routing/useViewRoute";
import { GestorStation } from "./stations/GestorStation";
import { VendedorStation } from "./stations/VendedorStation";

const PREFERRED_AGENT = "Anna Snelling";

export function App() {
  const { route, navigate } = useViewRoute();
  const { snapshot, status } = useViewData(route);

  useEffect(() => {
    const path = window.location.pathname.replace(/\/+$/, "") || "/";
    if (path !== "/vendedor" && path !== "/gestor") {
      navigate({ station: "vendedor", agente: PREFERRED_AGENT });
    }
  }, [navigate]);

  function onRail(station: Station) {
    if (station === "vendedor") {
      navigate({ station: "vendedor", agente: route.agente ?? PREFERRED_AGENT });
      return;
    }
    navigate({
      station: "gestor",
      gestor: route.gestor,
      escritorio: route.escritorio,
    });
  }

  return (
    <AppShell route={route} onNavigate={onRail}>
      {status === "error" ? (
        <p role="alert">Não foi possível carregar a fila</p>
      ) : status === "loading" || !snapshot ? (
        <p>Carregando a fila</p>
      ) : route.station === "gestor" ? (
        <GestorStation snapshot={snapshot} route={route} navigate={navigate} />
      ) : (
        <VendedorStation snapshot={snapshot} route={route} navigate={navigate} />
      )}
    </AppShell>
  );
}
