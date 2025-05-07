<template>
    <section class="edit-planogram-page" v-if="shelving">
      <h2>Редактирование планограммы</h2>
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
                @mouseenter="hoverBox = box"
                @mouseleave="hoverBox = null"
              >
                <img
                  v-if="box.planogram_product?.product"
                  :src="base_url + box.planogram_product.product.image_url"
                  :alt="box.planogram_product.product.name"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Tooltip -->
      <div v-if="hoverBox && hoverBox.planogram_product?.product" class="tooltip">
        <strong>{{ hoverBox.planogram_product.product.name }}</strong><br>
        Количество: {{ hoverBox.planogram_product.count }}
      </div>
  
      <button
        class="submit-btn"
        @click="submitEdits"
        :disabled="isSubmitting"
      >
        {{ isSubmitting ? 'Сохранение...' : 'Сохранить изменения' }}
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
    Shelving,
    ApprovePlanogramRequest,
    Planogram,
    AddPlanogramRequest
  } from '@/types';
  import { get_shelving } from '@/api/shelvings';
  import { get_products } from '@/api/products';
  import { get_planogram, add_planogram } from '@/api/planograms';
  import { base_url } from '@/api/config';
  import { authStore } from '@/auth/store';

  export default defineComponent({
    name: 'EditPlanogramView',
    setup() {
      const route = useRoute();
      const router = useRouter();
      const orderId = route.params.order_id as string;
      const planogramId = route.params.planogram_id as string;
      const shelvingId = ref<string>("");
  
      const products = ref<Product[]>([]);
      const shelving = ref<Shelving | null>(null);
      const matrix = ref<ProductMatrix>({ products: [], shelfs: [] });
      const hoverBox = ref<ProductBox | null>(null);
      const isSubmitting = ref(false);
  
      const makeBoxes = (n: number) =>
        Array.from({ length: n }).map((_, i) =>
          ({ product_id: '', pos_x: i, is_empty: true, is_incorrect_position: false } as ProductBox)
        );
  
      onMounted(async () => {
        console.log(planogramId)
        console.log(orderId)
        const plan: Planogram | null = await get_planogram(orderId, planogramId);
        shelvingId.value = plan!.shelving.id!
        shelving.value = await get_shelving(shelvingId.value);
        products.value = await get_products();
  
        // Инициализация пустой матрицы по количеству полок
        const count = shelving.value?.shelves_count || 0;
        matrix.value.shelfs = Array.from({ length: count }).map((_, i) => ({
          position: i,
          product_boxes: makeBoxes(10)
        }));
  
        if (plan) {
          // Переносим продуктовый список
          matrix.value.products = plan.product_matrix.products;
          // Заполнение боксов по данным
          plan.product_matrix.shelfs.forEach(shelfData => {
            const row = matrix.value.shelfs[shelfData.position];
            // Расширяем, если нужно
            if (row.product_boxes.length < shelfData.product_boxes.length) {
              row.product_boxes.push(...makeBoxes(
                shelfData.product_boxes.length - row.product_boxes.length
              ));
            }
            shelfData.product_boxes.forEach((boxData, idx) => {
              row.product_boxes[idx] = {
                ...boxData,
                // Если нужно, отметим is_empty по флагу:
                is_empty: boxData.is_empty,
              };
            });
          });
        }
      });
  
      // Drag & Drop логика как в создании
      const dragSource = ref<any>(null);
      function onDragStartFromList(p: Product) {
        dragSource.value = { fromList: true, product: p };
      }
      function onDragStartInMatrix(shelf: number, idx: number) {
        const box = matrix.value.shelfs[shelf].product_boxes[idx];
        if (!box.is_empty) dragSource.value = { fromList: false, shelf, idx, box };
      }
      function onDropOnShelf(shelf: number) {
        if (!dragSource.value) return;
        const row = matrix.value.shelfs[shelf];
        let idx = row.product_boxes.findIndex(b => b.is_empty);
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
          const srcRow = matrix.value.shelfs[dragSource.value.shelf].product_boxes;
          [row[idx], srcRow[dragSource.value.idx]] = [srcRow[dragSource.value.idx], row[idx]];
        }
        dragSource.value = null;
      }
      function place(shelf: number, idx: number, p: Product) {
        const row = matrix.value.shelfs[shelf];
        while (row.product_boxes.length <= idx) row.product_boxes.push(...makeBoxes(1));
        let planProd = matrix.value.products.find(x => x.product_id === p.id);
        if (!planProd) {
          planProd = { product_id: p.id!, count: 0 } as PlanogramProduct;
          matrix.value.products.push(planProd);
        }
        row.product_boxes[idx] = {
          product_id: p.id!,
          pos_x: idx,
          is_empty: false,
          is_incorrect_position: false,
          planogram_product: planProd,
        };
        planProd.count = row.product_boxes.filter(b => !b.is_empty && b.product_id === p.id).length;
      }
  
      async function submitEdits() {
        isSubmitting.value = true;
        try {
          await add_planogram({
            order_id: orderId,
            author_id: authStore.user!.id,
            shelving_id: shelvingId.value,
            planogram_id: planogramId,
            product_matrix: matrix.value,
          } as AddPlanogramRequest );
          router.push({ name: 'AllOrders' });
        } finally {
          isSubmitting.value = false;
        }
      }
  
      return {
        base_url, orderId, shelving, products, matrix,
        hoverBox, isSubmitting,
        onDragStartFromList, onDragStartInMatrix,
        onDropOnShelf, onSwap,
        submitEdits
      };
    }
  });
  </script>
  
  <style scoped>
  .create-planogram-page,
  .edit-planogram-page {
    padding: 1.5rem;
  }
  .editor-container {
    display: flex;
    gap: 2rem;
    margin-bottom: 1.5rem;
  }
  /* (остальные стили скопируйте из вашей create-страницы) */
  </style>
  