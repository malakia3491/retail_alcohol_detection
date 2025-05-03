import { Post } from "../post"
import { Store } from "../store"

export interface Person {
    id?: string;
    telegramId?: string;
    isWorker: boolean
    name: string;
  }