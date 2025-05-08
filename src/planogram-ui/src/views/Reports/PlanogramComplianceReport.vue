<template>
    <section class="report-page">
      <h2>Отчёт по выполнению планограмм</h2>
  
      <div class="period-selector">
        <label>
          Период с
          <input type="date" v-model="startDate" :max="today" />
        </label>
        <label>
          по
          <input type="date" v-model="endDate" :max="today" />
        </label>
        <button @click="fetchReport" :disabled="!isPeriodValid || isLoading">
          Загрузить
        </button>
        <div v-if="!isPeriodValid" class="period-error">
          Даты должны быть: start ≤ end ≤ сегодня
        </div>
      </div>
  
      <div v-if="isLoading" class="loader">Загрузка...</div>
      <table v-else class="report-table">
        <thead>
          <tr>
            <th rowspan="2">Магазин</th>
            <th rowspan="2">Смена</th>
            <th colspan="2">Количество уведомлений</th>
            <th colspan="2">Вовремя устранённые отклонения</th>
            <th rowspan="2">Неустранённые пустоты<br/>(нет товара)</th>
            <th colspan="2">Среднее время реагирования (мин)</th>
            <th rowspan="2">Средний % соответствия</th>
          </tr>
          <tr>
            <th>Пустоты</th>
            <th>Несоблюдения планограмм</th>
            <th>Пустоты</th>
            <th>Несоблюдения планограмм</th>
            <th>Пустоты</th>
            <th>Несоблюдения планограмм</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(shifts, store) in report.rows" :key="store">
            <tr
              v-for="(row, shift) in shifts"
              :key="`${store}-${shift}`"
            >
              <td>{{ store }}</td>
              <td>{{ shift }}</td>
              <td>{{ row.total_notifications_empty }}</td>
              <td>{{ row.total_notifications_mismatch }}</td>
              <td>{{ row.resolved_on_time_empty }}</td>
              <td>{{ row.resolved_on_time_mismatch }}</td>
              <td>{{ row.unresolved_empty_no_stock }}</td>
              <td>{{ formatFloat(row.avg_reaction_time_empty_min) }}</td>
              <td>{{ formatFloat(row.avg_reaction_time_mismatch_min) }}</td>
              <td>{{ formatPercent(row.avg_planogram_accordance_percent) }}</td>
            </tr>
          </template>
        </tbody>
      </table>
    </section>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, onMounted, computed } from 'vue';
  import { get_planogram_compliance_report } from '@/api/reports';
  import { PlanogramComplianceReport } from '@/types';

  export default defineComponent({
    name: 'PlanogramComplianceReportPage',
    setup() {
      const today = new Date().toISOString().slice(0, 10);
      const startDate = ref(today);
      const endDate = ref(today);
  
      const report = ref<PlanogramComplianceReport>({ rows: {} });
      const isLoading = ref(false);
  
      const isPeriodValid = computed(() => {
        return (
          !!startDate.value &&
          !!endDate.value &&
          startDate.value <= endDate.value &&
          endDate.value <= today
        );
      });
  
      const fetchReport = async () => {
        if (!isPeriodValid.value) return;
        isLoading.value = true;
        try {
          report.value = await get_planogram_compliance_report(startDate.value, endDate.value)
        } catch (e: any) {
          console.error('Ошибка загрузки отчёта:', e);
          report.value = { rows: {} };
        } finally {
          isLoading.value = false;
        }
      };
  
      const formatFloat = (v: number | null) =>
        v == null ? '—' : v.toFixed(1);
      const formatPercent = (v: number | null) =>
        v == null ? '—' : v.toFixed(1) + ' %';
  
      onMounted(fetchReport);
  
      return {
        today,
        startDate,
        endDate,
        report,
        isLoading,
        isPeriodValid,
        fetchReport,
        formatFloat,
        formatPercent,
      };
    },
  });
  </script>

  <style scoped>
  .report-page {
    padding: 1rem 2rem;
  }
  
  .report-page h2 {
    margin-bottom: 1rem;
    color: var(--primary);
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
  
  .period-error {
    color: red;
    font-size: 0.9rem;
  }
  
  .loader {
    text-align: center;
    padding: 2rem;
    font-size: 1.2rem;
    color: var(--text-secondary);
  }
  
  .report-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
  }
  
  .report-table th,
  .report-table td {
    border: 1px solid #ccc;
    padding: 0.5rem;
    text-align: center;
  }
  
  .report-table th {
    background: #f5f5f5;
    vertical-align: middle;
  }
  
  .report-table th[colspan] {
    text-align: center;
  }
  </style>