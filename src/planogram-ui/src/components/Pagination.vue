<template>
    <div class="pagination">
      <button :disabled="page <= 1" @click="emitPage(page - 1)">Назад</button>
      <span>Страница {{ page }} из {{ totalPages }}</span>
      <button :disabled="page >= totalPages" @click="emitPage(page + 1)">Вперёд</button>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, computed } from 'vue';
  
  export default defineComponent({
    name: 'Pagination',
    props: {
      page: { type: Number, required: true },
      total: { type: Number, required: true },
      pageSize: { type: Number, required: true },
    },
    emits: ['update:page'],
    setup(props, { emit }) {
      const totalPages = computed(() =>
        Math.ceil(props.total / props.pageSize)
      );
  
      const emitPage = (newPage: number) => {
        emit('update:page', newPage);
      };
  
      return { totalPages, emitPage };
    },
  });
  </script>
  
  <style scoped>
  .pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin-top: 1.5rem;
  }
  
  .pagination button {
    padding: 0.5rem 1rem;
    border: none;
    background-color: var(--bg-button);
    color: var(--text-primary);
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.2s;
  }
  
  .pagination button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
  </style>
  