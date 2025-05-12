<template>
  <section class="calibrate-page">
    <h2>Калибровка планограммы</h2>

    <div class="controls">
      <input type="file" accept="image/*" @change="onFileChange" />
      <button :disabled="!imageSrc || isDetecting" @click="detectBoxes">
        {{ isDetecting ? 'Обнаружение...' : 'Предварительно разметить' }}
      </button>
      <button :disabled="!boxes.length" @click="submitCalibration">Разметить</button>
    </div>

    <div v-if="imageSrc" class="image-container" ref="container">
      <img
        :src="imageSrc"
        ref="img"
        @load="onImageLoad"
        @dblclick="addBox"
        alt="Калибруемая планограмма"
      />
      <svg
        v-if="imgSize"
        class="overlay"
        :width="imgSize.width"
        :height="imgSize.height"
      >
        <g v-for="(box, idx) in boxes" :key="idx">
          <rect
            :x="box.x"
            :y="box.y"
            :width="box.w"
            :height="box.h"
            class="box-rect"
            @mousedown.prevent="startDrag(idx, $event)"
            @dblclick.prevent="removeBox(idx)"
          />
          <circle
            :cx="box.x + box.w"
            :cy="box.y + box.h"
            r="6"
            class="resize-handle"
            @mousedown.prevent="startResize(idx, $event)"
          />
        </g>
      </svg>
    </div>
  </section>
</template>

<script lang="ts">
import { defineComponent, ref, reactive } from 'vue';
import { useRoute } from 'vue-router';
import { get_calibrate_boxes, calibrate_planogram } from '@/api/planograms';
import { authStore } from '@/auth/store';

interface Box { x: number; y: number; w: number; h: number; conf: number }

export default defineComponent({
  name: 'CalibratePlanogramView',
  setup() {
    const route = useRoute();
    const order_id = route.query.order_id as string;
    const shelving_id = route.query.shelving_id as string;
    const store_id = route.query.store_id as string;

    const imageSrc = ref<string | null>(null);
    const imgSize = ref<{ width: number; height: number } | null>(null);
    const boxes = reactive<Box[]>([]);
    const isDetecting = ref(false);
    const selectedFile = ref<File|null>(null);

    // drag/resize state
    let mode: 'drag' | 'resize' | null = null;
    let activeIdx = -1;
    let startX = 0, startY = 0;
    let orig: Box = { x: 0, y: 0, w: 0, h: 0, conf: 0 };

    const img = ref<HTMLImageElement | null>(null);

    const onFileChange = (e: Event) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;
      imageSrc.value = URL.createObjectURL(file);
      selectedFile.value = file;
      boxes.splice(0);
      imgSize.value = null;
    };

    const onImageLoad = () => {
      if (!img.value) return;
      imgSize.value = {
        width: img.value.naturalWidth,
        height: img.value.naturalHeight
      };
    };

    const detectBoxes = async () => {
      if (!imageSrc.value) return;
      isDetecting.value = true;
      try {
        const form = new FormData();
        form.append('image_file', await fetch(imageSrc.value).then(r => r.blob()));
        const resp_boxes = await get_calibrate_boxes(form);
        boxes.splice(0);
        resp_boxes.forEach(box => {
          const [x1, y1, x2, y2] = box.xyxy;
          boxes.push({ x: x1, y: y1, w: x2 - x1, h: y2 - y1, conf: box.conf });
        });
      } finally {
        isDetecting.value = false;
      }
    };

    const startDrag = (idx: number, ev: MouseEvent) => {
      mode = 'drag'; activeIdx = idx;
      startX = ev.clientX; startY = ev.clientY;
      orig = { ...boxes[idx] };
      window.addEventListener('mousemove', onDrag);
      window.addEventListener('mouseup', endAction);
    };
    const onDrag = (ev: MouseEvent) => {
      if (mode !== 'drag') return;
      const dx = ev.clientX - startX, dy = ev.clientY - startY;
      boxes[activeIdx].x = orig.x + dx;
      boxes[activeIdx].y = orig.y + dy;
    };

    const startResize = (idx: number, ev: MouseEvent) => {
      mode = 'resize'; activeIdx = idx;
      startX = ev.clientX; startY = ev.clientY;
      orig = { ...boxes[idx] };
      window.addEventListener('mousemove', onResize);
      window.addEventListener('mouseup', endAction);
    };
    const onResize = (ev: MouseEvent) => {
      if (mode !== 'resize') return;
      const dx = ev.clientX - startX, dy = ev.clientY - startY;
      boxes[activeIdx].w = Math.max(10, orig.w + dx);
      boxes[activeIdx].h = Math.max(10, orig.h + dy);
    };

    const endAction = () => {
      window.removeEventListener('mousemove', onDrag);
      window.removeEventListener('mousemove', onResize);
      window.removeEventListener('mouseup', endAction);
      mode = null; activeIdx = -1;
    };

    const addBox = (e: MouseEvent) => {
      if (!imgSize.value || !img.value) return;
      const rect = img.value.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      boxes.push({ x, y, w: 100, h: 100, conf: 1.0 });
    };

    const removeBox = (idx: number) => {
      boxes.splice(idx, 1);
    };

    const submitCalibration = async () => {
        const form = new FormData();
        form.append("order_id", order_id);
        form.append("person_id", authStore.user!.id!);
        form.append("shelving_id", shelving_id);
        form.append("store_id", store_id);
        form.append(
            "calibration_boxes",
            JSON.stringify(boxes.map(b => ({
            xyxy: [b.x, b.y, b.x + b.w, b.y + b.h],
            conf: b.conf
            })))
        );
        if (!selectedFile.value) {
          alert("Сначала выберите картинку");
          return;
        }
        form.append("image_file", selectedFile.value);

      await calibrate_planogram(form);
      alert('Калибровка сохранена');
    };

    return {
      imageSrc, imgSize, boxes, isDetecting,
      img,
      onFileChange, onImageLoad, detectBoxes,
      startDrag, startResize, addBox, removeBox,
      submitCalibration
    };
  }
});
</script>

<style scoped>
.calibrate-page {
  padding: 2rem;
  font-family: Arial, sans-serif;
}
.controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}
button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  background: #007bff;
  color: white;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}
button:disabled {
  background: #aaa;
  cursor: not-allowed;
}
button:not(:disabled):hover {
  background: #0056b3;
}
.image-container {
  position: relative;
  display: inline-block;
}
.image-container img {
  display: block;
  max-width: 100%;
  cursor: crosshair;
}
.overlay {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
}
.box-rect {
  fill: rgba(255, 215, 0, 0.15);
  stroke: gold;
  stroke-width: 2;
  cursor: move;
  pointer-events: all;
}
.resize-handle {
  fill: white;
  stroke: gold;
  stroke-width: 2;
  cursor: se-resize;
  pointer-events: all;
}
</style>