// Page that loads and displays the user's chain integrity summary.

import React from "react";

import * as recordsApi from "../api/recordsApi";
import { FieldError } from "../components/FieldError";
import type { ChainStatusResponse } from "../types";
import { friendlyError } from "../utils/errors";
import { statusLabel } from "../utils/format";

export function ChainStatusPage({ token }: { token: string }) {
  const [status, setStatus] = React.useState<ChainStatusResponse | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  // Fetch the latest chain status from the API.
  const loadStatus = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setStatus(await recordsApi.chainStatus(token));
    } catch (err) {
      setError(friendlyError(err, "Erro ao carregar o estado da cadeia."));
    } finally {
      setLoading(false);
    }
  }, [token]);

  React.useEffect(() => {
    void loadStatus();
  }, [loadStatus]);

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Blockchain local</p>
          <h1>Estado da cadeia</h1>
        </div>
        <button type="button" onClick={() => void loadStatus()}>
          Atualizar
        </button>
      </div>
      <FieldError message={error} />
      {loading && <p className="muted">A validar...</p>}
      {status && (
        <div className="stats-grid">
          <div><span>Total</span><strong>{status.total_blocks}</strong></div>
          <div><span>Válidos</span><strong>{status.valid_blocks}</strong></div>
          <div><span>Inválidos</span><strong>{status.invalid_blocks}</strong></div>
          <div><span>Primeiro inválido</span><strong>{status.first_invalid_block_index ?? "-"}</strong></div>
          <div><span>Estado</span><strong>{statusLabel(status.chain_status)}</strong></div>
        </div>
      )}
    </section>
  );
}
