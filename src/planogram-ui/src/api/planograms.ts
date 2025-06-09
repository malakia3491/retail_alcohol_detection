import axios from 'axios';

import {base_url} from '@/api/config';
import type { Planogram, AddPlanogramRequest, ApprovePlanogramRequest, PlanogramsResponse, CalibrationBoxesResponse, CalibrationBox } from '@/types'  

const planogram_url = `${base_url}/retail/planograms`;
const video_control_url = `${base_url}/video_control`

export const add_planogram = async (request: AddPlanogramRequest): Promise<string | null> => {
    const url = `${planogram_url}/`;
    const result = await axios.post<string>(url, request, {
        headers: {
            'Content-Type': 'application/json',
        },
    });
    const response = result.data;
    return response;
}

export const get_actual_planograms = async () : Promise<PlanogramsResponse> => {
    const url = `${planogram_url}/actual/`;
    const result = await axios.get<PlanogramsResponse>(url, {
        headers: {
            'Content-Type': 'application/json',
        },
    });
    const response = result.data as PlanogramsResponse
    return response  
}

export const get_planogram = async (order_id: string, planogram_id: string): Promise<Planogram | null> => {
    const url = `${planogram_url}/${order_id}/${planogram_id}`;
    const result = await axios.get<Planogram>(url, {
        headers: {
            'Content-Type': 'application/json',
        },
    });
    const response = result.data as Planogram
    return response
}

export const approve_planogram = async (author_id: string, order_id: string, planogram_id: string): Promise<string> => {
    const url = `${planogram_url}/approve`;
    const req: ApprovePlanogramRequest = {
        approver_id: author_id, 
        order_id: order_id,
        planogram_id: planogram_id,
      };
    const result = await axios.put(url, req);
    const response = result.data
    return response
}

export const unapprove_planogram = async (author_id: string, order_id: string, planogram_id: string): Promise<string> => {
    const url = `${planogram_url}/unapprove`;
    const req: ApprovePlanogramRequest = {
        approver_id: author_id, 
        order_id: order_id,
        planogram_id: planogram_id,
      };
    const result = await axios.put(url, req);
    const response = result.data
    return response
}

export const get_calibrate_boxes = async (formData: FormData): Promise<CalibrationBox[]>  => {
    const url = `${video_control_url}/calibration_boxes`;
    const resp = await axios.post<CalibrationBoxesResponse>(
           url,
           formData,
           { headers:{ 'Content-Type':'multipart/form-data' } }
        );
    const boxes = resp.data.calibration_boxes
    return boxes
}

export const calibrate_planogram = async (
    formData: FormData
): Promise<string> => {
    const url = `${video_control_url}/calibrations`;
    const result = await axios.post(url, formData,{
        headers:{ 'Content-Type':'multipart/form-data' }
    });
    const response = result.data
    return response  
}