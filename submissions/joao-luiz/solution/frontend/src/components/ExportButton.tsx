import { useState } from "react";

import type { ViewFilter } from "../api/client";

const LABEL = "Exportar CSV";
const ERROR_MESSAGE = "Não foi possível exportar o CSV";

export function ExportButton({ filter }: { filter: ViewFilter }) {
  const [error, setError] = useState<string | null>(null);

  async function download() {
    setError(null);
    const path = exportCsvPath(filter);
    try {
      const response = await fetch(path);
      if (!response.ok) {
        setError(ERROR_MESSAGE);
        return;
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "export.csv";
      anchor.click();
      URL.revokeObjectURL(url);
    } catch {
      setError(ERROR_MESSAGE);
    }
  }

  return (
    <div>
      <button type="button" onClick={() => void download()}>
        {LABEL}
      </button>
      {error ? <p role="alert">{error}</p> : null}
    </div>
  );
}

function exportCsvPath(filter: ViewFilter): string {
  const search = new URLSearchParams();
  if (filter.agent) {
    search.set("agent", filter.agent);
  }
  if (filter.manager) {
    search.set("manager", filter.manager);
  }
  if (filter.office) {
    search.set("office", filter.office);
  }
  const query = search.toString();
  return query ? `/api/export.csv?${query}` : "/api/export.csv";
}
