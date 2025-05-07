<template>
    <section class="realograms-page">
      <h2 v-if="authStore.user?.store">
        Актуальные реалограммы — {{ authStore.user.store.name }}
      </h2>
      <h2 v-else>Выберите магазин</h2>
  
      <!-- Список магазинов -->
      <table v-if="!authStore.user?.store" class="stores-table">
        <thead>
          <tr><th>Магазин</th></tr>
        </thead>
        <tbody>
          <tr
            v-for="st in stores"
            :key="st.id"
            @click="selectStore(st)"
            class="store-row"
          >
            <td>{{ st.name }}</td>
          </tr>
        </tbody>
      </table>
  
      <!-- Реалограммы -->
      <div v-else>
        <div
          v-for="real in realograms"
          :key="real.id"
          class="realogram-block"
        >
          <!-- Метаданные -->
          <div class="realogram-header">
            <div><strong>Дата:</strong> {{ formatDate(real.create_date) }}</div>
            <div><strong>Соответствие:</strong> {{ real.accordance }}%</div>
            <div><strong>Пустых ячеек:</strong> {{ real.empties_count }}</div>
          </div>
  
          <!-- Изображение + оверлей -->
          <div class="image-container">
            <img
              :src="base_url + real.img_src"
              @load="onImageLoad($event, real.id!)"
              alt="realogram"
            />
            <svg
              v-if="boxes[real.id!]?.length"
              class="overlay"
              :width="imgSizes[real.id!].width"
              :height="imgSizes[real.id!].height"
            >
              <rect
                v-for="(b, idx) in boxes[real.id!]"
                :key="idx"
                :x="b.x" :y="b.y"
                :width="b.w" :height="b.h"
                :class="{ empty: b.is_empty, incorrect: b.is_incorrect_position }"
              />
            </svg>
          </div>
        </div>
      </div>
    </section>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, reactive, onMounted } from 'vue';
  import { authStore } from '@/auth/store';
  import { get_actual_realograms } from '@/api/realograms';
  import { base_url } from '@/api/config';
  import { Store, Realogram } from '@/types';
  import { get_stores } from '@/api/stores';
  import { formatDate } from '@/utils/date_utils';
  
  export default defineComponent({
    name: 'ActualRealogramsView',
    setup() {
      const stores = ref<Store[]>([]);
      const realograms = ref<Realogram[]>([]);
      const imgSizes = reactive<Record<string,{width:number;height:number}>>({});
      const boxes = reactive<Record<string,Array<{
        x:number; y:number; w:number; h:number;
        is_empty:boolean; is_incorrect_position:boolean
      }>>>({});
  
      // Загрузка магазинов
      const loadStores = async () => {
        stores.value = await get_stores();
      };
  
      // Загрузка реалограмм
      const loadRealograms = async () => {
        const store = authStore.user?.store;
        if (!store) return;
        realograms.value = await get_actual_realograms(store.id);
        console.log()
      };
  
      onMounted(async () => {
        await authStore.checkAuth();
        if (authStore.user?.store) {
          await loadRealograms();
        } else {
          await loadStores();
        }
      });
  
      // Выбор магазина
      const selectStore = async (st: Store) => {
        authStore.user!.store = st;
        await loadRealograms();
      };

      // Обработка загрузки изображения
      const onImageLoad = (e: Event, id: string) => {
        const img = e.target as HTMLImageElement;
        const { naturalWidth, naturalHeight, width, height } = img;
        imgSizes[id] = { width, height };
        boxes[id] = [];
  
        const real = realograms.value.find(r => r.id === id)!;
        console.log('Realogram', id, 'coords raw:', real.product_matrix.shelfs);
        real.product_matrix.shelfs.forEach(shelf => {
          shelf.product_boxes.forEach(box => {
            if (!box.cords || box.cords.length !== 4) return;
            const [x1,y1,x2,y2] = box.cords;
            const x = x1 / naturalWidth * width;
            const y = y1 / naturalHeight * height;
            const w = (x2 - x1) / naturalWidth * width;
            const h = (y2 - y1) / naturalHeight * height;
            boxes[id].push({
              x, y, w, h,
              is_empty: !!box.is_empty,
              is_incorrect_position: !!box.is_incorrect_position
            });
          });
        });
      };
  
      return {
        authStore,
        stores,
        realograms,
        selectStore,
        formatDate,
        base_url,
        imgSizes,
        boxes,
        onImageLoad,
      };
    }
  });
  </script>
  
  <style scoped>
  .realograms-page {
    padding: 2rem;
  }
  .stores-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 2rem;
  }
  .stores-table th,
  .stores-table td {
    border: 1px solid var(--border);
    padding: 0.75rem;
    text-align: left;
  }
  .store-row {
    cursor: pointer;
    background: #fff;
    transition: background 0.2s;
  }
  .store-row:hover {
    background: var(--bg);
  }
  .realogram-block {
    background: var(--surface);
    padding: 1rem;
    margin-bottom: 2rem;
    border-radius: 6px;
  }
  .realogram-header {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 1rem;
  }
  .image-container {
    position: relative;
    display: inline-block;
  }
  .image-container img {
    display: block;
    max-width: 100%;
  }
  .overlay {
    position: absolute;
    top: 0;
    left: 0;
  }
  .overlay rect {
    fill: transparent;
    stroke-width: 2;
    stroke: green;
  }
  .overlay rect.empty {
    stroke: red;
  }
  .overlay rect.incorrect {
    stroke: purple;
  }
  </style>
  