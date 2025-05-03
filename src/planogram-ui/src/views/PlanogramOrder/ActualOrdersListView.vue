<template>
  <section class="orders-page">
    <h2>Актуальные приказы</h2>
    <div v-if="isLoading" class="loader">Загрузка...</div>

    <OrdersTable v-else :orders="orders" />

    <Pagination
      :page="page"
      :total="totalCount"
      :page-size="pageSize"
      @update:page="handlePageChange"
    />
  </section>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import OrdersTable from '@/components/OrdersTable.vue';
import Pagination from '@/components/Pagination.vue';
import type { PlanogramOrdersPageResponse } from "@/types";
import type { PlanogramOrder } from '@/types';
import { get_actual_planogram_orders } from '@/api/orders';

export default defineComponent({
  name: 'AllOrders',
  components: { OrdersTable, Pagination },
  setup() {
    const orders = ref<PlanogramOrder[]>([]);
    const totalCount = ref(0);
    const page = ref(1);
    const pageSize = 10;
    const isLoading = ref(false);

    const fetchOrders = async () => {
      isLoading.value = true;
      try {
        let response = await get_actual_planogram_orders(page.value-1, pageSize) as PlanogramOrdersPageResponse;
        orders.value = response.planogram_orders;
        totalCount.value = response.total_count;
      } 
      catch (err) {
        console.error('Ошибка загрузки приказов:', err);
        orders.value = [];
      } finally {
        isLoading.value = false;
      }
    };

    const handlePageChange = (newPage: number) => {
      page.value = newPage;
      fetchOrders();
    };

    onMounted(fetchOrders);

    return {
      orders,
      totalCount,
      page,
      pageSize,
      isLoading,
      handlePageChange,
    };
  },
});
</script>

<style scoped>
.orders-page {
  padding: 1rem 2rem;
}

.orders-page h2 {
  margin-bottom: 1rem;
  color: var(--primary);
}

.loader {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: var(--text-secondary);
}
</style>
