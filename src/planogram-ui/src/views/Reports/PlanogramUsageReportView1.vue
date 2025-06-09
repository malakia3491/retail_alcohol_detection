<template>
  <section class="usage-report-page">
    <h2>Отчёт об использовании планограмм</h2>

    <!-- Селектор периода -->
    <div class="period-selector">
      <label>
        Период с
        <input type="date" v-model="startDate" :max="today" />
      </label>
      <label>
        по
        <input type="date" v-model="endDate" :max="today" />
      </label>
      <button
        @click="loadReport"
        :disabled="!isValidPeriod || loading"
      >
        Загрузить
      </button>
      <div v-if="!isValidPeriod" class="error-text">
        Даты должны быть: start ≤ end ≤ сегодня
      </div>
    </div>

    <div v-if="loading" class="loader">Загрузка…</div>
    <div v-else-if="error" class="error-text">{{ error }}</div>

    <div v-else>
      <!-- Кнопка «Экспорт в Excel» -->
      <ExportToExcel
        tableId="usage-report-table"
        filename="planogram_usage_report.xlsx"
        sheetName="Usage"
        :reportName="'Отчёт об использовании планограмм'"
        :period="formattedPeriod"
        :generatedBy="authStore.user?.name || ''"
      />

      <!-- Таблица с ID для экспорта -->
      <table id="usage-report-table" class="usage-table">
        <thead>
          <tr>
            <th>Магазин</th>
            <th>Стеллаж</th>
            <th>Планограмма</th>
            <th>Дата одобрения</th>
            <th>Утвердил</th>
            <th>Дата калибровки</th>
            <th>Калибровал</th>
            <th>Кол-во наблюдений</th>
            <th>Сред. % соответствия</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(shelves, store) in report.rows" :key="store">
            <template v-for="(row, shelfId) in shelves" :key="shelfId">
              <tr>
                <td>{{ row.store_name }}</td>
                <td>{{ row.shelving_name }}</td>
                <td>{{ "От " + formatDate(row.planogram_date) }}</td>
                <td>{{ formatDate(row.approval_date) }}</td>
                <td>{{ row.approver_name }}</td>
                <td>{{ formatDate(row.calibration_date) }}</td>
                <td>{{ row.calibrator_name }}</td>
                <td>{{ row.count }}</td>
                <td>{{ formatPercent(row.avg_accordance_percent) }}</td>
              </tr>
            </template>
          </template>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import { get_planogram_usage_report } from '@/api/reports';
import type {
  PlanogramUsageReport,
  PlanogramUsageReportRow,
} from '@/types';
import ExportToExcel from '@/components/ExportToExcel.vue';
import { authStore } from '@/auth/store';

export default defineComponent({
  name: 'PlanogramUsageReportPage',
  components: { ExportToExcel },
  setup() {
    const today = new Date().toISOString().slice(0, 10);
    const startDate = ref(today);
    const endDate = ref(today);

    const report = ref<PlanogramUsageReport>({ rows: {} });
    const loading = ref(false);
    const error = ref<string | null>(null);

    const isValidPeriod = computed(() => {
      return (
        !!startDate.value &&
        !!endDate.value &&
        startDate.value <= endDate.value &&
        endDate.value <= today
      );
    });

    const loadReport = async () => {
      if (!isValidPeriod.value) return;
      loading.value = true;
      error.value = null;
      try {
        report.value = await get_planogram_usage_report(
          startDate.value,
          endDate.value
        );
      } catch (e: any) {
        error.value = e.response?.data?.message || 'Ошибка загрузки';
      } finally {
        loading.value = false;
      }
    };

    const formatDate = (iso: string) =>
      iso ? new Date(iso).toLocaleDateString('ru-RU') : '—';

    const formatPercent = (v: number) =>
      v != null ? `${v.toFixed(1)} %` : '—';

    // Строка вида "01.06.2025 — 05.06.2025"
    const formattedPeriod = computed(() => {
      const d1 = new Date(startDate.value);
      const d2 = new Date(endDate.value);
      const opt = { day: '2-digit', month: '2-digit', year: 'numeric' } as const;
      return (
        d1.toLocaleDateString('ru-RU', opt) +
        ' — ' +
        d2.toLocaleDateString('ru-RU', opt)
      );
    });

    onMounted(async () => {
      await authStore.checkAuth();
      loadReport();
    });

    return {
      today,
      startDate,
      endDate,
      report,
      loading,
      error,
      isValidPeriod,
      loadReport,
      formatDate,
      formatPercent,
      authStore,
      formattedPeriod,
    };
  },
});
</script>

<style scoped>
.usage-report-page {
  padding: 1rem 2rem;
}

.usage-report-page h2 {
  color: var(--primary);
  margin-bottom: 1rem;
}

.period-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.period-selector label {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.period-selector button {
  padding: 0.5rem 1rem;
}

.error-text {
  color: red;
  margin-left: 1rem;
}

.loader {
  font-style: italic;
  padding: 1rem;
}

.usage-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.usage-table th,
.usage-table td {
  border: 1px solid #ccc;
  padding: 0.5rem;
  text-align: center;
}

.usage-table th {
  background: #f5f5f5;
}
</style>