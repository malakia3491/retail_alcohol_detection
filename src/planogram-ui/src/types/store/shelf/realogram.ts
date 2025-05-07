import { ProductMatrix } from "@/types/product_matrix/product_matrix"

export interface  Realogram {
    id?: string
    planogram_id: string
    shelving_id: string
    create_date: string
    img_src: string
    cords: number[]
    product_matrix: ProductMatrix
    accordance: number
    empties_count: number
}