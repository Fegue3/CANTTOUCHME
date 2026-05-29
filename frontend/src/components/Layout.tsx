// Authenticated application shell with the top navigation bar.

import type { ReactNode } from "react";

import type { UserPublic } from "../types";

type LayoutProps = {
  user: UserPublic;
  navigate: (path: string) => void;
  onLogout: () => void;
  children: ReactNode;
};

export function Layout({ user, navigate, onLogout, children }: LayoutProps) {
  // Wrap protected pages with the shared nav and user controls.
  return (
    <div className="shell">
      <header className="topbar">
        <button className="brand" type="button" onClick={() => navigate("/app")}>
          CANTTOUCHME
        </button>
        <nav className="nav" aria-label="Principal">
          <button type="button" onClick={() => navigate("/app")}>
            Novo
          </button>
          <button type="button" onClick={() => navigate("/records")}>
            Registos
          </button>
          <button type="button" onClick={() => navigate("/chain-status")}>
            Cadeia
          </button>
        </nav>
        <div className="userbox">
          <span>{user.email}</span>
          <button type="button" onClick={onLogout}>
            Sair
          </button>
        </div>
      </header>
      <main className="content">{children}</main>
    </div>
  );
}
