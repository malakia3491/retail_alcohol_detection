import axios from 'axios';

import {base_url} from '@/api/config';
import type { Person } from '@/types';
import type { AuthResponse } from '@/types';

const auth_url = `${base_url}/auth`;

export const login = async (username: string, password: string): Promise<AuthResponse | null> => {
    const url = `${auth_url}/login/`;
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    formData.append('grant_type', '');
    formData.append('client_id', '');
    formData.append('client_secret', '');
    formData.append('scope', '');
    const result = await axios.post<AuthResponse>(url, formData, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
    })
    const response = result.data as AuthResponse;
    return response;
}

export const me = async (token: string): Promise<Person | null> => {
    const url = `${auth_url}/me/`;
    const request = {
        token: token,
    }
    const result = await axios.post<Person>(url, request, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
    const response = result.data as Person;
    return response;
}