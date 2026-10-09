import type { ViewFilter } from "../api/client";

const LABEL = "Exportar CSV";

export function ExportButton({ filter }: { filter: ViewFilter }) {
  async function download() {
    const path = exportCsvPath(filter);
    const response = await fetch(path);
    if (!response.ok) {
      throw new Error(`GET ${path} failed: ${response.status}`);
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "export.csv";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  return (
    <button type="button" onClick={() => void download()}>
      {LABEL}
    </button>
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
