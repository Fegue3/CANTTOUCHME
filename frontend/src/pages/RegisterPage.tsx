import React from "react";

import * as authApi from "../api/authApi";
import { AuthFrame } from "../components/AuthFrame";
import { FieldError } from "../components/FieldError";
import type { EncryptionAlgorithm, HmacAlgorithm } from "../types";
import { friendlyError } from "../utils/errors";

export function RegisterPage({ navigate }: { navigate: (path: string) => void }) {
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [confirmPassword, setConfirmPassword] = React.useState("");
  const [encryptionAlgorithm, setEncryptionAlgorithm] = React.useState<EncryptionAlgorithm>("AES-128-CBC");
  const [hmacAlgorithm, setHmacAlgorithm] = React.useState<HmacAlgorithm>("HMAC-SHA256");
  const [error, setError] = React.useState<string | null>(null);
  const [success, setSuccess] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await authApi.register({
        email,
        password,
        confirm_password: confirmPassword,
        encryption_algorithm: encryptionAlgorithm,
        hmac_algorithm: hmacAlgorithm,
      });
      setSuccess("Conta criada. Pode iniciar sessão.");
    } catch (err) {
      setError(friendlyError(err, "Erro ao criar conta."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthFrame title="Criar conta">
      <form className="form" onSubmit={(event) => void submit(event)}>
        <label>
          Email
          <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required />
        </label>
        <label>
          Palavra-passe
          <input
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            type="password"
            minLength={8}
            required
          />
        </label>
        <label>
          Confirmar palavra-passe
          <input
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            type="password"
            minLength={8}
            required
          />
        </label>
        <label>
          Cifra
          <select
            value={encryptionAlgorithm}
            onChange={(event) => setEncryptionAlgorithm(event.target.value as EncryptionAlgorithm)}
          >
            <option value="AES-128-CBC">AES-128-CBC</option>
            <option value="AES-128-CTR">AES-128-CTR</option>
          </select>
        </label>
        <label>
          HMAC
          <select value={hmacAlgorithm} onChange={(event) => setHmacAlgorithm(event.target.value as HmacAlgorithm)}>
            <option value="HMAC-SHA256">HMAC-SHA256</option>
            <option value="HMAC-SHA512">HMAC-SHA512</option>
          </select>
        </label>
        <FieldError message={error} />
        {success && <div className="notice notice--success">{success}</div>}
        <button className="primary" type="submit" disabled={loading}>
          {loading ? "A criar..." : "Criar conta"}
        </button>
      </form>
      <button className="link-button" type="button" onClick={() => navigate("/login")}>
        Já tenho conta
      </button>
    </AuthFrame>
  );
}
