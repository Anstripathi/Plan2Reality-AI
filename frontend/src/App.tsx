import { useEffect, useState } from "react";

type Env = { python: string; optional_tools: Record<string, { available: boolean }> };

export default function App() {
  const [env, setEnv] = useState<Env | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/environment")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(setEnv)
      .catch((e: Error) => setError(e.message));
  }, []);

  return (
    <main style={{ fontFamily: "system-ui", padding: 24 }}>
      <h1>Plan2Reality AI</h1>
      <p>From 2D Blueprint to 3D Reality.</p>
      <h2>Backend status</h2>
      {error && <p role="alert">Backend unreachable: {error}</p>}
      {!env && !error && <p>Checking…</p>}
      {env && (
        <ul>
          <li>Python {env.python}</li>
          {Object.entries(env.optional_tools).map(([k, v]) => (
            <li key={k}>{k}: {v.available ? "available" : "not found"}</li>
          ))}
        </ul>
      )}
    </main>
  );
}
