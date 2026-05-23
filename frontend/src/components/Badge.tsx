import { statusLabel } from "../utils/format";

export function Badge({ value }: { value: string }) {
  const isValid = value === "valid";
  return <span className={`badge ${isValid ? "badge--valid" : "badge--invalid"}`}>{statusLabel(value)}</span>;
}
