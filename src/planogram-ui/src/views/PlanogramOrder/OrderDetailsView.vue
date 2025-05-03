<template>
  <section class="order-detail-page" v-if="order">
    <h2>Детали приказа №{{ order.id }}</h2>

    <div class="order-info">
      <div class="info-row">
        <span class="label">Автор:</span>
        <span class="value">{{ order.author.name }}</span>
      </div>
      <div class="info-row">
        <span class="label">Дата создания:</span>
        <span class="value">{{ formatDate(order.create_date) }}</span>
      </div>
      <div class="info-row">
        <span class="label">Дата разработки:</span>
        <span class="value">{{ formatDate(order.develop_date) }}</span>
      </div>
      <div class="info-row">
        <span class="label">Дата внедрения:</span>
        <span class="value">{{ formatDate(order.implementation_date) }}</span>
      </div>
      <div class="info-row">
        <span class="label">Статус приказа:</span>
        <span class="value status-badge" :class="statusClass(order.status)">
          {{ order.status }}
        </span>
      </div>
    </div>

    <h3>Стеллажи</h3>
    <ul class="shelvings-list">
      <li v-for="s in order.shelvings" :key="s.id" class="shelving-item">
        <span class="shelving-name">{{ s.name }}</span>
        <button
          v-if="!s.isApproved"
          class="btn-create"
          @click="goToCreate(order.id, s.id)"
        >
          Создать
        </button>
        <span v-else class="status-badge status-approved">
          Согласована
        </span>
      </li>
    </ul>
  </section>

  <div v-else class="loading">Загрузка деталей приказа...</div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import type { PlanogramOrder } from '@/types';
import { get_planogram_order } from '@/api/orders';

export default defineComponent({
  name: 'OrderDetailsView',
  setup() {
    const route = useRoute();
    const router = useRouter();

    const order = ref<PlanogramOrder | null>(null);

    const orderId = route.params.id as string;

    const fetchOrder = async (id: string) => {
      try {
        const response = await get_planogram_order(id);
        order.value = response as PlanogramOrder;
        console.log('Приказ загружен:', order.value);
      } catch (err) {
        console.error('Ошибка при загрузке приказа:', err);
      }
    };

    onMounted(() => {
      fetchOrder(orderId);
    });

    const statusClass = (status: string) => {
      switch (status) {
        case 'создан':
          return 'status-created';
        case 'разрабатывается':
          return 'status-developing';
        case 'отклонён':
          return 'status-declined';
        case 'согласован':
          return 'status-approved';
        default:
          return '';
      }
    };

    const formatDate = (d: string | Date | null | undefined) => {
      if (d == null) {
        return '—';
      }

      let dt: Date;
      if (typeof d === 'string') {
        const isoMatch = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/.test(d);
        const isoString = isoMatch ? `${d}Z` : d;
        dt = new Date(isoString);
      } else {
        dt = d;
      }

      if (isNaN(dt.getTime())) {
        console.warn('Invalid date passed to formatDate:', d);
        return '—';
      }

      return dt.toLocaleDateString('ru-RU', {
        year:   'numeric',
        month:  'long',
        day:    'numeric',
      });
    };

    const goToCreate = (order_id: string, shelving_id: string) => {
      router.push({
        name: 'CreatePlanogram',
        params: { 
          order_id: order_id, 
          shelving_id: shelving_id
        }
      });
    };

    return {
      order,
      formatDate,
      statusClass,
      goToCreate,
    };
  },
});
</script>

<style scoped>
.order-detail-page {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.loading {
  padding: 2rem;
  text-align: center;
  color: var(--text-secondary);
}

.order-info {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
}

.info-row {
  display: flex;
  margin-bottom: 0.75rem;
}

.info-row .label {
  width: 150px;
  font-weight: 600;
  color: var(--text-secondary);
}

.info-row .value {
  color: var(--text);
}

.shelvings-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.shelving-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
}

.shelving-name {
  font-weight: 500;
  color: var(--text);
}

.btn-create {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  background-color: var(--primary);
  color: #fff;
  transition: background 0.2s;
}

.btn-create:hover {
  background-color: var(--primary-light);
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #fff;
  text-transform: capitalize;
}

.status-created { background-color: #3b82f6; }
.status-developing { background-color: #f59e0b; }
.status-declined { background-color: #ef4444; }
.status-approved { background-color: #10b981; }
</style>
