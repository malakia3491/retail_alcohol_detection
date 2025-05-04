import { Product } from "../store/product";
import { PlanogramProduct } from "./planogram_product";

export interface ProductBox {
    id?: string;
    product_id: string;
    planogram_product?: PlanogramProduct
    product?: Product;
    pos_x: number;
    is_empty?: boolean;
  }