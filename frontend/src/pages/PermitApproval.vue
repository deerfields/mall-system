<template>
  <div class="permit-approval">
    <div style="display: flex; justify-content: flex-end; margin-bottom: 1rem;">
      <select v-model="lang" @change="switchLang">
        <option value="en">English</option>
        <option value="ar">العربية</option>
      </select>
    </div>
    <h1>{{ $t('permit_approval') }}</h1>
    <div v-if="permits.length === 0">{{ $t('no_pending_permits') }}</div>
    <div v-for="permit in permits" :key="permit.id" class="permit-card">
      <div><b>{{ $t('company_name') }}:</b> {{ permit.company_name }}</div>
      <div><b>{{ $t('job_location') }}:</b> {{ permit.job_location }}</div>
      <div><b>{{ $t('job_type') }}:</b> {{ $t(permit.job_type) }}</div>
      <div><b>{{ $t('job_description') }}:</b> {{ permit.job_description }}</div>
      <div><b>{{ $t('requested_by') }}:</b> {{ permit.requested_by }}</div>
      <button @click="editId = permit.id">{{ $t('edit') }}</button>
      <button @click="approvePermit(permit.id)">{{ $t('approve') }}</button>
      <div v-if="editId === permit.id" class="edit-form">
        <h3>{{ $t('edit_permit') }}</h3>
        <form @submit.prevent="submitEdit(permit.id)">
          <div class="form-row">
            <label>{{ $t('company_name') }}</label>
            <input v-model="editForm.company_name" />
          </div>
          <div class="form-row">
            <label>{{ $t('job_location') }}</label>
            <input v-model="editForm.job_location" />
          </div>
          <div class="form-row">
            <label>{{ $t('job_description') }}</label>
            <textarea v-model="editForm.job_description"></textarea>
          </div>
          <div class="form-row">
            <button type="submit">{{ $t('save') }}</button>
            <button type="button" @click="editId = null">{{ $t('cancel') }}</button>
          </div>
        </form>
      </div>
    </div>
    <div v-if="success" class="success">{{ $t('success_message') }}</div>
    <div v-if="error" class="error">{{ $t('error_message') }}</div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      lang: this.$i18n.locale,
      department: 'facilities', // Change to 'marketing' or 'operations' for other managers
      permits: [],
      editId: null,
      editForm: {},
      success: false,
      error: false
    }
  },
  mounted() {
    this.fetchPermits();
  },
  methods: {
    switchLang() {
      this.$i18n.locale = this.lang;
      document.body.setAttribute('dir', this.lang === 'ar' ? 'rtl' : 'ltr');
    },
    async fetchPermits() {
      const res = await axios.get(`/api/permits/pending/${this.department}`);
      this.permits = res.data;
    },
    editPermit(permit) {
      this.editId = permit.id;
      this.editForm = { ...permit };
    },
    async submitEdit(permitId) {
      this.success = false;
      this.error = false;
      try {
        await axios.put(`/api/permits/${permitId}/edit/${this.department}`, this.editForm);
        this.success = true;
        this.editId = null;
        this.fetchPermits();
      } catch (e) {
        this.error = true;
      }
    },
    async approvePermit(permitId) {
      this.success = false;
      this.error = false;
      try {
        await axios.post(`/api/permits/${permitId}/approve/${this.department}`);
        this.success = true;
        this.fetchPermits();
      } catch (e) {
        this.error = true;
      }
    }
  }
}
</script>

<style>
.permit-approval { max-width: 700px; margin: 2rem auto; background: #fff; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 8px #eee; }
.permit-card { border: 1px solid #ccc; border-radius: 6px; padding: 1rem; margin-bottom: 1.5rem; background: #f9f9f9; }
.edit-form { background: #f3f3f3; padding: 1rem; border-radius: 6px; margin-top: 1rem; }
.form-row { margin-bottom: 1rem; display: flex; flex-direction: column; }
label { margin-bottom: 0.3rem; font-weight: bold; }
input, textarea { padding: 0.5rem; border: 1px solid #ccc; border-radius: 4px; }
button { margin-right: 0.5rem; padding: 0.5rem 1.5rem; background: #007bff; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
.success { color: green; margin-top: 1rem; }
.error { color: red; margin-top: 1rem; }
</style> 