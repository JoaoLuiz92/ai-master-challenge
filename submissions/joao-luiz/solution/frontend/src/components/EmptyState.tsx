export type EmptyKind = "ghost-agent" | "only-revisar" | "no-sellers";

export function EmptyState({
  kind,
  count = 0,
}: {
  kind: EmptyKind;
  count?: number;
}) {
  return <p role="status">{messageFor(kind, count)}</p>;
}

function messageFor(kind: EmptyKind, count: number): string {
  if (kind === "ghost-agent") {
    return "Este nome não tem carteira. Escolha outro vendedor.";
  }
  if (kind === "only-revisar") {
    return `Nada trabalhável. ${count} em Revisar.`;
  }
  return "nenhum vendedor neste gestor/escritório";
}
