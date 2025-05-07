import axios from 'axios';

import {base_url} from '@/api/config';
import type { Shelving, ShelvingsResponse } from '@/types'  

const shelvings_url = `${base_url}/retail/shelvings`;

export const get_shelvings = async (): Promise<Shelving[]> => {
    const url = `${shelvings_url}/`;
    const result = await axios.get<ShelvingsResponse>(url,);
    const shelvings = result.data.shelvings as Shelving[];
    return shelvings;
  };

export const get_shelving = async (shelving_id: string): Promise<Shelving | null> => {
    const url = `${shelvings_url}/${shelving_id}/`;
    const result = await axios.get<ShelvingsResponse>(url,);
    const shelving = result.data.shelvings[0] as Shelving;
    return shelving;
  };