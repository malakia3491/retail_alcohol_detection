import { PlanogramProduct } from "./planogram_product";
import { Shelf } from "./shelf";

export interface ProductMatrix {
    products: PlanogramProduct[]
    shelfs: Shelf[];
  }