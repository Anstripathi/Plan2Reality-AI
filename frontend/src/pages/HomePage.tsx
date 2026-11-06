import { useEffect, useState } from "react";
import ToolStatusList from "../components/ToolStatusList";
import { fetchEnvironment } from "../services/api";
import type { EnvironmentInfo } from "../types/environment";

export default function HomePage() {
  const [env, setEnv] = useState<EnvironmentInfo | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchEnvironment()
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
      {env && <ToolStatusList env={env} />}
    </main>
  );
}
