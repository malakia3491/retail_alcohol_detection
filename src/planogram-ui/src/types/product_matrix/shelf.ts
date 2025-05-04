import { ProductBox } from "./product_box";

export interface Shelf {
    position: number;
    product_boxes: ProductBox[];
  }