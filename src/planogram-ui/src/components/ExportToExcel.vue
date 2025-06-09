<template>
  <button
    class="export-btn"
    @click="exportToExcel"
    :disabled="!tableId"
  >
    Экспорт в Excel
  </button>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';
// Убедитесь, что SheetJS (xlsx) установлен: npm install xlsx
import * as XLSX from 'xlsx';

export default defineComponent({
  name: 'ExportToExcel',
  props: {
    /** ID HTML-таблицы, которую нужно экспортировать */
    tableId: {
      type: String as PropType<string>,
      required: true,
    },
    /** Имя итогового файла, например "report.xlsx" */
    filename: {
      type: String as PropType<string>,
      default: 'report.xlsx',
    },
    /** Имя листа внутри Excel-файла */
    sheetName: {
      type: String as PropType<string>,
      default: 'Sheet1',
    },
    /** Название отчёта, которое пойдёт в шапку Excel-а */
    reportName: {
      type: String as PropType<string>,
      default: '',
    },
    /** Строка с периодом, например "01.06.2025 — 05.06.2025" */
    period: {
      type: String as PropType<string>,
      default: '',
    },
    /** Имя пользователя, сгенерировавшего отчёт */
    generatedBy: {
      type: String as PropType<string>,
      default: '',
    },
  },
  setup(props) {
    const exportToExcel = () => {
      const tableEl = document.getElementById(
        props.tableId
      ) as HTMLTableElement | null;
      if (!tableEl) {
        console.error(
          `ExportToExcel: не найден элемент TABLE с id="${props.tableId}"`
        );
        return;
      }

      // 1. Создаём новую книгу
      const wb = XLSX.utils.book_new();

      // 2. Собираем первые 4 строки: отчёт, период, автор, пустая строка
      const headerAOA: Array<string[]> = [];
      if (props.reportName) {
        headerAOA.push([`Отчёт: ${props.reportName}`]);
      }
      if (props.period) {
        headerAOA.push([`Период: ${props.period}`]);
      }
      if (props.generatedBy) {
        headerAOA.push([`Сгенерировал: ${props.generatedBy}`]);
      }
      // Пустая строка для разделения
      headerAOA.push([]);

      // 3. Создаём лист с этими строками
      const ws = XLSX.utils.aoa_to_sheet(headerAOA);

      // 4. Вставляем саму таблицу HTML ниже: origin.row = headerAOA.length
      //    sheet_add_dom вставляет содержимое tableEl начиная с указанной ячейки.
      XLSX.utils.sheet_add_dom(ws, tableEl, {
        origin: { r: headerAOA.length, c: 0 },
      });

      // 5. Переименовываем лист и добавляем в книгу
      XLSX.utils.book_append_sheet(wb, ws, props.sheetName);

      // 6. Сохраняем файл
      XLSX.writeFile(wb, props.filename);
    };

    return { exportToExcel };
  },
});
</script>

<style scoped>
.export-btn {
  padding: 0.5rem 1rem;
  background-color: var(--primary);
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-bottom: 1rem;
}

.export-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.export-btn:not(:disabled):hover {
  background-color: #005bb5;
}
</style>