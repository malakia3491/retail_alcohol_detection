<template>
    <section class="planogram-detail-page" v-if="planogram">
      <h2>Планограмма №{{ planogram.id }}</h2>
  
      <div class="detail-info">
        <div class="info-row">
          <span class="label">Автор:</span>
          <span class="value">{{ planogram.author.name }}</span>
        </div>
        <div class="info-row">
          <span class="label">Стеллаж:</span>
          <span class="value">{{ planogram.shelving.name }}</span>
        </div>
        <div class="info-row">
          <span class="label">Дата создания:</span>
          <span class="value">{{ formatDate(planogram.create_date) }}</span>
        </div>
        <div class="info-row" v-if="planogram.approver">
          <span class="label">Согласовал:</span>
          <span class="value">{{ planogram.approver.name }}</span>
        </div>
        <div class="info-row" v-if="planogram.approval_date">
          <span class="label">Дата согласования:</span>
          <span class="value">{{ formatDate(planogram.approval_date) }}</span>
        </div>
      </div>
  
      <h3>Матрица продуктов</h3>
      <div class="matrix">
        <div
          v-for="shelf in planogram.product_matrix.shelfs"
          :key="shelf.position"
          class="shelf-row"
        >
          <h4>Полка {{ shelf.position + 1 }}</h4>
          <div class="shelf-boxes">
            <div
              v-for="box in shelf.product_boxes"
              :key="box.pos_x"
              class="shelf-box"
            >
              <img
                v-if="!box.is_empty && box.planogram_product?.product"
                :src="base_url + box.planogram_product.product.image_url"
                :alt="box.planogram_product.product.name"
              />
            </div>
          </div>
        </div>
      </div>
  
      <div class="actions">
        <button
          v-if="!planogram.approver"
          class="btn-approve"
          @click="approve"
          :disabled="isProcessing"
        >
          {{ isProcessing ? 'Согласование...' : 'Согласовать' }}
        </button>
        <button
          v-else
          class="btn-revoke"
          @click="revoke"
          :disabled="isProcessing"
        >
          {{ isProcessing ? 'Отмена...' : 'Отменить согласование' }}
        </button>
        <button
         class="btn-edit"
         @click="edit"
         :disabled="isProcessing"
         >
         Редактировать
         </button>
      </div>
    </section>
  
    <div v-else class="loading">Загрузка данных...</div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, onMounted, onBeforeUnmount } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import type { Planogram } from '@/types';
  import { get_planogram } from '@/api/planograms';
  import { unapprove_planogram } from '@/api/planograms';
  import { approve_planogram } from '@/api/planograms';
  import { formatDate } from '@/utils/date_utils';
  import { base_url } from '@/api/config';
  import { authStore } from '@/auth/store';
  
  export default defineComponent({
    name: 'PlanogramDetailView',
    setup() {
      const route = useRoute();
      const router = useRouter();
      const orderId = route.params.order_id as string;
      const planId = route.params.planogram_id as string;
  
      const planogram = ref<Planogram | null>(null);
      const isProcessing = ref(false);
  
      const load = async () => {
        planogram.value = await get_planogram(orderId, planId);
      };
  
      onMounted(load);
  
      const approve = async () => {
        if (!planogram.value) return;
        isProcessing.value = true;
        try {
          await approve_planogram(authStore.user!.id!, orderId, planId);
          await load();
        } catch {
          alert('Ошибка при согласовании');
        } finally {
          isProcessing.value = false;
        }
      };
  
      const revoke = async () => {
        if (!planogram.value) return;
        isProcessing.value = true;
        try {
            await unapprove_planogram(authStore.user!.id!, orderId, planId);
          await load();
        } catch {
          alert('Ошибка при отмене согласования');
        } finally {
          isProcessing.value = false;
        }
      };
      
      const edit = () => {
        if (!planogram.value) return;
        router.push({
          name: 'UpdatePlanogram',
          params: {
            order_id: orderId,
            planogram_id: planId,
          }
        });
      }

      return {
        base_url,
        planogram,
        isProcessing,
        formatDate,
        approve,
        revoke,
        edit
      };
    },
  });
  </script>
  
  <style scoped>
  .planogram-detail-page {
    padding: 2rem;
    max-width: 800px;
    margin: auto;
  }
  .loading {
    padding: 2rem;
    text-align: center;
    color: var(--text-secondary);
  }
  .detail-info {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 2rem;
  }
  .info-row {
    display: flex;
    margin-bottom: 0.75rem;
  }
  .info-row .label {
    width: 160px;
    font-weight: 600;
    color: var(--text-secondary);
  }
  .info-row .value {
    color: var(--text);
  }
  .matrix {
    margin-bottom: 2rem;
  }
  .shelf-row {
    margin-bottom: 1.5rem;
  }
  .shelf-row h4 {
    margin-bottom: 0.5rem;
  }
  .shelf-boxes {
    display: flex;
    gap: 0.5rem;
  }
  .shelf-box {
    width: 60px;
    height: 60px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .shelf-box img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
  }
  .actions {
    display: flex;
    gap: 1rem;
  }
  .btn-approve,
  .btn-revoke {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 6px;
    color: #fff;
    cursor: pointer;
  }
  .btn-approve {
    background: var(--primary);
  }
  .btn-revoke {
    background: #ef4444;
  }
  .btn-approve:disabled,
  .btn-revoke:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  .btn-edit {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 6px;
    background: var(--primary);
    color: #fff;
    cursor: pointer;
  }
  </style>
  