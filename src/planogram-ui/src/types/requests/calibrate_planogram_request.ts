import { CalibrationBox } from "../product_matrix/calibration_box"

export interface CalibratePlanogramRequest {
    order_id: string
    person_id: string
    shelving_id: string
    store_id: string
    calibration_boxes: CalibrationBox[]
}