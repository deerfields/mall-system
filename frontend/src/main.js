import { createApp } from 'vue';
import Dashboard from './pages/Dashboard.vue';
import { createI18n } from 'vue-i18n';
import en from './locales/en.json';
import ar from './locales/ar.json';

const i18n = createI18n({
  locale: 'en', // default language
  fallbackLocale: 'en',
  messages: { en, ar }
});

const app = createApp(Dashboard);
app.use(i18n);
app.mount('#app'); 