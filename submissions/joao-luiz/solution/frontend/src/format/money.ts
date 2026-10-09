export function formatValue(value: number): string {
  return `US$ ${value.toLocaleString("pt-BR")}`;
}
