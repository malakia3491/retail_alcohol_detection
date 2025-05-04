import { reactive } from 'vue';
import axios from 'axios';
import { me } from '@/api/auth';
import { Person } from '@/types';

export const authStore = reactive({
  user: null as Person | null,
  isAuthenticated: false,
  
  async checkAuth() {
    try {
      const token = localStorage.getItem('jwt');
      if (token) {
        this.user = await me(token);
        this.isAuthenticated = true;
      }
    } catch {
      this.clearAuth();
    }
  },
  
  clearAuth() {
    this.user = null;
    this.isAuthenticated = false;
    localStorage.removeItem('jwt');
    delete axios.defaults.headers.common['Authorization'];
  }
});