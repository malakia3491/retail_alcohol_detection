export interface PlanogramDataResponse {
    shelving_id: string
    planogram_id: string
    order_id: string
}

export interface PlanogramsResponse{
    planogram_data: PlanogramDataResponse[]
}