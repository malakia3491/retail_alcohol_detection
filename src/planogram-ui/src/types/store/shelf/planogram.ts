import { ProductMatrix } from "@/types/product_matrix/product_matrix";
import { Person } from "../person_managment/person";
import { Shelving } from "./shelving";
import { PlanogramProduct } from "@/types/product_matrix/planogram_product";

export interface Planogram {
    id?: string;
    author: Person;
    shelving: Shelving;
    create_date: Date;
    products: PlanogramProduct[];
    product_matrix: ProductMatrix;
    approver?: Person;
    approval_date?: Date;
  }