import axios from 'axios';

import {base_url} from '@/api/config';
import type { PlanogramOrder } from '@/types'  
import type { PlanogramOrdersPageResponse } from '@/types/responses/planogram_orders_page_response';

const orders_url = `${base_url}/retail/planogram_orders`;

const parse_result = (result: any): PlanogramOrder => {
    const order = result = {
      ...result,
      create_date: new Date(result.create_date),
      develop_date: new Date(result.develop_date),
      implementation_date: new Date(result.implementation_date),
    };
    return order;
}

export const get_page_planogram_orders = async (page: number, page_size: number): Promise<PlanogramOrdersPageResponse | null> => {
  const url = `${orders_url}/page/${page}`;
  const params = {
    page_size: page_size,
  };
  const result = await axios.get<PlanogramOrdersPageResponse>(url, { params });
  const planogram_orders: Array<PlanogramOrder> = [];
  if (result.data) 
    for (const order of result.data.planogram_orders) 
      planogram_orders.push(parse_result(order));
  result.data.planogram_orders = planogram_orders;
  return result.data;
};

export const get_planogram_order = async (order_id: string): Promise<PlanogramOrder | null> => {
  const url = `${orders_url}/${order_id}`;
  const result = await axios.get<PlanogramOrder>(url);
  return parse_result(result.data);
};

export const get_actual_planogram_orders = async (page: number, page_size: number): Promise<PlanogramOrdersPageResponse | null> => {
  const url = `${orders_url}/actual/page/${page}`;
  const params = {
    page_size: page_size,
  };
  const result = await axios.get<PlanogramOrdersPageResponse>(url, { params });
  const planogram_orders: Array<PlanogramOrder> = [];
  if (result.data) 
    for (const order of result.data.planogram_orders) 
      planogram_orders.push(parse_result(order));
  result.data.planogram_orders = planogram_orders;
  return result.data;
};