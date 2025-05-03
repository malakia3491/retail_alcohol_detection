import { ProductBox } from "./product_box";

export interface Shelf {
    position: number;
    productBoxes: ProductBox[];
  }