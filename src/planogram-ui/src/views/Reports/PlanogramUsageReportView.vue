<template>
    <section class="usage-report-page">
      <h2>Отчёт об использовании планограмм</h2>
  
      <div class="period-selector">
        <label>
          Период с
          <input type="date" v-model="startDate" :max="today" />
        </label>
        <label>
          по
          <input type="date" v-model="endDate" :max="today" />
        </label>
        <button @click="loadReport" :disabled="!isValidPeriod || loading">
          Загрузить
        </button>
        <div v-if="!isValidPeriod" class="error-text">
          Даты должны быть: start ≤ end ≤ сегодня
        </div>
      </div>
  
      <div v-if="loading" class="loader">Загрузка…</div>
      <div v-else-if="error" class="error-text">{{ error }}</div>
      <table v-else class="usage-table">
        <thead>
          <tr>
            <th>Стеллаж</th>
            <th>Планограмма</th>
            <th>Магазин</th>
            <th>Дата одобрения</th>
            <th>Утвердил</th>
            <th>Дата калибровки</th>
            <th>Калибровал</th>
            <th>Сред. % соответствия</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(plans, shelf) in report.rows" :key="shelf">
            <tr
              v-for="(row, planId) in plans"
              :key="`${shelf}-${planId}`"
            >
              <td>{{ shelf }}</td>
              <td>{{ "От " + formatDate(row.planogram_date) }}</td>
              <td>{{ row.store_name }}</td>
              <td>{{ formatDate(row.approval_date) }}</td>
              <td>{{ row.approver_name }}</td>
              <td>{{ formatDate(row.calibration_date) }}</td>
              <td>{{ row.calibrator_name }}</td>
              <td>{{ formatPercent(row.avg_accordance_percent) }}</td>
            </tr>
          </template>
        </tbody>
      </table>
    </section>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, computed, onMounted } from 'vue';
  import { get_planogram_usage_report } from '@/api/reports';
  import {
    PlanogramUsageReport,
    PlanogramUsageReportRow
  } from '@/types';
  
  export default defineComponent({
    name: 'PlanogramUsageReportPage',
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
        new Date(iso).toLocaleDateString('ru-RU');
  
      const formatPercent = (v: number) => v.toFixed(1) + ' %';
  
      onMounted(loadReport);
  
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
  