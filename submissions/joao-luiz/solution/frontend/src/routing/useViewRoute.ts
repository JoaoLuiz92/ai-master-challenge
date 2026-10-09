import { useCallback, useSyncExternalStore } from "react";

import { parseLocation, toUrl, type ViewRoute } from "./route";

const listeners = new Set<() => void>();

function subscribe(onStoreChange: () => void): () => void {
  listeners.add(onStoreChange);
  window.addEventListener("popstate", onStoreChange);
  return () => {
    listeners.delete(onStoreChange);
    window.removeEventListener("popstate", onStoreChange);
  };
}

function getSnapshot(): string {
  return `${window.location.pathname}${window.location.search}`;
}

function notify(): void {
  listeners.forEach((listener) => listener());
}

export function useViewRoute(): {
  route: ViewRoute;
  navigate: (next: ViewRoute) => void;
} {
  const location = useSyncExternalStore(subscribe, getSnapshot);
  const sep = location.indexOf("?");
  const route =
    sep === -1
      ? parseLocation(location, "")
      : parseLocation(location.slice(0, sep), location.slice(sep));

  const navigate = useCallback((next: ViewRoute) => {
    const url = toUrl(next);
    if (url === getSnapshot()) {
      return;
    }
    window.history.pushState(null, "", url);
    notify();
  }, []);

  return { route, navigate };
}
