const iconModules = import.meta.glob<string>("@/assets/icons/*.svg", {
  eager: true,
  query: "?raw",
  import: "default",
});

export const ICON_NAMES = [
  "chevron-left",
  "chevron-down",
  "chat",
  "monitor",
  "dialogs",
  "sun",
  "moon",
  "send",
  "user",
  "chat-bubble",
  "clock",
  "warning",
  "inbox-empty",
  "dashboard-empty",
  "users-empty",
  "users",
  "close",
  "info",
] as const;

export type IconName = (typeof ICON_NAMES)[number];

const iconMap = Object.fromEntries(
  Object.entries(iconModules).map(([path, content]) => {
    const name = path.split("/").pop()?.replace(".svg", "") ?? "";
    return [name, content];
  }),
) as Record<string, string>;

export function getIconSvg(name: string): string {
  return iconMap[name] ?? iconMap.info ?? "";
}

export function isIconName(name: string): name is IconName {
  return name in iconMap;
}
