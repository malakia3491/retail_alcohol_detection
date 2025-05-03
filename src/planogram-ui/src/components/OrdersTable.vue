<template>
  <table class="orders-table">
    <thead>
      <tr>
        <th>Дата создания</th>
        <th>Автор</th>
        <th>Дата разработки</th>
        <th>Дата внедрения</th>
        <th>Статус</th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="order in orders"
        :key="order.id"
        class="orders-row"
        @click="goToDetail(order)"
      >
        <td>{{ formatDate(order.create_date) }}</td>
        <td>{{ order.author.name }}</td>
        <td>{{ formatDate(order.develop_date) }}</td>
        <td>{{ formatDate(order.implementation_date) }}</td>
        <td>
          <span class="status-badge" :class="statusClass(order.status)">
            {{ order.status }}
          </span>
        </td>
      </tr>
      <tr v-if="orders.length === 0">
        <td colspan="5" class="no-data">Нет приказов</td>
      </tr>
    </tbody>
  </table>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';
import { useRouter } from 'vue-router';
import type { PlanogramOrder } from '@/types'; 

export default defineComponent({
  name: 'OrdersTable',
  props: {
    orders: {
      type: Array as PropType<PlanogramOrder[]>,
      required: true,
    },
  },
  setup() {
    const router = useRouter();

    const goToDetail = (order: PlanogramOrder) => {
      router.push({
        name: 'OrderDetail',
        params: { id: order.id },
      });
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

    const statusClass = (status: string) => {
      switch (status) {
        case 'В работе':
          return 'status-developing';
        case 'Отменён':
          return 'status-declined';
        case 'Согласован':
          return 'status-approved';
        default:
          return '';
      }
    };

    return { goToDetail, formatDate, statusClass };
  },
});
</script>

<style scoped>
.orders-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--surface);
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  border-radius: 8px;
  overflow: hidden;
}

.orders-table th,
.orders-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border);
}

.orders-table th {
  background: var(--bg);
  font-weight: 600;
  color: var(--text-secondary);
}

.orders-row {
  cursor: pointer;
  transition: background 0.2s;
}

.orders-row:hover {
  background: var(--bg);
}

.no-data {
  text-align: center;
  color: var(--text-secondary);
  padding: 1.5rem;
}

/* Бейдж статуса */
.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
  color: rgb(0, 0, 0);
  text-transform: capitalize;
}

/* Цвета для статусов */
.status-created {
  background-color: #3b82f6; /* синий */
}

.status-developing {
  background-color: #f59e0b; /* оранжевый */
}

.status-declined {
  background-color: #ef4444; /* красный */
}

.status-approved {
  background-color: #10b981; /* зелёный */
}
</style>
