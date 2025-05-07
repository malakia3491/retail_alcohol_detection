<template>
  <nav class="navbar">
    <ul class="nav-list">
      <li class="nav-item">
         <router-link to="/profile" class="nav-button">Личный кабинет</router-link>
      </li>

      <!-- Приказы -->
      <li class="nav-item">
        <button class="nav-button" @click="toggle('orders')">
          Приказы
          <span class="arrow" :class="{ open: openItem === 'orders' }">▾</span>
        </button>
        <ul class="subnav" v-show="openItem === 'orders'">
          <li>
            <router-link to="/orders" class="subnav-link">
              Все приказы
            </router-link>
          </li>
          <li>
            <router-link to="/orders/active" class="subnav-link">
              Актуальные приказы
            </router-link>
          </li>
        </ul>
      </li>

      <!-- Стеллажи -->
      <li class="nav-item">
        <button class="nav-button" @click="toggle('shelves')">
          Стеллажи
          <span class="arrow" :class="{ open: openItem === 'shelves' }">▾</span>
        </button>
        <ul class="subnav" v-show="openItem === 'shelves'">
          <li>
            <router-link to="/planograms/actual" class="subnav-link">
              Планограммы
            </router-link>
          </li>
          <li>
            <router-link to="/realograms/actual" class="subnav-link">
              Реалограммы
            </router-link>
          </li>
        </ul>
      </li>

      <!-- Товары -->
      <li class="nav-item">
        <button class="nav-button" @click="toggle('products')">
          Товары
          <span class="arrow" :class="{ open: openItem === 'products' }">▾</span>
        </button>
        <ul class="subnav" v-show="openItem === 'products'">
          <li>
            <router-link to="/products/add-images" class="subnav-link">
              Добавить изображения
            </router-link>
          </li>
        </ul>
      </li>

      <!-- Отчёты -->
      <li class="nav-item">
        <button class="nav-button" @click="toggle('reports')">
          Отчёты
          <span class="arrow" :class="{ open: openItem === 'reports' }">▾</span>
        </button>
        <ul class="subnav" v-show="openItem === 'reports'">
          <li>
            <router-link to="/reports/execution" class="subnav-link">
              Отчёт по выполнению планограмм
            </router-link>
          </li>
          <li>
            <router-link to="/reports/economics" class="subnav-link">
              Отчёт об экономической эффективности планограмм
            </router-link>
          </li>
        </ul>
      </li>
    </ul>
  </nav>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'Navigation',
  setup() {
    // Хранит ключ открытого пункта (или null)
    const openItem = ref<string | null>(null);

    const toggle = (key: string) => {
      openItem.value = openItem.value === key ? null : key;
    };

    return { openItem, toggle };
  },
});
</script>

<style scoped>
.navbar {
  position: relative;
}

.nav-list {
  list-style: none;
  display: flex;
  gap: 1rem;
  margin: 0;
  padding: 0;
}

.nav-item {
  position: relative;
}

.nav-button {
  background: none;
  border: none;
  font: inherit;
  cursor: pointer;
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
}

.arrow {
  display: inline-block;
  margin-left: 0.5rem;
  transition: transform 0.2s;
}

.arrow.open {
  transform: rotate(180deg);
}

.subnav {
  position: absolute;
  top: calc(100% + 0.25rem);
  left: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  padding: 0.5rem 0;
  min-width: 220px;
  z-index: 10;
}

.subnav-link {
  display: block;
  color: var(--text-secondary);
  text-decoration: none;
  padding: 0.5rem 1rem;
  transition: background 0.2s, color 0.2s;
}

.subnav-link:hover {
  background: var(--bg);
  color: var(--text);
}

/* Скрываем через v-show, но на всякий случай перекроем pointer-events */
.subnav[style*="display: none"] {
  pointer-events: none;
}
</style>
