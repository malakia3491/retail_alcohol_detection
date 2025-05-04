import axios from "axios";

export const base_url = "http://127.0.0.1:8000"

axios.interceptors.request.use(config => {
    const token = localStorage.getItem('jwt');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });
  
axios.interceptors.response.use(
    response => response,
    error => {
      if (error.response.status === 401) {
        localStorage.removeItem('jwt');
        localStorage.removeItem('user');
      }
      return Promise.reject(error);
    });