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
      <button @click="loadReport" :disabled="!isValidPeriod">
        Загрузить
      </button>
      <div v-if="!isValidPeriod" class="error-text">
        Даты должны быть: start ≤ end ≤ сегодня
      </div>
    </div>

    <ExportToExcel
      tableId="usage-report-table"
      filename="planogram_usage_report.xlsx"
      sheetName="Usage"
      :reportName="'Отчёт об использовании планограмм'"
      :period="formattedPeriod"
      :generatedBy="authStore.user?.name || ''"
    />

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
          <template v-for="(row, shelf) in shelves" :key="shelf">
            <tr>
              <td>{{ row.store_name }}</td>
              <td>{{ row.shelving_name }}</td>
              <td>{{ 'От ' + formatDate(row.planogram_date) }}</td>
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
  </section>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import ExportToExcel from '@/components/ExportToExcel.vue';
import { authStore } from '@/auth/store';

type UsageRow = {
  store_name: string;
  shelving_name: string;
  planogram_date: string;
  approval_date: string;
  approver_name: string;
  calibration_date: string;
  calibrator_name: string;
  count: number;
  avg_accordance_percent: number;
};

type UsageReport = {
  rows: Record<string, Record<string, UsageRow>>;
};

export default defineComponent({
  name: 'PlanogramUsageReportPage',
  components: { ExportToExcel },
  setup() {
    const today = new Date().toISOString().slice(0, 10);
    const startDate = ref(today);
    const endDate = ref(today);

    const report = ref<UsageReport>({
      rows: {
        'Магазин 1': {
          'Стеллаж 1': {
            store_name: 'Магазин 1', shelving_name: 'Стеллаж 1',
            planogram_date: '2025-06-01T10:00:00Z', approval_date: '2025-06-01T12:00:00Z',
            approver_name: 'Сотрудник 0000019', calibration_date: '2025-06-02T09:00:00Z',
            calibrator_name: 'Сотрудник 0000017', count: 15, avg_accordance_percent: 72.4,
          },
          'Стеллаж 2': {
            store_name: 'Магазин 1', shelving_name: 'Стеллаж 2',
            planogram_date: '2025-06-02T11:30:00Z', approval_date: '2025-06-02T13:00:00Z',
            approver_name: 'Сотрудник 0000019', calibration_date: '2025-06-03T10:30:00Z',
            calibrator_name: 'Сотрудник 0000024', count: 18, avg_accordance_percent: 68.9,
          },
          'Стеллаж 3': {
            store_name: 'Магазин 1', shelving_name: 'Стеллаж 3',
            planogram_date: '2025-06-03T09:15:00Z', approval_date: '2025-06-03T11:45:00Z',
            approver_name: 'Сотрудник 0000019', calibration_date: '2025-06-04T08:45:00Z',
            calibrator_name: 'Сотрудник 0000022', count: 20, avg_accordance_percent: 75.1,
          },
        },
        'Магазин 2': {
          'Стеллаж 1': {
            store_name: 'Магазин 2', shelving_name: 'Стеллаж 1',
            planogram_date: '2025-06-01T09:00:00Z', approval_date: '2025-06-01T10:30:00Z',
            approver_name: 'Сотрудник 0000019', calibration_date: '2025-06-02T09:30:00Z',
            calibrator_name: 'Сотрудник 0000021', count: 22, avg_accordance_percent: 82.3,
          },
          'Стеллаж 2': {
            store_name: 'Магазин 2', shelving_name: 'Стеллаж 2',
            planogram_date: '2025-06-02T12:00:00Z', approval_date: '2025-06-02T14:00:00Z',
            approver_name: 'Сотрудник 0000019', calibration_date: '2025-06-03T10:00:00Z',
            calibrator_name: 'Сотрудник 0000018', count: 19, avg_accordance_percent: 79.7,
          },
          'Стеллаж 3': {
            store_name: 'Магазин 2', shelving_name: 'Стеллаж 3',
            planogram_date: '2025-06-03T08:45:00Z', approval_date: '2025-06-03T10:15:00Z',
            approver_name: 'Сотрудник 0000019', calibration_date: '2025-06-04T08:30:00Z',
            calibrator_name: 'Сотрудник 0000012', count: 24, avg_accordance_percent: 88.2,
          },
        },
        'Магазин 3': {
          'Стеллаж 1': {
            store_name: 'Магазин 3', shelving_name: 'Стеллаж 1',
            planogram_date: '2025-06-01T11:00:00Z', approval_date: '2025-06-01T12:30:00Z',
            approver_name: 'Сотрудник 0000019', calibration_date: '2025-06-02T09:15:00Z',
            calibrator_name: 'Сотрудник 0000013', count: 17, avg_accordance_percent: 65.8,
          },
          'Стеллаж 2': {
            store_name: 'Магазин 3', shelving_name: 'Стеллаж 2',
            planogram_date: '2025-06-02T10:45:00Z', approval_date: '2025-06-02T12:15:00Z',
            approver_name: 'Сотрудник 0000019', calibration_date: '2025-06-03T09:45:00Z',
            calibrator_name: 'Сотрудник 0000015', count: 21, avg_accordance_percent: 70.4,
          },
          'Стеллаж 3': {
            store_name: 'Магазин 3', shelving_name: 'Стеллаж 3',
            planogram_date: '2025-06-03T09:30:00Z', approval_date: '2025-06-03T11:00:00Z',
            approver_name: 'Сотрудник 0000019', calibration_date: '2025-06-04T08:15:00Z',
            calibrator_name: 'Сотрудник 0000016', count: 23, avg_accordance_percent: 74.9,
          },
        },
      }
    });

    const isValidPeriod = computed(() =>
      startDate.value && endDate.value && startDate.value <= endDate.value && endDate.value <= today
    );

    const loadReport = () => {
      // данные уже статичны
    };

    const formatDate = (iso: string) => iso ? new Date(iso).toLocaleDateString('ru-RU') : '—';
    const formatPercent = (v: number) => `${v.toFixed(1)} %`;

    const formattedPeriod = computed(() => {
      const d1 = new Date(startDate.value);
      const d2 = new Date(endDate.value);
      const opt = { day: '2-digit', month: '2-digit', year: 'numeric' } as const;
      return d1.toLocaleDateString('ru-RU', opt) + ' — ' + d2.toLocaleDateString('ru-RU', opt);
    });

    onMounted(() => authStore.checkAuth());

    return { today, startDate, endDate, report, isValidPeriod, loadReport, formatDate, formatPercent, formattedPeriod, authStore };
  },
});
</script>

<style scoped>
.usage-report-page {
  padding: 1rem 2rem;
}
.usage-report-page h2 {
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
