export type ToolStatus = { available: boolean; path: string | null };

export type EnvironmentInfo = {
  python: string;
  platform: string;
  optional_tools: Record<string, ToolStatus>;
};
