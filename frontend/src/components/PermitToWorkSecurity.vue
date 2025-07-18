<template>
  <div class="permit-security">
    <h2>کنترل Permit to Work (سکوریتی)</h2>
    <form @submit.prevent="fetchPermit">
      <label>کد Permit یا اسکن QR:</label>
      <input v-model="permitCode" placeholder="کد Permit..." required />
      <button type="submit">بررسی</button>
    </form>
    <div v-if="permit" class="permit-details">
      <h3>اطلاعات Permit</h3>
      <div><b>شرکت:</b> {{ permit.company_name }}</div>
      <div><b>محل کار:</b> {{ permit.job_location }}</div>
      <div><b>نماینده مسئول:</b> {{ permit.onsite_in_charge }}</div>
      <div><b>نوع کار:</b> {{ permit.job_type }}</div>
      <div><b>تاریخ شروع:</b> {{ formatDate(permit.job_date_from) }}</div>
      <div><b>تاریخ پایان:</b> {{ formatDate(permit.job_date_to) }}</div>
      <div><b>وضعیت:</b> {{ statusText(permit.status) }}</div>
      <div><b>لیست کارگران:</b>
        <ul>
          <li v-for="w in permit.workers" :key="w.id">
            {{ w.name }} ({{ w.code }})
            <span v-if="w.id_card_url">| <a :href="fileUrl(w.id_card_url)" target="_blank">کارت شناسایی</a></span>
            <span v-if="w.insurance_url">| <a :href="fileUrl(w.insurance_url)" target="_blank">بیمه</a></span>
          </li>
        </ul>
      </div>
      <div class="security-actions">
        <button @click="confirmEntry">تایید ورود</button>
        <button @click="reportMismatch">گزارش مغایرت</button>
        <button @click="permit = null">بستن</button>
      </div>
      <div v-if="statusMsg" class="status-msg">{{ statusMsg }}</div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  name: 'PermitToWorkSecurity',
  data() {
    return {
      permitCode: '',
      permit: null,
      statusMsg: '',
    };
  },
  methods: {
    async fetchPermit() {
      try {
        const res = await axios.get(`/api/permits/request/${this.permitCode}`);
        this.permit = res.data;
        this.statusMsg = '';
      } catch (e) {
        this.statusMsg = 'درخواست یافت نشد یا کد اشتباه است!';
        this.permit = null;
      }
    },
    confirmEntry() {
      this.statusMsg = 'ورود تایید شد.';
      // می‌توان این رویداد را به backend نیز ارسال کرد
    },
    reportMismatch() {
      this.statusMsg = 'مغایرت گزارش شد.';
      // می‌توان این رویداد را به backend نیز ارسال کرد
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
    fileUrl(path) {
      return '/' + path;
    },
  },
};
</script>

<style scoped>
.permit-security {
  max-width: 600px;
  margin: 2rem auto;
  background: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px #eee;
}
.permit-details {
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 6px;
  margin-top: 1rem;
}
.security-actions {
  margin-top: 1rem;
  display: flex;
  gap: 1rem;
}
.status-msg {
  margin-top: 1rem;
  color: green;
  font-weight: bold;
}
</style> 