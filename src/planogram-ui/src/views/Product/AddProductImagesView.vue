<template>
    <section class="add-images-page">
      <h2 class="title">Добавить изображения для товара</h2>
  
      <form @submit.prevent="onSubmit" class="form card">
        <!-- Выбор товара -->
        <div class="form-group">
          <label for="product">Товар</label>
          <select id="product" v-model="selectedProductId" required>
            <option value="" disabled>— Выберите товар —</option>
            <option v-for="p in products" :key="p.id" :value="p.id">
              {{ p.name }}
            </option>
          </select>
        </div>
  
        <!-- Загрузка файлов -->
        <div class="form-group">
          <label for="images">Фотографии</label>
          <input
            id="images"
            type="file"
            multiple
            accept="image/*"
            @change="onFilesChange"
            required
          />
        </div>
  
        <!-- Превью -->
        <div class="previews" v-if="previews.length">
          <h3>Предпросмотр</h3>
          <div class="preview-list">
            <div
              v-for="(src, idx) in previews"
              :key="idx"
              class="preview-wrapper"
            >
              <img :src="src" class="preview-img" />
            </div>
          </div>
        </div>
  
        <!-- Кнопка отправки -->
        <button type="submit" class="btn" :disabled="isUploading">
          {{ isUploading ? 'Загрузка...' : 'Загрузить' }}
        </button>
      </form>
    </section>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, onMounted } from 'vue';
  import type { Product } from '@/types';
  import { get_products } from '@/api/products';
  import { load_product_imgs } from '@/api/products';
  
  export default defineComponent({
    name: 'AddProductImagesView',
    setup() {
      const products = ref<Product[]>([]);
      const selectedProductId = ref<string>('');
      const files = ref<File[]>([]);
      const previews = ref<string[]>([]);
      const isUploading = ref(false);
  
      // Подгружаем список товаров
      onMounted(async () => {
        try {
            products.value = await get_products()
        } catch (e) {
          console.error('Ошибка загрузки товаров', e);
        }
      });
  
      const onFilesChange = (e: Event) => {
        const input = e.target as HTMLInputElement;
        if (!input.files) return;
        files.value = Array.from(input.files);
        previews.value = files.value.map((f) => URL.createObjectURL(f));
      };
  
      const onSubmit = async () => {
        if (!selectedProductId.value || !files.value.length) return;
        isUploading.value = true;
  
        const formData = new FormData();
        files.value.forEach((f) => formData.append('image_files', f));
  
        try {
          const message = await load_product_imgs(
            selectedProductId.value,
            formData
          );
          alert(message);
          // сброс формы
          selectedProductId.value = '';
          files.value = [];
          previews.value = [];
        } catch (e: any) {
          console.error('Ошибка при загрузке изображений', e);
          alert(e.response?.data?.message || 'Ошибка загрузки');
        } finally {
          isUploading.value = false;
        }
      };
  
      return {
        products,
        selectedProductId,
        previews,
        isUploading,
        onFilesChange,
        onSubmit,
      };
    },
  });
  </script>
  
  <style scoped>
  .add-images-page {
    padding: 2rem;
    max-width: 700px;
    margin: auto;
  }
  
  .title {
    font-size: 1.75rem;
    margin-bottom: 1.5rem;
    color: var(--primary);
    text-align: center;
  }
  
  .card {
    background: var(--surface);
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
    margin-bottom: 1.25rem;
  }
  
  .form-group label {
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: var(--text-secondary);
  }
  
  .form-group select,
  .form-group input[type='file'] {
    padding: 0.5rem;
    border: 1px solid var(--border);
    border-radius: 4px;
    font-size: 1rem;
  }
  
  .previews {
    margin-bottom: 1.25rem;
  }
  
  .preview-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
  }
  
  .preview-wrapper {
    width: 120px;
    height: 120px;
    border: 1px solid var(--border);
    border-radius: 6px;
    overflow: hidden;
    background: var(--bg);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .preview-img {
    max-width: 100%;
    max-height: 100%;
    object-fit: cover;
  }
  
  .btn {
    display: block;
    width: 100%;
    padding: 0.75rem;
    font-size: 1rem;
    font-weight: 600;
    background: var(--primary);
    color: #fff;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: opacity 0.2s;
  }
  
  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  </style>
  