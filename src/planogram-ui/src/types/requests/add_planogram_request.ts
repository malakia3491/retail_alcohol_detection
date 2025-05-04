import { ProductMatrix } from "../product_matrix/product_matrix"

export interface AddPlanogramRequest {
    order_id: string
    author_id: string
    shelving_id: string
    product_matrix: ProductMatrix
}
