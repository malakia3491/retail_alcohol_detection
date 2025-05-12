<template>
  <section class="realogram-detail" v-if="realogram && store && shelving">
    <button class="back-btn" @click="goBack">← Назад</button>

    <!-- Заголовок -->
    <h2>Реалограмма {{ formatDateTime(realogram.create_date) }}</h2>
    <div class="meta-panel" v-if="realogram && store && shelving">
        <!-- Первая строка: дата, магазин, стеллаж -->
        <div class="meta-row">
        <div><strong>Магазин:</strong> {{ store.name }}</div>
        <div><strong>Стеллаж:</strong> {{ shelving.name }}</div>
        </div>
        <!-- Вторая строка: метрики -->
        <div class="meta-row metrics-row">
        <div><strong>Соответствие:</strong> {{ realogram.accordance.toFixed(2) }}%</div>
        <div><strong>Пустых ячеек:</strong> {{ realogram.empties_count }}</div>
        </div>
    </div>

    <!-- Картинка + overlay -->
    <div class="image-container">
      <img
        :src="base_url + realogram.img_src"
        @load="onImageLoad"
        alt="Realogram"
        ref="imgRef"
      />
      <svg
        v-if="boxes.length"
        class="overlay"
        :width="imgSize.width"
        :height="imgSize.height"
      >
        <rect
          v-for="(b, idx) in boxes"
          :key="idx"
          :x="b.x" :y="b.y"
          :width="b.w" :height="b.h"
          :class="{
            empty: b.is_empty,
            incorrect: b.is_incorrect_position
          }"
        />
      </svg>
    </div>
  </section>

  <div v-else class="loading">Загрузка данных...</div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { get_stores } from '@/api/stores';
import { getRealogram } from '@/api/realograms';
import { get_shelving } from '@/api/shelvings';
import { base_url } from '@/api/config';
import { formatDateTime } from '@/utils/date_utils';
import type { Realogram, Store, Shelving } from '@/types';

export default defineComponent({
  name: 'RealogramDetail',
  setup() {
    const route = useRoute();
    const router = useRouter();

    const storeId = route.params.store_id as string;
    const realogramId = route.params.id as string;

    const realogram = ref<Realogram | null>(null);
    const store = ref<Store | null>(null);
    const shelving = ref<Shelving | null>(null);

    const imgRef = ref<HTMLImageElement>();
    const imgSize = reactive({ width: 0, height: 0 });
    const boxes = reactive<Array<{
      x: number; y: number; w: number; h: number;
      is_empty: boolean; is_incorrect_position: boolean;
    }>>([]);

    const goBack = () => router.back();

    const fetchAll = async () => {
      try {
        // 1. Realogram
        const r = await getRealogram(storeId, realogramId);
        realogram.value = r;

        // 2. Магазины -> находим наш
        const allStores = await get_stores();
        store.value = allStores.find(s => s.id === storeId) || null;

        // 3. Стеллаж
        shelving.value = await get_shelving(r.shelving_id);
      } catch (e) {
        console.error('Ошибка загрузки данных:', e);
      }
    };

    const onImageLoad = () => {
      if (!imgRef.value || !realogram.value) return;
      const img = imgRef.value;
      const { naturalWidth, naturalHeight, width, height } = img;
      imgSize.width = width;
      imgSize.height = height;
      boxes.splice(0, boxes.length);

      realogram.value.product_matrix.shelfs.forEach(shelf =>
        shelf.product_boxes.forEach(box => {
          if (!box.cords || box.cords.length !== 4) return;
          const [x1, y1, x2, y2] = box.cords;
          const x = (x1 / naturalWidth) * width;
          const y = (y1 / naturalHeight) * height;
          const w = ((x2 - x1) / naturalWidth) * width;
          const h = ((y2 - y1) / naturalHeight) * height;
          boxes.push({
            x, y, w, h,
            is_empty: !!box.is_empty,
            is_incorrect_position: !!box.is_incorrect_position,
          });
        })
      );
    };

    onMounted(fetchAll);

    return {
      realogram,
      store,
      shelving,
      imgRef,
      imgSize,
      boxes,
      base_url,
      formatDateTime,
      onImageLoad,
      goBack,
    };
  },
});
</script>

<style scoped>

.meta-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: var(--surface);
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
}

/* Каждая строка внутри meta-panel */
.meta-row {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.metrics-row {
  border-top: 1px solid var(--border);
  padding-top: 0.75rem;
  color: var(--text-primary);
}

.realogram-detail {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
}

.back-btn {
  background: none;
  border: none;
  color: var(--primary);
  font-size: 1rem;
  cursor: pointer;
  margin-bottom: 1rem;
}

.meta-panel {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  background: var(--surface);
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  margin-bottom: 2rem;
}

.meta-panel div {
  font-size: 1rem;
  color: var(--text-primary);
}

.image-container {
  position: relative;
  background: var(--surface);
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.image-container img {
  display: block;
  max-width: 100%;
  border-radius: 4px;
}

.overlay {
  position: absolute;
  top: 1rem;
  left: 1rem;
}

.overlay rect {
  fill: transparent;
  stroke-width: 2;
}

.overlay rect.empty {
  stroke: red;
}

.overlay rect.incorrect {
  stroke: purple;
}

.overlay rect:not(.empty):not(.incorrect) {
  stroke: green;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}
</style>