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
              @dragstart="onDragStart(p)"
            >
              {{ p.name }}
            </li>
          </ul>
        </aside>
  
        <!-- Полки -->
        <div class="shelves">
          <div
            v-for="shelf in matrix.shelfs"
            :key="shelf.position"
            class="shelf-row"
          >
            <h4>Полка {{ shelf.position }}</h4>
            <div
              class="shelf-boxes"
              @dragover.prevent
            >
              <div
                v-for="(box, idx) in shelf.product_boxes"
                :key="idx"
                class="shelf-box"
                @drop="onDrop(shelf.position, idx)"
              >
                <img
                  v-if="!box.is_empty && box.planogram_product?.product"
                  :src="box.planogram_product.product.imageUrl"
                  :alt="box.planogram_product.product.name"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
  
      <button class="submit-btn" @click="submitPlanogram" :disabled="isSubmitting">
        {{ isSubmitting ? 'Отправка...' : 'Отправить на согласование' }}
      </button>
    </section>

    <div v-else class="loading">Загрузка деталей...</div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, onMounted } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import axios from 'axios';
  import { get_shelving } from '@/api/shelvings';
  import { get_products } from '@/api/products';
  import type {
    Product,
    PlanogramProduct,
    ProductBox,
    Shelf,
    Shelving,
    ProductMatrix,
    AddPlanogramRequest,
  } from '@/types';
  
  export default defineComponent({
    name: 'CreatePlanogramView',
    setup() {
      const route = useRoute();
      const router = useRouter();
      const orderId = route.params.order_id as string;
      const shelvingId = route.params.shelving_id as string;

      const products = ref<Product[]>([]);
      const shelving = ref<Shelving>(null);
  
      const matrix = ref<ProductMatrix>({
        products: [],
        shelfs: [],
      });
  
      const draggedProduct = ref<Product | null>(null);
      const isSubmitting = ref(false);
  
      onMounted(async () => {
        shelving.value = await get_shelving(shelvingId);
        products.value = await get_products();        

        const shelfs = [];
        for (let i = 0; i < shelving.value.shelves_count; i++) {
            shelfs.push({
                position: i,
                product_boxes: []
            })
        }

        matrix.value = {
          products: [],
          shelfs: shelfs,
        };

        console.log(products.value);
      });
  
      const onDragStart = (p: Product) => {
        draggedProduct.value = p;
      };
  
      // drop — создаём или обновляем ProductBox
      const onDrop = (shelfPos: number, boxIndex: number) => {
        if (!draggedProduct.value) return;
  
        const shelf = matrix.value.shelfs.find(s => s.position === shelfPos)!;
        const existingBox = shelf.product_boxes[boxIndex];
  
        // создаём PlanogramProduct, если его ещё нет
        let planProd = matrix.value.products.find(
          mp => mp.product_id === draggedProduct.value!.id
        );
        if (!planProd) {
          planProd = {
            product_id: draggedProduct.value.id!,
            count: 0,
            // id и product заполним на бэке или позже
          } as PlanogramProduct;
          matrix.value.products.push(planProd);
        }
  
        // создаём/перезаписываем ProductBox
        const newBox: ProductBox = {
          product_id: draggedProduct.value.id!,
          pos_x: boxIndex,
          is_empty: false,
          planogram_product: planProd,
        };
        shelf.product_boxes[boxIndex] = newBox;
  
        // увеличим count, если хотим считать кол‑во на полке
        planProd.count = shelf.product_boxes.filter(b => !b.is_empty && b.product_id === planProd!.product_id).length;
  
        // сбросим drag
        draggedProduct.value = null;
      };
  
      const submitPlanogram = async () => {
        isSubmitting.value = true;
        try {
          const payload: AddPlanogramRequest = {
            order_id: orderId,
            author_id: 'current-user-id', // замените на реальный
            shelving_id: shelvingId,
            product_matrix: matrix.value,
          };
          await axios.post('/api/planograms', payload);
          // после успеха — редирект обратно на список приказов
          router.push({ name: 'AllOrders' });
        } catch (err) {
          console.error('Ошибка отправки планограммы', err);
          alert('Не удалось отправить планограмму.');
        } finally {
          isSubmitting.value = false;
        }
      };
  
      return {
        orderId,
        shelvingId,
        shelving,
        products,
        matrix,
        isSubmitting,
        onDragStart,
        onDrop,
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
  
  /* Список товаров */
  .products-list {
    width: 200px;
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
  
  /* Полки */
  .shelves {
    flex: 1;
  }
  
  .shelf-row {
    margin-bottom: 1rem;
  }
  
  .shelf-row h4 {
    margin-bottom: 0.5rem;
  }
  
  .shelf-boxes {
    display: flex;
    border: 1px solid var(--border);
    border-radius: 4px;
    overflow: hidden;
  }
  
  .shelf-box {
    width: 60px;
    height: 60px;
    border-right: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .shelf-box:last-child {
    border-right: none;
  }
  
  .shelf-box img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
  }
  
  /* Кнопка отправки */
  .submit-btn {
    padding: 0.75rem 1.5rem;
    background: var(--primary);
    color: #fff;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 600;
  }
  
  .submit-btn:disabled {
    background: #aaa;
    cursor: not-allowed;
  }
  </style>
  