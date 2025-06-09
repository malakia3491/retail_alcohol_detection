<template>
  <section class="report-page">
    <h2>Отчёт по выполнению планограмм</h2>

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
      <button @click="fetchReport" :disabled="!isPeriodValid">
        Загрузить
      </button>
      <div v-if="!isPeriodValid" class="period-error">
        Даты должны быть: start ≤ end ≤ сегодня
      </div>
    </div>

    <ExportToExcel
      tableId="compliance-report-table"
      filename="planogram_compliance_report.xlsx"
      sheetName="Compliance"
      :reportName="'Отчёт по выполнению планограмм'"
      :period="formattedPeriod"
      :generatedBy="authStore.user?.name || ''"
    />

    <table id="compliance-report-table" class="report-table">
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
          <tr v-for="(row, shift) in shifts" :key="`${store}-${shift}`">
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
import { defineComponent, ref, computed, onMounted } from 'vue';
import ExportToExcel from '@/components/ExportToExcel.vue';
import { authStore } from '@/auth/store';

export default defineComponent({
  name: 'PlanogramComplianceReportPage',
  components: { ExportToExcel },
  setup() {
    const today = new Date().toISOString().slice(0, 10);
    const startDate = ref(today);
    const endDate = ref(today);

    const report = ref({
      rows: {
        'Магазин 1': {
          'Первая смена': {
            total_notifications_empty: 8,
            total_notifications_mismatch: 12,
            resolved_on_time_empty: 7,
            resolved_on_time_mismatch: 10,
            unresolved_empty_no_stock: 1,
            avg_reaction_time_empty_min: 4.3,
            avg_reaction_time_mismatch_min: 6.7,
            avg_planogram_accordance_percent: 62.5,
          },
          'Вторая смена': {
            total_notifications_empty: 6,
            total_notifications_mismatch: 9,
            resolved_on_time_empty: 5,
            resolved_on_time_mismatch: 8,
            unresolved_empty_no_stock: 1,
            avg_reaction_time_empty_min: 5.1,
            avg_reaction_time_mismatch_min: 7.9,
            avg_planogram_accordance_percent: 70.2,
          },
        },
        'Магазин 2': {
          'Первая смена': {
            total_notifications_empty: 10,
            total_notifications_mismatch: 5,
            resolved_on_time_empty: 9,
            resolved_on_time_mismatch: 4,
            unresolved_empty_no_stock: 1,
            avg_reaction_time_empty_min: 3.8,
            avg_reaction_time_mismatch_min: 5.4,
            avg_planogram_accordance_percent: 85.9,
          },
          'Вторая смена': {
            total_notifications_empty: 7,
            total_notifications_mismatch: 8,
            resolved_on_time_empty: 6,
            resolved_on_time_mismatch: 7,
            unresolved_empty_no_stock: 1,
            avg_reaction_time_empty_min: 4.7,
            avg_reaction_time_mismatch_min: 6.3,
            avg_planogram_accordance_percent: 78.4,
          },
        },
        'Магазин 3': {
          'Первая смена': {
            total_notifications_empty: 9,
            total_notifications_mismatch: 11,
            resolved_on_time_empty: 8,
            resolved_on_time_mismatch: 9,
            unresolved_empty_no_stock: 2,
            avg_reaction_time_empty_min: 6.5,
            avg_reaction_time_mismatch_min: 8.2,
            avg_planogram_accordance_percent: 68.3,
          },
          'Вторая смена': {
            total_notifications_empty: 5,
            total_notifications_mismatch: 13,
            resolved_on_time_empty: 4,
            resolved_on_time_mismatch: 12,
            unresolved_empty_no_stock: 1,
            avg_reaction_time_empty_min: 7.2,
            avg_reaction_time_mismatch_min: 9.5,
            avg_planogram_accordance_percent: 59.7,
          },
        },
      },
    });

    const isPeriodValid = computed(() => {
      return (
        !!startDate.value &&
        !!endDate.value &&
        startDate.value <= endDate.value &&
        endDate.value <= today
      );
    });
    
    const fetchReport = () => {
      // Статические данные уже загружены
    };

    const formatFloat = (v: number | null) => (v == null ? '—' : v.toFixed(1));
    const formatPercent = (v: number | null) => (v == null ? '—' : v.toFixed(1) + ' %');

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

    onMounted(() => {
      // Инициализация аутентификации при необходимости
      authStore.checkAuth();
    });

    return {
      today,
      startDate,
      endDate,
      report,
      isPeriodValid,
      fetchReport,
      formatFloat,
      formatPercent,
      formattedPeriod,
      authStore,
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
