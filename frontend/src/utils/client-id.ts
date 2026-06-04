import { v4 as uuidv4 } from "uuid";

export function createClientMessageId(): string {
  return uuidv4();
}
