import axios from 'axios';

import {base_url} from '@/api/config';
import type { Store, StoreResponse } from '@/types'  

const stores_url = `${base_url}/retail/stores`;

export const get_stores = async (): Promise<Store[]> => {
    const url = `${stores_url}/`;
    const result = await axios.get<StoreResponse>(url)
    const response = result.data.stores;
    return response;
}