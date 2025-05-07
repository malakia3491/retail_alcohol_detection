import axios from 'axios';

import {base_url} from '@/api/config';
import type { Realogram, RealogramsResponse } from '@/types'  

const realograms_url = `${base_url}/retail/realograms`;

export const get_actual_realograms = async (store_id: string): Promise<Realogram[]> => {
    const url = `${realograms_url}/actual/${store_id}`;
    const result = await axios.get<RealogramsResponse>(url,);
    const realograms = result.data.realograms as Realogram[];
    return realograms;
}