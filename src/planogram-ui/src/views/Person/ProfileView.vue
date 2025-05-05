<template>
  <section class="profile-page">
    <h2>Личный кабинет</h2>
    <div v-if="user">
      <p><strong>Имя:</strong> {{ user.name }}</p>
      <p><strong>Telegram ID:</strong> {{ user.telegram_id }}</p>
      <p><strong>Статус:</strong> {{ user.is_store_worker ? 'Сотрудник' : 'Клиент' }}</p>
      <button @click="logout" class="logout-button">Выйти</button>
    </div>
    <div v-else-if="loading" class="loading">Загрузка данных...</div>
    <div v-else class="error">Ошибка загрузки профиля</div>
  </section>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import type { Person } from '@/types';
import { authStore } from '@/auth/store';

export default defineComponent({
  name: 'ProfileView',
  setup() {
    const user = ref<Person | null>(null);
    const loading = ref(true);
    const router = useRouter();

    const loadUser = async () => {
      try {
        const user_data = localStorage.getItem('user');
        if (!user_data) throw new Error('No token');
        
        user.value = JSON.parse(user_data) as Person;
      } catch (e) {
        console.error('Profile load error:', e);
        router.push({ name: 'Login' });
      } finally {
        loading.value = false;
      }
    };

    onMounted(loadUser);

    const logout = () => {
      authStore.clearAuth()
      router.push({ name: 'Login' });
    };

    return { user, loading, logout };
  },
});
</script>

<style scoped>
.profile-page {
  max-width: 600px;
  margin: 2rem auto;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.loading {
  color: #666;
  text-align: center;
}

.error {
  color: #dc3545;
  text-align: center;
}

.logout-button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.logout-button:hover {
  background: #bb2d3b;
}
</style>