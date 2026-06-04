export function getCurrentPageTitle(path: string): string {
  if (path === "/chatter") {
    return "Chatter Workspace";
  }
  if (path === "/teamlead") {
    return "Teamlead Monitor";
  }
  if (path === "/lead/dialogs") {
    return "Dialogs";
  }
  if (path === "/admin/users") {
    return "Users";
  }
  if (path.startsWith("/invite/")) {
    return "Create account";
  }
  return "CRM Chatters";
}
