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
      <li
        v-for="s in order.shelvings"
        :key="s.id"
        class="shelving-item"
      >
        <div class="shelving-header" @click="toggleShelf(s.id!)">
          <span class="shelving-name">{{ s.name }}</span>
          <template v-if="hasApproved(s.id!)">
            <span class="status-badge status-approved">Согласована</span>
          </template>
          <template v-else>
            <button class="btn-create" @click.stop="goToCreate(order.id!, s.id!)">
              Создать
            </button>
          </template>
        </div>
        <ul
          v-show="expanded === s.id"
          class="planograms-list"
        >
          <li
            v-if="get_planograms(s.id!).length === 0"
            class="planogram-item"
          >
            Нет планограмм
          </li>
          <li
            v-for="p in get_planograms(s.id!)"
            :key="p.id"
            class="planogram-item"
            @click="goToDetail(order.id!, p.id!)"
          >
            <span>{{ formatDate(p.create_date) }}</span>
            <span>{{ p.author.name }}</span>
            <span
              class="status-badge"
              :class="is_approved(p) ? 'status-approved' : 'status-developing'"
            >
              {{ is_approved(p) ? 'Согласована' : 'На проверке' }}
            </span>
          </li>
        </ul>
      </li>
    </ul>
  </section>

  <div v-else class="loading">Загрузка деталей приказа...</div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import type { PlanogramOrder, Planogram } from '@/types';
import { get_planogram_order } from '@/api/orders';
import { formatDate } from '@/utils/date_utils';

export default defineComponent({
  name: 'OrderDetailsView',
  setup() {
    const route = useRoute();
    const router = useRouter();
    const orderId = route.params.id as string;

    const order = ref<PlanogramOrder | null>(null);
    const expanded = ref<string | null>(null);

    onMounted(async () => {
      order.value = await get_planogram_order(orderId);
    });

    const toggleShelf = (id: string) => {
      expanded.value = expanded.value === id ? null : id;
    };

    const is_approved = (p: Planogram) => !!p.approver;

    const get_planograms = (shelfId: string): Planogram[] =>
      (order.value?.shelving_assignments[shelfId] as Planogram[]) || [];

    const hasApproved = (shelfId: string) =>
      get_planograms(shelfId).some(is_approved);

    const goToDetail = (order_id: string, planId: string) => {
      const params = {
        order_id: order_id,
        planogram_id: planId
      }
      router.push({ name: 'PlanogramDetail', params: params });
    };

    const goToCreate = (orderId: string, shelvingId: string) => {
      router.push({
        name: 'CreatePlanogram',
        params: { order_id: orderId, shelving_id: shelvingId },
      });
    };

    const statusClass = (st: string) => ({
      'status-created': st === 'создан',
      'status-developing': st === 'разрабатывается',
      'status-declined': st === 'отклонён',
      'status-approved': st === 'согласован',
    });

    return {
      order, expanded,
      toggleShelf, is_approved, get_planograms, hasApproved,
      goToDetail, goToCreate,
      formatDate, statusClass,
    };
  },
});
</script>

<style scoped>
.order-detail-page {
  padding: 2rem;
  max-width: 800px;
  margin: auto;
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
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
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
.shelvings-list, .planograms-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.shelving-item {
  margin-bottom: 1rem;
}
/* белый фон строк */
.shelving-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  background: #fff;
  padding: 0.75rem 1rem;
  border: 1px solid var(--border);
  border-radius: 6px;
}
.planograms-list {
  max-height: 200px;
  overflow-y: auto;
  margin: 0.5rem 0 0 1rem;
}
.planogram-item {
  display: flex;
  justify-content: space-between;
  background: #fff;
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid var(--border);
}
.planogram-item:last-child {
  border-bottom: none;
}
.planogram-item:hover {
  background: var(--bg);
}
.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  color: #fff;
  font-size: 0.875rem;
  font-weight: 500;
  text-transform: capitalize;
}
.status-approved {
  background-color: #10b981;
}
.status-developing {
  background-color: #3b82f6;
}
.status-created {
  background-color: #3b82f6;
}
.status-developing { background-color: #0b22f5; }
.status-declined { background-color: #b6133c; }
.status-approved { background-color: #10b981; }

.btn-create {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  background-color: var(--primary);
  color: #fff;
  cursor: pointer;
}
.btn-create:hover {
  background-color: var(--primary-light);
}
</style>
