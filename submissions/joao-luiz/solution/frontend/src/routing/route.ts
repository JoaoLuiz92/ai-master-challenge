export type Station = "vendedor" | "gestor";

export type ViewRoute = {
  station: Station;
  agente?: string;
  gestor?: string;
  escritorio?: string;
};

export function parseLocation(pathname: string, search: string): ViewRoute {
  const path = pathname.replace(/\/+$/, "") || "/";
  const station: Station = path === "/gestor" ? "gestor" : "vendedor";
  const params = new URLSearchParams(search.startsWith("?") ? search.slice(1) : search);
  return {
    station,
    ...optionalQuery(params, "agente"),
    ...optionalQuery(params, "gestor"),
    ...optionalQuery(params, "escritorio"),
  };
}

export function toUrl(route: ViewRoute): string {
  const path = route.station === "gestor" ? "/gestor" : "/vendedor";
  const search = new URLSearchParams();
  if (route.agente) {
    search.set("agente", route.agente);
  }
  if (route.gestor) {
    search.set("gestor", route.gestor);
  }
  if (route.escritorio) {
    search.set("escritorio", route.escritorio);
  }
  const query = search.toString();
  return query ? `${path}?${query}` : path;
}

function optionalQuery(
  params: URLSearchParams,
  key: "agente" | "gestor" | "escritorio",
): Partial<Pick<ViewRoute, "agente" | "gestor" | "escritorio">> {
  const value = params.get(key);
  return value ? { [key]: value } : {};
}
