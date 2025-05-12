<template>
  <section class="realograms-page">
    <h2>Реалограммы</h2>

    <!-- Панель фильтров -->
    <div class="filters-panel">
      <label class="filter-item">
        <span>Магазин</span>
        <select v-model="storeId" @change="onFilterChange">
          <option
            v-for="store in stores"
            :key="store.id"
            :value="store.id"
          >
            {{ store.name }}
          </option>
        </select>
      </label>

      <label class="filter-item">
        <span>Стеллаж</span>
        <select v-model="shelvingId" @change="onFilterChange">
          <option value="">Все</option>
          <option
            v-for="sh in shelvings"
            :key="sh.id"
            :value="sh.id"
          >
            {{ sh.name }}
          </option>
        </select>
      </label>

      <label class="filter-item">
        <span>С даты</span>
        <input
          type="date"
          v-model="dateStartStr"
          @change="onFilterChange"
        />
      </label>

      <label class="filter-item">
        <span>По дату</span>
        <input
          type="date"
          v-model="dateEndStr"
          @change="onFilterChange"
        />
      </label>
    </div>

    <!-- Таблица реалограмм -->
  <div class="table-wrapper">
    <table class="realograms-table">
      <thead>
        <tr>
          <th>Изображение</th>
          <th>Дата</th>
          <th>Соответствие</th>
          <th>Пустот</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="realogram in realograms"
          :key="realogram.id"
          class="realogram-row clickable"
          @click="goToDetail(realogram, storeId)"
        >
          <td class="img-cell">
            <img :src="base_url + realogram.img_src" alt="Превью" />
          </td>
          <td>{{ formatDateTime(realogram.create_date) }}</td>
          <td>{{ realogram.accordance.toFixed(2) }}%</td>
          <td>{{ realogram.empties_count }}</td>
        </tr>
        <tr v-if="!isLoading && realograms.length === 0">
          <td colspan="4" class="no-data">Нет реалограмм</td>
        </tr>
        <tr v-if="isLoading">
          <td colspan="4" class="loading">Загрузка...</td>
        </tr>
      </tbody>
    </table>
  </div>

    <!-- Пагинация -->
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
import Pagination from '@/components/Pagination.vue';
import {
  getRealogramsPage,
} from '@/api/realograms';
import { formatDateTime } from '@/utils/date_utils';
import type {
  Store,
  Shelving,
  Realogram,
  RealogramsPageResponse,
} from '@/types';
import { get_stores } from '@/api/stores';
import { get_shelvings } from '@/api/shelvings';
import { base_url } from '@/api/config';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'RealogramsPage',
  components: { Pagination },
  setup() {
    const router = useRouter();  
    
    const stores = ref<Store[]>([]);
    const shelvings = ref<Shelving[]>([]);

    const storeId = ref<string>('');
    const shelvingId = ref<string>('');
    const dateStartStr = ref('');
    const dateEndStr = ref('');

    const realograms = ref<Realogram[]>([]);
    const totalCount = ref(0);
    const page = ref(1);
    const pageSize = 10;
    const isLoading = ref(false);

    const loadFilters = async () => {
      try {
        stores.value = await get_stores();
        if (stores.value.length) storeId.value = stores.value[0].id;
        shelvings.value = await get_shelvings();
      } catch (err) {
        console.error('Ошибка фильтров:', err);
      }
    };

    const fetchRealograms = async () => {
      if (!storeId.value || !dateStartStr.value || !dateEndStr.value) return;
      isLoading.value = true;
      try {
        const params = {
          store_id: storeId.value,
          shelving_id: shelvingId.value || undefined,
          date_start: dateStartStr.value,
          date_end: dateEndStr.value,
          page: page.value - 1,
          page_size: pageSize,
        };
        const res: RealogramsPageResponse =
          await getRealogramsPage(params);
        realograms.value = res.realograms;
        totalCount.value = res.total_count;
      } catch (err) {
        console.error('Ошибка реалограмм:', err);
        realograms.value = [];
        totalCount.value = 0;
      } finally {
        isLoading.value = false;
      }
    };

    const onFilterChange = () => {
      page.value = 1;
      fetchRealograms();
    };

    const handlePageChange = (newPage: number) => {
      page.value = newPage;
      fetchRealograms();
    };

    onMounted(async () => {
      await loadFilters();
      // даты по умолчанию: неделя назад — сегодня
      const today = new Date();
      const weekAgo = new Date();
      weekAgo.setDate(today.getDate() - 7);
      dateStartStr.value = weekAgo.toISOString().slice(0, 10);
      dateEndStr.value = today.toISOString().slice(0, 10);
      await fetchRealograms();
    });

    const goToDetail = (realogram: Realogram, storeId: string) => {
      router.push({
        name: 'RealogramDetails',
        params: { id: realogram.id, store_id: storeId},
      });
    };

    return {
      base_url,
      stores,
      shelvings,
      storeId,
      shelvingId,
      dateStartStr,
      dateEndStr,
      realograms,
      totalCount,
      page,
      pageSize,
      isLoading,
      onFilterChange,
      handlePageChange,
      formatDateTime,
      goToDetail, 
    };
  },
});
</script>

<style scoped>
.clickable {
  cursor: pointer;
}
.clickable:hover {
  background: var(--hover);
}

.realograms-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.realograms-page h2 {
  margin-bottom: 1.5rem;
  color: var(--primary);
  font-size: 1.75rem;
}

/* Фильтры */
.filters-panel {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  background: var(--surface);
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  margin-bottom: 2rem;
}

.filter-item {
  display: flex;
  flex-direction: column;
  font-size: 0.9rem;
}

.filter-item span {
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.filter-item select,
.filter-item input[type="date"] {
  padding: 0.5rem;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--bg);
  font-size: 1rem;
}

/* Таблица */
.table-wrapper {
  overflow-x: auto;
  background: var(--surface);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.realograms-table {
  width: 100%;
  border-collapse: collapse;
}

.realograms-table th,
.realograms-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border);
}

.realograms-table th {
  background: var(--bg);
  position: sticky;
  top: 0;
  z-index: 1;
  font-weight: 600;
  color: var(--text-secondary);
}

.realogram-row {
  transition: background 0.2s;
  cursor: default;
}

.realogram-row:hover {
  background: var(--hover);
}

.img-cell {
  width: 100px;
}

.img-cell img {
  max-width: 100%;
  border-radius: 4px;
}

/* Плейсхолдеры */
.no-data,
.loading {
  text-align: center;
  padding: 1.5rem;
  color: var(--text-secondary);
}

/* Пагинация */
</style>
