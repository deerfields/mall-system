<template>
  <div class="permit-form">
    <h2>فرم Permit to Work</h2>
    <form @submit.prevent="submitForm">
      <div>
        <label>نام شرکت/پیمانکار:</label>
        <input v-model="form.company_name" required />
      </div>
      <div>
        <label>مجوز شرکت:</label>
        <input type="file" @change="onCompanyLicenseChange" required />
      </div>
      <div>
        <label>محل کار:</label>
        <input v-model="form.job_location" required />
      </div>
      <div>
        <label>نماینده مسئول:</label>
        <input v-model="form.onsite_in_charge" required />
      </div>
      <div>
        <label>شماره تماس:</label>
        <input v-model="form.contact_no" required />
      </div>
      <div>
        <label>نوع کار:</label>
        <input v-model="form.job_type" required />
      </div>
      <div>
        <label>شرح کار:</label>
        <textarea v-model="form.job_description" required></textarea>
      </div>
      <div>
        <label>تاریخ شروع:</label>
        <input type="date" v-model="form.job_date_from" required />
        <label>تاریخ پایان:</label>
        <input type="date" v-model="form.job_date_to" required />
      </div>
      <div>
        <label>ساعت شروع:</label>
        <input type="time" v-model="form.job_time_from" required />
        <label>ساعت پایان:</label>
        <input type="time" v-model="form.job_time_to" required />
      </div>
      <div>
        <label>ارزیابی ریسک:</label>
        <textarea v-model="form.risk_assessment"></textarea>
      </div>
      <div>
        <label>اقدامات ایمنی:</label>
        <textarea v-model="form.safety_measures"></textarea>
      </div>
      <div>
        <label>لیست تجهیزات:</label>
        <input v-model="equipmentInput" @keyup.enter.prevent="addEquipment" placeholder="افزودن تجهیزات..." />
        <ul>
          <li v-for="(eq, idx) in form.equipment_list" :key="idx">
            {{ eq }} <button type="button" @click="removeEquipment(idx)">حذف</button>
          </li>
        </ul>
      </div>
      <div>
        <label>نیاز به قطع برق/آب/گاز:</label>
        <select v-model="form.need_power_cut">
          <option value="no">خیر</option>
          <option value="yes">بله</option>
        </select>
      </div>
      <div>
        <label>نیاز به همراهی پرسنل مال:</label>
        <select v-model="form.need_mall_staff">
          <option value="no">خیر</option>
          <option value="yes">بله</option>
        </select>
      </div>
      <div>
        <label>توضیحات تکمیلی:</label>
        <textarea v-model="form.extra_notes"></textarea>
      </div>
      <div>
        <label>پیوست‌ها:</label>
        <input type="file" multiple @change="onAttachmentsChange" />
      </div>
      <div>
        <label>لیست کارگران:</label>
        <div v-for="(worker, idx) in form.workers" :key="idx" class="worker-row">
          <input v-model="worker.name" placeholder="نام کارگر" required />
          <input v-model="worker.code" placeholder="کد/شماره شناسایی" />
          <input type="file" @change="e => onWorkerFileChange(e, idx, 'id_card')" />
          <input type="file" @change="e => onWorkerFileChange(e, idx, 'insurance')" />
          <button type="button" @click="removeWorker(idx)">حذف</button>
        </div>
        <button type="button" @click="addWorker">افزودن کارگر</button>
      </div>
      <button type="submit">ثبت درخواست</button>
    </form>
    <div v-if="statusMsg" class="status-msg">{{ statusMsg }}</div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  name: 'PermitToWorkForm',
  data() {
    return {
      form: {
        company_name: '',
        job_location: '',
        onsite_in_charge: '',
        contact_no: '',
        job_type: '',
        job_description: '',
        job_date_from: '',
        job_date_to: '',
        job_time_from: '',
        job_time_to: '',
        risk_assessment: '',
        safety_measures: '',
        equipment_list: [],
        need_power_cut: 'no',
        need_mall_staff: 'no',
        extra_notes: '',
        attachments: [],
        workers: [],
      },
      companyLicenseFile: null,
      attachmentsFiles: [],
      equipmentInput: '',
      statusMsg: '',
    };
  },
  methods: {
    addWorker() {
      this.form.workers.push({ name: '', code: '', id_card: null, insurance: null });
    },
    removeWorker(idx) {
      this.form.workers.splice(idx, 1);
    },
    onWorkerFileChange(e, idx, type) {
      const file = e.target.files[0];
      this.$set(this.form.workers[idx], type, file);
    },
    onCompanyLicenseChange(e) {
      this.companyLicenseFile = e.target.files[0];
    },
    onAttachmentsChange(e) {
      this.attachmentsFiles = Array.from(e.target.files);
    },
    addEquipment() {
      if (this.equipmentInput) {
        this.form.equipment_list.push(this.equipmentInput);
        this.equipmentInput = '';
      }
    },
    removeEquipment(idx) {
      this.form.equipment_list.splice(idx, 1);
    },
    async submitForm() {
      try {
        // مرحله ۱: ارسال اطلاعات متنی و لیست کارگران
        const workersData = this.form.workers.map(w => ({ name: w.name, code: w.code }));
        const payload = { ...this.form, workers: workersData, attachments: this.attachmentsFiles.map(f => f.name) };
        const res = await axios.post('/api/permits/request/full', payload);
        const permitId = res.data.id;
        // مرحله ۲: آپلود مجوز شرکت
        if (this.companyLicenseFile) {
          const formData = new FormData();
          formData.append('license_file', this.companyLicenseFile);
          await axios.post(`/api/permits/request/${permitId}/upload_license`, formData);
        }
        // مرحله ۳: آپلود مدارک کارگران
        for (let i = 0; i < this.form.workers.length; i++) {
          const worker = this.form.workers[i];
          if (worker.id_card || worker.insurance) {
            // باید worker_id را از backend بگیریم (در نسخه بعدی)
            // فرض: worker_idها به ترتیب ایجاد می‌شوند
            const workerId = permitId + '_' + i;
            const formData = new FormData();
            if (worker.id_card) formData.append('id_card', worker.id_card);
            if (worker.insurance) formData.append('insurance', worker.insurance);
            await axios.post(`/api/permits/worker/${workerId}/upload`, formData);
          }
        }
        // مرحله ۴: آپلود پیوست‌ها (در صورت نیاز)
        // ...
        this.statusMsg = 'درخواست با موفقیت ثبت شد!';
      } catch (e) {
        this.statusMsg = 'خطا در ثبت درخواست!';
      }
    },
  },
};
</script>

<style scoped>
.permit-form {
  max-width: 700px;
  margin: 2rem auto;
  padding: 1.5rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px #eee;
}
.permit-form form > div {
  margin-bottom: 1rem;
}
.worker-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}
.status-msg {
  margin-top: 1rem;
  color: green;
  font-weight: bold;
}
</style> 