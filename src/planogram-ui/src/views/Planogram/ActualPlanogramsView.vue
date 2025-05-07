<template>
    <section class="planograms-page">
      <h2>Список стеллажей и планограмм</h2>
  
      <table class="shelves-table">
        <thead>
          <tr>
            <th>Название стеллажа</th>
            <th>Количество полок</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="s in data"
            :key="s.shelving.id"
            class="shelves-row"
            @click="goToPlanograms(s.planogram_id, s.order_id)"
          >
            <td>{{ s.shelving.name }}</td>
            <td>{{ s.shelving.shelves_count }}</td>
          </tr>
          <tr v-if="shelves.length === 0">
            <td colspan="2" class="no-data">Нет стеллажей</td>
          </tr>
        </tbody>
      </table>
    </section>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import type { Shelving, Planogram, PlanogramsResponse } from "@/types"
  import { get_shelvings } from "@/api/shelvings"
  import { get_actual_planograms } from '@/api/planograms';

  interface ShelvingPlanogramOrder {
    shelving: Shelving,
    order_id: string,
    planogram_id: string
  }

  export default defineComponent({
    name: 'PlanogramsListView',
    setup() {
      const shelves = ref<Shelving[]>([]);
      const planogram_data = ref<PlanogramsResponse|null>(null);
      const data = ref<ShelvingPlanogramOrder[]>()
      const router = useRouter();
  
      onMounted(async () => {
        try {
          shelves.value = await get_shelvings()
          planogram_data.value = await get_actual_planograms()
          data.value = set_planogram(shelves.value, planogram_data.value)
        } catch (e) {
          console.error('Ошибка загрузки данных', e);
          shelves.value = [];
        }
      });
  
      const set_planogram = (shelvings: Shelving[], data: PlanogramsResponse) => {
        const actual_planograms_dict = []
        for (const shelving of shelvings){
            for (const d of data.planogram_data){
                if (d.shelving_id === shelving.id){
                    const shelf_planogram = {
                        order_id: d.order_id,
                        planogram_id: d.planogram_id,
                        shelving: shelving
                    }
                    actual_planograms_dict.push(shelf_planogram)
                }
            }
        }
        return actual_planograms_dict
      }

      const goToPlanograms = (planogram_id: string, order_id: string) => {
        router.push({ name: 'PlanogramDetail', params: { planogram_id: planogram_id, order_id: order_id } });
      };
      return { shelves, data, goToPlanograms };
    },
  });
  </script>
  
  <style scoped>
  .planograms-page {
    padding: 2rem;
    max-width: 800px;
    margin: auto;
  }
  .shelves-table {
    width: 100%;
    border-collapse: collapse;
    background: var(--surface);
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    border-radius: 8px;
    overflow: hidden;
  }
  .shelves-table th,
  .shelves-table td {
    padding: 0.75rem 1rem;
    text-align: left;
    border-bottom: 1px solid var(--border);
  }
  .shelves-table th {
    background: var(--bg);
    font-weight: 600;
    color: var(--text-secondary);
  }
  .shelves-row {
    cursor: pointer;
    transition: background 0.2s;
  }
  .shelves-row:hover {
    background: var(--bg);
  }
  .no-data {
    text-align: center;
    color: var(--text-secondary);
    padding: 1.5rem;
  }
  </style>  