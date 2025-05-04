import axios from 'axios';

import {base_url} from '@/api/config';
import type { Product, ProductsResponse } from '@/types'  

const products_url = `${base_url}/retail/products`;
const video_products_url = `${base_url}/video_control`;

export const get_products = async (): Promise<Product[]> => {
    const url = `${products_url}/`;
    const result = await axios.get<ProductsResponse>(url);
    const products = result.data.products as Product[];
    return products;
};

export const load_product_imgs = async (
  product_id: string,
  formData: FormData
): Promise<string> => {
  const response = await axios.post<{ message: string }>(
    `${video_products_url}/product_images/${product_id}`,
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
    }
  );
  return response.data.message;
};