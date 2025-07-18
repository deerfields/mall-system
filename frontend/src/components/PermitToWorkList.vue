<template>
  <div class="permit-list">
    <h2>درخواست‌های Permit to Work من</h2>
    <table>
      <thead>
        <tr>
          <th>کد</th>
          <th>شرکت</th>
          <th>محل کار</th>
          <th>تاریخ شروع</th>
          <th>وضعیت</th>
          <th>عملیات</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="permit in permits" :key="permit.id">
          <td>{{ permit.id }}</td>
          <td>{{ permit.company_name }}</td>
          <td>{{ permit.job_location }}</td>
          <td>{{ formatDate(permit.job_date_from) }}</td>
          <td>
            <span :class="statusClass(permit.status)">{{ statusText(permit.status) }}</span>
          </td>
          <td>
            <button @click="viewDetails(permit.id)">جزئیات</button>
            <button v-if="canEdit(permit)" @click="editPermit(permit.id)">ویرایش</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="selectedPermit" class="permit-details">
      <h3>جزئیات درخواست</h3>
      <div><b>شرکت:</b> {{ selectedPermit.company_name }}</div>
      <div><b>محل کار:</b> {{ selectedPermit.job_location }}</div>
      <div><b>نماینده مسئول:</b> {{ selectedPermit.onsite_in_charge }}</div>
      <div><b>شماره تماس:</b> {{ selectedPermit.contact_no }}</div>
      <div><b>نوع کار:</b> {{ selectedPermit.job_type }}</div>
      <div><b>شرح کار:</b> {{ selectedPermit.job_description }}</div>
      <div><b>تاریخ شروع:</b> {{ formatDate(selectedPermit.job_date_from) }}</div>
      <div><b>تاریخ پایان:</b> {{ formatDate(selectedPermit.job_date_to) }}</div>
      <div><b>وضعیت:</b> {{ statusText(selectedPermit.status) }}</div>
      <div><b>مجوز شرکت:</b>
        <a v-if="selectedPermit.company_license_url" :href="fileUrl(selectedPermit.company_license_url)" target="_blank">دانلود</a>
        <span v-else>ندارد</span>
      </div>
      <div><b>لیست کارگران:</b>
        <ul>
          <li v-for="w in selectedPermit.workers" :key="w.id">
            {{ w.name }} ({{ w.code }})
            <span v-if="w.id_card_url">| <a :href="fileUrl(w.id_card_url)" target="_blank">کارت شناسایی</a></span>
            <span v-if="w.insurance_url">| <a :href="fileUrl(w.insurance_url)" target="_blank">بیمه</a></span>
          </li>
        </ul>
      </div>
      <div><b>ارزیابی ریسک:</b> {{ selectedPermit.risk_assessment }}</div>
      <div><b>اقدامات ایمنی:</b> {{ selectedPermit.safety_measures }}</div>
      <div><b>تجهیزات:</b> {{ (selectedPermit.equipment_list || []).join(', ') }}</div>
      <div><b>پیوست‌ها:</b> {{ (selectedPermit.attachments || []).join(', ') }}</div>
      <div><b>توضیحات تکمیلی:</b> {{ selectedPermit.extra_notes }}</div>
      <button @click="selectedPermit = null">بستن</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  name: 'PermitToWorkList',
  data() {
    return {
      permits: [],
      selectedPermit: null,
      tenantId: '', // باید از سیستم auth گرفته شود
    };
  },
  methods: {
    async fetchPermits() {
      // فرض: API لیست درخواست‌ها بر اساس tenant_id پیاده‌سازی شده است
      const res = await axios.get(`/api/permits/request?tenant_id=${this.tenantId}`);
      this.permits = res.data;
    },
    async viewDetails(permitId) {
      const res = await axios.get(`/api/permits/request/${permitId}`);
      // تبدیل رشته‌های JSON به آرایه (در صورت نیاز)
      if (res.data.equipment_list && typeof res.data.equipment_list === 'string') {
        res.data.equipment_list = JSON.parse(res.data.equipment_list);
      }
      if (res.data.attachments && typeof res.data.attachments === 'string') {
        res.data.attachments = JSON.parse(res.data.attachments);
      }
      this.selectedPermit = res.data;
    },
    canEdit(permit) {
      return ['pending', 'incomplete'].includes(permit.status);
    },
    editPermit(permitId) {
      // ریدایرکت به فرم ویرایش (در صورت نیاز)
      this.$router.push({ name: 'PermitEdit', params: { id: permitId } });
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
    fileUrl(path) {
      // اگر نیاز به تغییر مسیر فایل‌ها بود اینجا اصلاح شود
      return '/' + path;
    },
  },
  mounted() {
    // tenantId را باید از سیستم احراز هویت بگیریم
    this.tenantId = localStorage.getItem('tenant_id') || '';
    this.fetchPermits();
  },
};
</script>

<style scoped>
.permit-list {
  max-width: 900px;
  margin: 2rem auto;
  background: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px #eee;
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
.permit-details {
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 6px;
  margin-top: 1rem;
}
</style> 