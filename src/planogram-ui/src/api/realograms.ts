import axios from 'axios';

import {base_url} from '@/api/config';
import type { Realogram, RealogramsResponse, RealogramsPageResponse } from '@/types'  

const realograms_url = `${base_url}/retail/realograms`;

export const getRealogram = async (
  store_id: string,
  realogram_id: string
): Promise<Realogram> => {
  const response = await axios.get<Realogram>(
    realograms_url+`/${store_id}/${realogram_id}`
  );
  return response.data;
};

export const get_actual_realograms = async (store_id: string): Promise<Realogram[]> => {
    const url = `${realograms_url}/actual/${store_id}`;
    const result = await axios.get<RealogramsResponse>(url,);
    const realograms = result.data.realograms as Realogram[];
    return realograms;
}

export const getRealogramsPage = async (params: {
  store_id: string;
  shelving_id?: string;
  date_start: string;
  date_end: string;
  page: number;
  page_size: number;
}): Promise<RealogramsPageResponse> => {
  const { store_id, shelving_id, date_start, date_end, page, page_size } = params;

  const query = new URLSearchParams({
    store_id,
    date_start: date_start,
    date_end: date_end,
    page: String(page),
  });

  if (shelving_id) query.append('shelving_id', shelving_id);

  const response = await axios.get(realograms_url+`/page/${page}`, {
    params: {
      store_id,
      shelving_id,
      date_start: date_start,
      date_end: date_end,
      page,
      page_size,
    },
  });

  return response.data;
};