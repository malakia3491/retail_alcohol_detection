<template>
  <section class="notification-help">
    <h2>Настройка уведомлений в Telegram</h2>
    
    <div class="instructions">
      <p>Для получения оперативных уведомлений выполните следующие шаги:</p>
      
      <ol class="steps-list">
        <li>Установите Telegram, если у вас его нет</li>
        <li>Перейдите в нашего бота-уведомителя: 
          <a href="https://t.me/PlanogramControllerBot" 
             target="_blank" 
             class="telegram-link">
            @PlanogramControllerBot
          </a>
        </li>
        <li>Нажмите кнопку "Start" в диалоге с ботом</li>
        <li>Введите ваш корпоративный email для привязки</li>
      </ol>

      <div class="qr-section">
        <p>Или отсканируйте QR-код:</p>
        <img src="@/assets/tg-qr.png" 
             alt="QR код для Telegram бота" 
             class="qr-code">
      </div>

      <p class="note">
        После регистрации вы будете получать важные уведомления прямо в Telegram!
      </p>
    </div>
  </section>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'NotificationHelpView',
});
</script>

<style scoped>
.notification-help {
  padding: 1rem 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.notification-help h2 {
  margin-bottom: 1.5rem;
  color: var(--primary);
  text-align: center;
}

.instructions {
  background-color: var(--background-secondary);
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.steps-list {
  line-height: 1.6;
  margin: 1.5rem 0;
  padding-left: 1.5rem;
}

.steps-list li {
  margin-bottom: 1rem;
}

.telegram-link {
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.telegram-link:hover {
  color: var(--primary-hover);
}

.qr-section {
  margin-top: 2rem;
  text-align: center;
}

.qr-code {
  width: 300px;
  height: 300px;
  margin: 1rem auto;
  display: block;
  border: 1px solid var(--border-color);
  padding: 8px;
  border-radius: 8px;
}

.note {
  margin-top: 1.5rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
  text-align: center;
}
</style>