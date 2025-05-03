import { Post } from "./post";
import { Store } from "./store";

export interface Shift {
    id?: string;
    store: Store;
    name: string;
    post: Post[];
  }