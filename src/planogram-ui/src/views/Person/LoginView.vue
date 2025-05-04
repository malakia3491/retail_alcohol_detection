<template>
    <section class="login-page">
      <h2>Вход в систему</h2>
      <form @submit.prevent="onSubmit" class="login-form">
        <div class="form-group">
          <label for="username">Логин</label>
          <input 
            id="username" 
            v-model="username" 
            required
            autocomplete="username"
          />
        </div>
        <div class="form-group">
          <label for="password">Пароль</label>
          <input 
            id="password" 
            type="password" 
            v-model="password" 
            required
            autocomplete="current-password"
          />
        </div>
        <button 
          type="submit" 
          :disabled="loading"
          class="login-button"
        >
          {{ loading ? 'Входим...' : 'Войти' }}
        </button>
        <div v-if="error" class="error">{{ error }}</div>
      </form>
    </section>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref } from 'vue';
  import { useRouter } from 'vue-router';
  import type { AxiosError } from 'axios';
  import axios from 'axios';
  import type { AuthResponse, Person } from '@/types';
  import { login, me } from '@/api/auth';
  
  export default defineComponent({
    name: 'LoginView',
    setup() {
      const username = ref('');
      const password = ref('');
      const loading = ref(false);
      const error = ref<string | null>(null);
      const router = useRouter();
  
      const handleSuccessfulLogin = async (authData: AuthResponse) => {
        localStorage.setItem('jwt', authData.access_token);
        axios.defaults.headers.common.Authorization = `Bearer ${authData.access_token}`;
  
        try {
          const user = await me(authData.access_token);
          if (user) {
            localStorage.setItem('user', JSON.stringify({
              id: user.id,
              name: user.name,
              access_token: user.access_token,
              telegram_id: user.telegram_id,
              is_active: user.is_active,
              is_worker: user.is_worker
            }));
            
            const redirectPath = user.is_worker ? '/home' : '/login';
            await router.push(redirectPath);
          }
        } catch (e) {
          console.error('Ошибка получения данных пользователя:', e);
          error.value = 'Ошибка авторизации';
        }
      };
  
      const onSubmit = async () => {
        loading.value = true;
        error.value = null;
  
        try {
          const authData = await login(username.value, password.value);
          if (authData) {
            await handleSuccessfulLogin(authData);
          }
        } catch (e: unknown) {
          const axiosError = e as AxiosError;
          if (axiosError.response) {
            error.value = (axiosError.response.data as any).detail || 'Ошибка авторизации';
          } else {
            error.value = 'Сервер недоступен';
          }
        } finally {
          loading.value = false;
          password.value = ''; 
        }
      };
  
      return { username, password, loading, error, onSubmit };
    },
  });
  </script>
  
  <style scoped>
  .login-page {
    max-width: 400px;
    margin: 2rem auto;
    padding: 20px;
    background: #f5f5f5;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  
  .login-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  input {
    padding: 0.8rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
  }
  
  .login-button {
    padding: 0.8rem;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.3s;
  }
  
  .login-button:disabled {
    background: #6c757d;
    cursor: not-allowed;
  }
  
  .login-button:hover:not(:disabled) {
    background: #0056b3;
  }
  
  .error {
    color: #dc3545;
    padding: 0.5rem;
    text-align: center;
    border: 1px solid #dc3545;
    border-radius: 4px;
    background: #fff5f5;
  }
  </style>