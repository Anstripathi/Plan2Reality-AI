import type { EnvironmentInfo } from "../types/environment";

export async function fetchEnvironment(): Promise<EnvironmentInfo> {
  const response = await fetch("/api/environment");
  if (!response.ok) {
    throw new Error(`Backend returned HTTP ${response.status}`);
  }
  return (await response.json()) as EnvironmentInfo;
}
