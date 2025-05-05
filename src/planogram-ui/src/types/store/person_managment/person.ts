import { Store } from "@/types";

export interface Person {
    id?: string;
    telegram_id?: string;
    is_store_worker: boolean
    is_active: boolean
    store? : Store
    name: string;
    access_token: string
  }


