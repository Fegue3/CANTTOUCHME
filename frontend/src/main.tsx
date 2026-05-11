import React from "react";
import ReactDOM from "react-dom/client";

import "./styles.css";

type HealthResponse = {
  api: "ok" | "error";
  database: "ok" | "error";
};

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

function StatusBadge({ label, status }: { label: string; status: "ok" | "error" }) {
  const isOnline = status === "ok";

  return (
    <div className={`status-badge ${isOnline ? "status-badge--online" : "status-badge--offline"}`}>
      <span className="status-dot" aria-hidden="true" />
      <span>
        {label} {isOnline ? "online" : "offline"}
      </span>
    </div>
  );
}

function App() {
  const [health, setHealth] = React.useState<HealthResponse | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(true);

  async function loadHealth() {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/health`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = (await response.json()) as HealthResponse;
      setHealth(data);
    } catch (err) {
      setHealth(null);
      setError(err instanceof Error ? err.message : "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  }

  React.useEffect(() => {
    void loadHealth();
  }, []);

  return (
    <main className="app-shell">
      <section className="health-panel" aria-labelledby="health-title">
        <div>
          <p className="eyebrow">CANTTOUCHME</p>
          <h1 id="health-title">Project skeleton</h1>
          <p className="description">
            Frontend React ligado ao backend FastAPI. A base de dados e validada com um
            pedido simples ao PostgreSQL.
          </p>
        </div>

        <div className="status-list" aria-live="polite">
          {loading && <p className="muted">A verificar servicos...</p>}

          {!loading && health && (
            <>
              <StatusBadge label="API" status={health.api} />
              <StatusBadge label="Database" status={health.database} />
            </>
          )}

          {!loading && error && (
            <div className="error-box">
              <strong>API offline</strong>
              <span>{error}</span>
            </div>
          )}
        </div>

        <div className="actions">
          <button type="button" onClick={() => void loadHealth()}>
            Testar novamente
          </button>
          <a href={`${API_URL}/docs`} target="_blank" rel="noreferrer">
            Abrir FastAPI docs
          </a>
        </div>
      </section>
    </main>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
