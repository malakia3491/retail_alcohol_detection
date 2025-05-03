import { PlanogramOrder } from "@/types";

export interface PlanogramOrdersPageResponse {
    planogram_orders: PlanogramOrder[];
    total_count: number;
    page: number;
  }