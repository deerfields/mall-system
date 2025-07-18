<template>
  <div class="permit-dashboard">
    <h2>داشبورد مدیریتی Permit to Work</h2>
    <div class="stats">
      <div>کل درخواست‌ها: {{ stats.total }}</div>
      <div>تایید شده: {{ stats.approved }}</div>
      <div>رد شده: {{ stats.rejected }}</div>
      <div>ناقص: {{ stats.incomplete }}</div>
      <div>در انتظار بررسی: {{ stats.pending }}</div>
    </div>
    <div class="chart-section">
      <canvas id="statusChart"></canvas>
    </div>
    <h3>درخواست‌های اخیر</h3>
    <table>
      <thead>
        <tr>
          <th>کد</th>
          <th>شرکت</th>
          <th>محل کار</th>
          <th>تاریخ شروع</th>
          <th>وضعیت</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="permit in recentPermits" :key="permit.id">
          <td>{{ permit.id }}</td>
          <td>{{ permit.company_name }}</td>
          <td>{{ permit.job_location }}</td>
          <td>{{ formatDate(permit.job_date_from) }}</td>
          <td><span :class="statusClass(permit.status)">{{ statusText(permit.status) }}</span></td>
        </tr>
      </tbody>
    </table>
    <h3>درخواست‌های با مدارک ناقص</h3>
    <ul>
      <li v-for="permit in incompletePermits" :key="permit.id">
        {{ permit.company_name }} - {{ permit.job_location }} (کد: {{ permit.id }})
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios';
import Chart from 'chart.js/auto';
export default {
  name: 'PermitDashboard',
  data() {
    return {
      stats: { total: 0, approved: 0, rejected: 0, incomplete: 0, pending: 0 },
      recentPermits: [],
      incompletePermits: [],
      chart: null,
    };
  },
  methods: {
    async fetchStats() {
      // فرض: API آمار و لیست درخواست‌ها پیاده‌سازی شده است
      const res = await axios.get('/api/permits/dashboard');
      this.stats = res.data.stats;
      this.recentPermits = res.data.recent;
      this.incompletePermits = res.data.incomplete;
      this.renderChart();
    },
    renderChart() {
      if (this.chart) this.chart.destroy();
      const ctx = document.getElementById('statusChart');
      this.chart = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: ['تایید شده', 'رد شده', 'ناقص', 'در انتظار بررسی'],
          datasets: [{
            data: [this.stats.approved, this.stats.rejected, this.stats.incomplete, this.stats.pending],
            backgroundColor: ['#4caf50', '#f44336', '#ffc107', '#ff9800'],
          }],
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom' } } },
      });
    },
    formatDate(date) {
      if (!date) return '';
      return new Date(date).toLocaleDateString('fa-IR');
    },
    statusText(status) {
      switch (status) {
        case 'pending': return 'در انتظار بررسی';
        case 'approved': return 'تایید شده';
        case 'rejected': return 'رد شده';
        case 'incomplete': return 'ناقص';
        default: return status;
      }
    },
    statusClass(status) {
      return {
        pending: 'status-pending',
        approved: 'status-approved',
        rejected: 'status-rejected',
        incomplete: 'status-incomplete',
      }[status] || '';
    },
  },
  mounted() {
    this.fetchStats();
  },
};
</script>

<style scoped>
.permit-dashboard {
  max-width: 900px;
  margin: 2rem auto;
  background: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px #eee;
}
.stats {
  display: flex;
  gap: 2rem;
  margin-bottom: 1rem;
}
.chart-section {
  max-width: 400px;
  margin: 1rem auto;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}
th, td {
  border: 1px solid #eee;
  padding: 0.5rem 1rem;
  text-align: center;
}
.status-pending { color: orange; }
.status-approved { color: green; }
.status-rejected { color: red; }
.status-incomplete { color: #bfa700; }
</style> 