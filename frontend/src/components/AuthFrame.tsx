import type { ReactNode } from "react";

export function AuthFrame({ title, children }: { title: string; children: ReactNode }) {
  return (
    <main className="auth-page">
      <section className="auth-panel">
        <p className="eyebrow">CANTTOUCHME</p>
        <h1>{title}</h1>
        {children}
      </section>
    </main>
  );
}
