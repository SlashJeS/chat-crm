export function getCurrentPageTitle(path: string): string {
  if (path === "/chatter") {
    return "Chatter Workspace";
  }
  if (path === "/teamlead") {
    return "Teamlead Monitor";
  }
  if (path === "/lead/dialogs") {
    return "Dialog Assignment";
  }
  if (path === "/lead/users") {
    return "User Management";
  }
  return "CRM Chatters";
}
