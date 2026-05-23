import React from "react";

import * as recordsApi from "../api/recordsApi";
import { Badge } from "../components/Badge";
import { FieldError } from "../components/FieldError";
import type { RecordItem } from "../types";
import { friendlyError } from "../utils/errors";
import { formatDate } from "../utils/format";

export function RecordsPage({ token }: { token: string }) {
  const [records, setRecords] = React.useState<RecordItem[]>([]);
  const [page, setPage] = React.useState(1);
  const [pageSize] = React.useState(10);
  const [total, setTotal] = React.useState(0);
  const [startDate, setStartDate] = React.useState("");
  const [endDate, setEndDate] = React.useState("");
  const [status, setStatus] = React.useState<"all" | "valid" | "invalid">("all");
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  const loadRecords = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await recordsApi.listRecords(token, {
        page,
        page_size: pageSize,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        status: status === "all" ? undefined : status,
      });
      setRecords(response.records);
      setTotal(response.total);
    } catch (err) {
      setError(friendlyError(err, "Erro ao carregar registos."));
    } finally {
      setLoading(false);
    }
  }, [endDate, page, pageSize, startDate, status, token]);

  React.useEffect(() => {
    void loadRecords();
  }, [loadRecords]);

  const lastPage = Math.max(1, Math.ceil(total / pageSize));

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Registos</p>
          <h1>Histórico cifrado</h1>
        </div>
        <button type="button" onClick={() => void loadRecords()}>
          Atualizar
        </button>
      </div>
      <div className="filters">
        <label>
          Inicio
          <input
            value={startDate}
            onChange={(event) => {
              setStartDate(event.target.value);
              setPage(1);
            }}
            type="date"
          />
        </label>
        <label>
          Fim
          <input
            value={endDate}
            onChange={(event) => {
              setEndDate(event.target.value);
              setPage(1);
            }}
            type="date"
          />
        </label>
        <label>
          Estado
          <select
            value={status}
            onChange={(event) => {
              setStatus(event.target.value as "all" | "valid" | "invalid");
              setPage(1);
            }}
          >
            <option value="all">Todos</option>
            <option value="valid">Válidos</option>
            <option value="invalid">Inválidos</option>
          </select>
        </label>
      </div>
      <FieldError message={error} />
      {loading && <p className="muted">A carregar...</p>}
      <div className="record-list">
        {records.map((record) => (
          <article className="record-card" key={record.id}>
            <div className="record-card__head">
              <strong>Bloco {record.block_index}</strong>
              <Badge value={record.validation.overall} />
            </div>
            <time>{formatDate(record.timestamp)}</time>
            <p>{record.text ?? "Conteúdo não apresentado porque a validação falhou."}</p>
            <div className="validation-grid">
              <span>HMAC <Badge value={record.validation.hmac} /></span>
              <span>Hash <Badge value={record.validation.block_hash} /></span>
              <span>Anterior <Badge value={record.validation.previous_hash} /></span>
              <span>RSA <Badge value={record.validation.rsa_signature} /></span>
              <span>Decifra <Badge value={record.validation.decrypt} /></span>
            </div>
          </article>
        ))}
      </div>
      {!loading && records.length === 0 && <p className="muted">Sem registos para mostrar.</p>}
      <div className="pagination">
        <button type="button" onClick={() => setPage((value) => Math.max(1, value - 1))} disabled={page <= 1}>
          Anterior
        </button>
        <span>
          Página {page} de {lastPage}
        </span>
        <button type="button" onClick={() => setPage((value) => Math.min(lastPage, value + 1))} disabled={page >= lastPage}>
          Seguinte
        </button>
      </div>
    </section>
  );
}
