<template>
  <section class="create-planogram-page" v-if="shelving">
    <h2>Создание планограммы</h2>
    <p>
      <strong>Приказ №:</strong> {{ orderId }}<br>
      <strong>Стеллаж:</strong> {{ shelving.name }}
    </p>

    <div class="editor-container">
      <!-- Список товаров -->
      <aside class="products-list">
        <h3>Товары</h3>
        <ul>
          <li
            v-for="p in products"
            :key="p.id"
            class="product-item"
            draggable="true"
            @dragstart="onDragStartFromList(p)"
          >
            {{ p.name }}
          </li>
        </ul>
      </aside>

      <!-- Матрица полок -->
      <div class="shelves">
        <div
          v-for="shelf in matrix.shelfs"
          :key="shelf.position"
          class="shelf-row"
        >
          <h4>Полка {{ shelf.position + 1 }}</h4>
          <div
            class="shelf-boxes"
            @dragover.prevent
            @drop="onDropOnShelf(shelf.position)"
          >
            <div
              v-for="(box, idx) in shelf.product_boxes"
              :key="idx"
              class="shelf-box"
              draggable="true"
              @dragstart="onDragStartInMatrix(shelf.position, idx)"
              @drop.prevent="onSwap(shelf.position, idx)"
              @dragover.prevent
              @mouseenter="hoverBox = box.product ? box : null"
              @mouseleave="hoverBox = null"
            >
              <img
                v-if="box.product"
                :src="base_url + box.product.image_url"
                :alt="box.product.name"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Таблица добавленных товаров -->
    <div class="selected-products">
      <h3>Добавленные товары</h3>
      <table class="selected-table">
        <thead>
          <tr>
            <th>Товар</th>
            <th>Количество</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="plan in matrix.products" :key="plan.product_id">
            <td>
              {{ productName(plan.product_id) }}
            </td>
            <td>
              <input
                type="number"
                min="0"
                v-model.number="plan.count"
                @change="onCountChange(plan)"
              />
            </td>
          </tr>
          <tr v-if="matrix.products.length === 0">
            <td colspan="2" class="no-data">Нет добавленных товаров</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Tooltip -->
    <div v-if="hoverBox" class="tooltip">
      <strong>{{ hoverBox.product!.name }}</strong><br />
      Количество: {{ hoverBox.planogram_product!.count }}
    </div>

    <button
      class="submit-btn"
      @click="submitPlanogram"
      :disabled="isSubmitting"
    >
      {{ isSubmitting ? 'Отправка...' : 'Отправить на согласование' }}
    </button>
  </section>

  <div v-else class="loading">Загрузка данных...</div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import type {
  Product,
  ProductBox,
  PlanogramProduct,
  ProductMatrix,
  Shelf,
  Shelving,
  AddPlanogramRequest,
} from '@/types';
import { get_shelving } from '@/api/shelvings';
import { get_products } from '@/api/products';
import { add_planogram } from '@/api/planograms';
import { base_url } from '@/api/config';
import { authStore } from '@/auth/store';

export default defineComponent({
  name: 'CreatePlanogramView',
  setup() {
    const route = useRoute();
    const router = useRouter();
    const orderId = route.params.order_id as string;
    const shelvingId = route.params.shelving_id as string;

    const products = ref<Product[]>([]);
    const shelving = ref<Shelving | null>(null);
    const matrix = ref<ProductMatrix>({ products: [], shelfs: [] });

    const dragSource = ref<any>(null);
    const hoverBox = ref<ProductBox | null>(null);
    const isSubmitting = ref(false);

    function makeBoxes(n: number) {
      return Array.from({ length: n }).map((_, i) => ({
        product_id: '',
        pos_x: i,
        is_empty: true,
        is_incorrect_position: false,
      } as ProductBox));
    }

    onMounted(async () => {
      shelving.value = await get_shelving(shelvingId);
      products.value = await get_products();
      const count = shelving.value?.shelves_count || 0;
      matrix.value.shelfs = Array.from({ length: count }).map((_, i) => ({
        position: i,
        product_boxes: makeBoxes(10),
      }));
    });

    // drag & drop (как было)
    function onDragStartFromList(p: Product) {
      dragSource.value = { fromList: true, product: p };
    }
    function onDragStartInMatrix(shelf: number, idx: number) {
      const box = matrix.value.shelfs[shelf].product_boxes[idx];
      if (!box.is_empty) {
        dragSource.value = { fromList: false, shelf, idx };
      }
    }
    function onDropOnShelf(shelf: number) {
      if (!dragSource.value) return;
      const row = matrix.value.shelfs[shelf];
      let idx = row.product_boxes.findIndex((b) => b.is_empty);
      if (idx < 0) {
        idx = row.product_boxes.length;
        row.product_boxes.push(...makeBoxes(1));
      }
      place(shelf, idx, dragSource.value.product);
      dragSource.value = null;
    }
    function onSwap(shelf: number, idx: number) {
      if (!dragSource.value) return;
      const row = matrix.value.shelfs[shelf].product_boxes;
      if (dragSource.value.fromList) {
        place(shelf, idx, dragSource.value.product);
      } else {
        const srcRow =
          matrix.value.shelfs[dragSource.value.shelf].product_boxes;
        const tmp = row[idx];
        row[idx] = srcRow[dragSource.value.idx];
        srcRow[dragSource.value.idx] = tmp;
      }
      dragSource.value = null;
    }

    // кладём товар в ячейку и увеличиваем plan.count
    function place(shelf: number, idx: number, p: Product) {
      const row = matrix.value.shelfs[shelf];
      while (row.product_boxes.length <= idx) {
        row.product_boxes.push(...makeBoxes(1));
      }
      let plan = matrix.value.products.find((x) => x.product_id === p.id);
      if (!plan) {
        plan = { product_id: p.id!, count: 0 } as PlanogramProduct;
        matrix.value.products.push(plan);
      }
      row.product_boxes[idx] = {
        product_id: p.id!,
        pos_x: idx,
        is_empty: false,
        product: p,
        is_incorrect_position: false,
        planogram_product: plan,
      } as ProductBox;

      // синхронизуем count через количество заполненных ячеек
      plan.count = matrix.value.shelfs
        .flatMap((s) => s.product_boxes)
        .filter((b) => !b.is_empty && b.product_id === p.id).length;
    }

    // когда пользователь вручную меняет количество в таблице
    function onCountChange(plan: PlanogramProduct) {
      // ничего дополнительно не делаем —
      // при сабмите возьмётся именно plan.count
    }

    // вспомогалки
    const productName = (id: string) => {
      const p = products.value.find((x) => x.id === id);
      return p ? p.name : id;
    };

    function hasGaps() {
      return matrix.value.shelfs.some((shelf) => {
        const arr = shelf.product_boxes;
        let filled = false;
        for (let b of arr) {
          if (!b.is_empty) filled = true;
          else if (filled) return true;
        }
        return arr.some((b) => b.is_empty);
      });
    }

    async function submitPlanogram() {
      if (hasGaps()) {
        const shelves: Shelf[] = [];
        for (const shelf of matrix.value.shelfs) {
          const new_shelf: Shelf = {
            position: shelf.position,
            product_boxes: [],
          };
          for (const box of shelf.product_boxes) {
            if (!box.is_empty) {
              new_shelf.product_boxes.push({
                product_id: box.product_id,
                pos_x: box.pos_x,
                is_empty: false,
                is_incorrect_position: false,
              } as ProductBox);
            }
          }
          shelves.push(new_shelf);
        }
        matrix.value.shelfs = shelves;
      }
      isSubmitting.value = true;
      try {
        await add_planogram({
          order_id: orderId,
          author_id: authStore.user!.id!,
          shelving_id: shelvingId,
          product_matrix: matrix.value,
        } as AddPlanogramRequest);
        router.push({ name: 'AllOrders' });
      } finally {
        isSubmitting.value = false;
      }
    }

    return {
      base_url,
      orderId,
      shelving,
      products,
      matrix,
      hoverBox,
      isSubmitting,
      onDragStartFromList,
      onDragStartInMatrix,
      onDropOnShelf,
      onSwap,
      onCountChange,
      productName,
      submitPlanogram,
    };
  },
});
</script>

<style scoped>
.create-planogram-page {
  padding: 1.5rem;
}

.editor-container {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.products-list {
  width: 220px;
  background: var(--surface);
  padding: 1rem;
  border-radius: 8px;
}

.product-item {
  padding: 0.5rem;
  margin-bottom: 0.25rem;
  background: var(--bg);
  cursor: grab;
  border: 1px solid var(--border);
  border-radius: 4px;
}

.shelves {
  flex: 1;
}

.shelf-row {
  margin-bottom: 1.25rem;
}

.shelf-boxes {
  display: flex;
  border: 1px solid var(--border);
  border-radius: 4px;
  overflow-x: auto;
}

.shelf-box {
  width: 60px;
  height: 60px;
  border-right: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
  transition: outline 0.2s, background 0.2s;
}

.shelf-box:last-child {
  border-right: none;
}

.shelf-box img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.tooltip {
  position: fixed;
  top: 50px;
  right: 50px;
  background: var(--surface);
  border: 1px solid var(--border);
  padding: 0.5rem;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.selected-products {
  margin-bottom: 1.5rem;
}

.selected-products h3 {
  margin-bottom: 0.5rem;
  color: var(--primary);
}

.selected-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--surface);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  overflow: hidden;
}

.selected-table th,
.selected-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border);
  text-align: left;
}

.selected-table th {
  background: var(--bg);
  font-weight: 600;
  color: var(--text-secondary);
}

.selected-table input[type='number'] {
  width: 80px;
  padding: 0.25rem;
  border: 1px solid var(--border);
  border-radius: 4px;
}

.no-data {
  text-align: center;
  padding: 1rem;
  color: var(--text-secondary);
}

.submit-btn {
  padding: 0.75rem 1.5rem;
  background: var(--primary);
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}
</style>