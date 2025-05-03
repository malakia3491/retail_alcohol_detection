import { Product } from "../store/product";

export interface PlanogramProduct {
    id?: string;
    product: Product;
    count: number;
  }