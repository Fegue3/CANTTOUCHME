// Compact status badge used throughout the record views.

import { statusLabel } from "../utils/format";

export function Badge({ value }: { value: string }) {
  // Map a validation value to the badge styling and label.
  const isValid = value === "valid";
  return <span className={`badge ${isValid ? "badge--valid" : "badge--invalid"}`}>{statusLabel(value)}</span>;
}
