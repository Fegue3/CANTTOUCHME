// Top-level app shell that restores auth and chooses the active page.

import React from "react";

import * as authApi from "./api/authApi";
import { Layout } from "./components/Layout";
import { AppPage } from "./pages/AppPage";
import { ChainStatusPage } from "./pages/ChainStatusPage";
import { LoginPage } from "./pages/LoginPage";
import { RecordsPage } from "./pages/RecordsPage";
import { RegisterPage } from "./pages/RegisterPage";
import type { UserPublic } from "./types";

const TOKEN_KEY = "canttouchme_token";
const protectedPaths = new Set(["/app", "/records", "/chain-status"]);

export function App() {
  const [path, setPath] = React.useState(window.location.pathname);
  const [token, setToken] = React.useState(() => sessionStorage.getItem(TOKEN_KEY));
  const [user, setUser] = React.useState<UserPublic | null>(null);
  const [loading, setLoading] = React.useState(true);

  // Update browser history and the in-memory route state together.
  const navigate = React.useCallback((nextPath: string) => {
    window.history.pushState({}, "", nextPath);
    setPath(nextPath);
  }, []);

  // Drop all auth state from both storage and React state.
  const clearAuth = React.useCallback(() => {
    sessionStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  }, []);

  React.useEffect(() => {
    function onPopState() {
      setPath(window.location.pathname);
    }
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  React.useEffect(() => {
    // Restore the current user from the stored token on first load.
    async function restore() {
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        setUser(await authApi.me(token));
      } catch {
        clearAuth();
      } finally {
        setLoading(false);
      }
    }
    void restore();
  }, [clearAuth, token]);

  React.useEffect(() => {
    // Redirect the bare root path to the appropriate entry screen.
    if (path === "/") {
      navigate(token ? "/app" : "/login");
    }
  }, [navigate, path, token]);

  React.useEffect(() => {
    // Keep authenticated users away from public pages they should not stay on.
    if (token && user && path !== "/register" && path !== "/login" && !protectedPaths.has(path)) {
      navigate("/app");
    }
  }, [navigate, path, token, user]);

  // Persist a successful login in session storage and React state.
  function handleLogin(nextToken: string, nextUser: UserPublic) {
    sessionStorage.setItem(TOKEN_KEY, nextToken);
    setToken(nextToken);
    setUser(nextUser);
  }

  // Clear the local session and try to invalidate the server session too.
  async function handleLogout() {
    if (token) {
      try {
        await authApi.logout(token);
      } catch {
        // The local token is cleared even if the in-memory backend session is already gone.
      }
    }
    clearAuth();
    navigate("/login");
  }

  if (loading) {
    return <main className="auth-page"><p className="muted">A carregar...</p></main>;
  }

  if (path === "/register") {
    return <RegisterPage navigate={navigate} />;
  }

  if (path === "/login" || !token || !user) {
    return <LoginPage navigate={navigate} onLogin={handleLogin} />;
  }

  let page = <AppPage token={token} user={user} navigate={navigate} />;
  if (path === "/records") {
    page = <RecordsPage token={token} />;
  } else if (path === "/chain-status") {
    page = <ChainStatusPage token={token} />;
  }

  return (
    <Layout user={user} navigate={navigate} onLogout={() => void handleLogout()}>
      {page}
    </Layout>
  );
}
