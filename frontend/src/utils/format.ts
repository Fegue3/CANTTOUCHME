// Formatting helpers for dates and validation labels in the UI.

export function formatDate(value: string | null) {
  // Render API timestamps in the local Portuguese format.
  if (!value) return "Sem data validada";
  return new Intl.DateTimeFormat("pt-PT", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function statusLabel(value: string) {
  // Translate internal status codes into human-friendly labels.
  const labels: Record<string, string> = {
    valid: "Válido",
    invalid: "Inválido",
    invalid_hmac: "HMAC inválido",
    invalid_block_hash: "Hash inválido",
    invalid_previous_hash: "Ligação inválida",
    invalid_rsa_signature: "RSA inválida",
    decrypt_error: "Erro de decifra",
    chain_affected: "Cadeia afetada",
    not_checked: "Não verificado",
  };
  return labels[value] ?? value;
}
