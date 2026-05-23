import React from "react";

import * as recordsApi from "../api/recordsApi";
import { FieldError } from "../components/FieldError";
import type { UserPublic } from "../types";
import { friendlyError } from "../utils/errors";

type AppPageProps = {
  token: string;
  user: UserPublic;
  navigate: (path: string) => void;
};

export function AppPage({ token, user, navigate }: AppPageProps) {
  const [text, setText] = React.useState("");
  const [message, setMessage] = React.useState<string | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      const response = await recordsApi.createRecord(token, text);
      setText("");
      setMessage(`Registo guardado no bloco ${response.block_index}.`);
    } catch (err) {
      setError(friendlyError(err, "Erro ao guardar registo."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Novo registo</p>
          <h1>Livro pessoal</h1>
        </div>
        <div className="crypto-summary">
          <span>{user.encryption_algorithm}</span>
          <span>{user.hmac_algorithm}</span>
        </div>
      </div>
      <form className="record-form" onSubmit={(event) => void submit(event)}>
        <textarea
          aria-label="Texto do novo registo"
          placeholder="Escreva aqui o registo do dia..."
          value={text}
          onChange={(event) => setText(event.target.value)}
          required
          minLength={1}
          maxLength={10000}
        />
        <FieldError message={error} />
        {message && <div className="notice notice--success">{message}</div>}
        <div className="actions-row">
          <button className="primary" type="submit" disabled={loading}>
            {loading ? "A guardar..." : "Guardar registo"}
          </button>
          <button type="button" onClick={() => navigate("/records")}>
            Ver registos
          </button>
          <button type="button" onClick={() => navigate("/chain-status")}>
            Estado da cadeia
          </button>
        </div>
      </form>
    </section>
  );
}
