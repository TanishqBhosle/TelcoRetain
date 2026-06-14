export function StatusPill({ value }: { value: string }) {
  return <span className={`status status-${value.toLowerCase().replace(/\s+/g, "-")}`}>{value}</span>;
}
