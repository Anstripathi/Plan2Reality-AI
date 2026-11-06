import type { EnvironmentInfo } from "../types/environment";

export default function ToolStatusList({ env }: { env: EnvironmentInfo }) {
  return (
    <ul>
      <li>Python {env.python}</li>
      {Object.entries(env.optional_tools).map(([name, tool]) => (
        <li key={name}>
          {name}: {tool.available ? "available" : "not found on PATH"}
        </li>
      ))}
    </ul>
  );
}
