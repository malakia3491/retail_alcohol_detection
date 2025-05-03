import { ProductMatrix } from "@/types/product_matrix/product_matrix";
import { Person } from "../person_managment/person";
import { Shelving } from "./shelving";
import { PlanogramProduct } from "@/types/product_matrix/planogram_product";

export interface Planogram {
    id?: string;
    author: Person;
    shelving: Shelving;
    createDate: Date;
    products: PlanogramProduct[];
    productMatrix: ProductMatrix;
    approver?: Person;
    approvalDate?: Date;
  }