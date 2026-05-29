// Login screen that authenticates the user and restores the app state.

import React from "react";

import * as authApi from "../api/authApi";
import { AuthFrame } from "../components/AuthFrame";
import { FieldError } from "../components/FieldError";
import type { UserPublic } from "../types";
import { friendlyError } from "../utils/errors";

type LoginPageProps = {
  navigate: (path: string) => void;
  onLogin: (token: string, user: UserPublic) => void;
};

export function LoginPage({ navigate, onLogin }: LoginPageProps) {
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  // Submit credentials and store the returned session details.
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await authApi.login(email, password);
      onLogin(response.access_token, response.user);
      navigate("/app");
    } catch (err) {
      setError(friendlyError(err, "Erro ao iniciar sessão."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthFrame title="Iniciar sessão">
      <form className="form" onSubmit={(event) => void submit(event)}>
        <label>
          Email
          <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required />
        </label>
        <label>
          Palavra-passe
          <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" required />
        </label>
        <FieldError message={error} />
        <button className="primary" type="submit" disabled={loading}>
          {loading ? "A entrar..." : "Entrar"}
        </button>
      </form>
      <button className="link-button" type="button" onClick={() => navigate("/register")}>
        Criar conta
      </button>
    </AuthFrame>
  );
}
