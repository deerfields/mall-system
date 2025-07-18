<template>
  <div class="dashboard">
    <div style="display: flex; justify-content: flex-end; margin-bottom: 1rem;">
      <select v-model="lang" @change="switchLang">
        <option value="en">English</option>
        <option value="ar">العربية</option>
      </select>
    </div>
    <h1>{{ $t('dashboard') }}</h1>
    <div class="kpi-cards">
      <div class="kpi-card">{{ $t('active_users') }}: {{ summary.active_users }}</div>
      <div class="kpi-card">{{ $t('active_contracts') }}: {{ summary.active_contracts }}</div>
      <div class="kpi-card">{{ $t('open_tasks') }}: {{ summary.open_tasks }}</div>
      <div class="kpi-card">{{ $t('security_events') }}: {{ summary.security_events }}</div>
    </div>
    <NotificationManager />
  </div>
</template>

<script>
import axios from 'axios';
import NotificationManager from '../components/NotificationManager.vue';
export default {
  components: { NotificationManager },
  data() {
    return {
      summary: {},
      lang: this.$i18n.locale
    }
  },
  mounted() {
    axios.get('/api/dashboard/summary').then(res => {
      this.summary = res.data;
    });
  },
  methods: {
    switchLang() {
      this.$i18n.locale = this.lang;
      document.body.setAttribute('dir', this.lang === 'ar' ? 'rtl' : 'ltr');
    }
  }
}
</script>

<style>
.dashboard { padding: 2rem; }
.kpi-cards { display: flex; gap: 2rem; }
.kpi-card { background: #f3f3f3; padding: 1rem 2rem; border-radius: 8px; font-size: 1.2rem; }
</style> 