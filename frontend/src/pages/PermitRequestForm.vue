<template>
  <div class="permit-form">
    <div style="display: flex; justify-content: flex-end; margin-bottom: 1rem;">
      <select v-model="lang" @change="switchLang">
        <option value="en">English</option>
        <option value="ar">العربية</option>
      </select>
    </div>
    <h1>{{ $t('permit_form') }}</h1>
    <form @submit.prevent="submitForm">
      <div class="form-row">
        <label>{{ $t('company_name') }}</label>
        <input v-model="form.company_name" required />
      </div>
      <div class="form-row">
        <label>{{ $t('job_location') }}</label>
        <input v-model="form.job_location" required />
      </div>
      <div class="form-row">
        <label>{{ $t('onsite_in_charge') }}</label>
        <input v-model="form.onsite_in_charge" required />
      </div>
      <div class="form-row">
        <label>{{ $t('contact_no') }}</label>
        <input v-model="form.contact_no" required />
      </div>
      <div class="form-row">
        <label>{{ $t('tenant_or_contractor') }}</label>
        <select v-model="form.tenant_or_contractor" required>
          <option value="tenant">{{ $t('tenant') }}</option>
          <option value="contractor">{{ $t('contractor') }}</option>
        </select>
      </div>
      <div class="form-row">
        <label>{{ $t('job_date_from') }}</label>
        <input type="date" v-model="form.job_date_from" required />
        <label>{{ $t('job_date_to') }}</label>
        <input type="date" v-model="form.job_date_to" required />
      </div>
      <div class="form-row">
        <label>{{ $t('job_time_from') }}</label>
        <input type="time" v-model="form.job_time_from" required />
        <label>{{ $t('job_time_to') }}</label>
        <input type="time" v-model="form.job_time_to" required />
      </div>
      <div class="form-row">
        <label>{{ $t('job_type') }}</label>
        <select v-model="form.job_type" required>
          <option value="maintenance">{{ $t('maintenance') }}</option>
          <option value="remedial">{{ $t('remedial_works') }}</option>
          <option value="new">{{ $t('new_works') }}</option>
          <option value="trading">{{ $t('trading_hours') }}</option>
          <option value="others">{{ $t('others') }}</option>
        </select>
      </div>
      <div class="form-row">
        <label>{{ $t('job_description') }}</label>
        <textarea v-model="form.job_description" required></textarea>
      </div>
      <div class="form-row">
        <label>{{ $t('requested_by') }}</label>
        <input v-model="form.requested_by" required />
      </div>
      <div class="form-row">
        <button type="submit">{{ $t('submit') }}</button>
      </div>
      <div v-if="success" class="success">{{ $t('success_message') }}</div>
      <div v-if="error" class="error">{{ $t('error_message') }}</div>
    </form>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      lang: this.$i18n.locale,
      form: {
        company_name: '',
        job_location: '',
        onsite_in_charge: '',
        contact_no: '',
        tenant_or_contractor: 'tenant',
        job_date_from: '',
        job_date_to: '',
        job_time_from: '',
        job_time_to: '',
        job_type: 'maintenance',
        job_description: '',
        requested_by: ''
      },
      success: false,
      error: false
    }
  },
  methods: {
    switchLang() {
      this.$i18n.locale = this.lang;
      document.body.setAttribute('dir', this.lang === 'ar' ? 'rtl' : 'ltr');
    },
    async submitForm() {
      this.success = false;
      this.error = false;
      try {
        const payload = { ...this.form };
        payload.job_date_from = this.form.job_date_from;
        payload.job_date_to = this.form.job_date_to;
        await axios.post('/api/permits/', payload);
        this.success = true;
        this.form = {
          company_name: '', job_location: '', onsite_in_charge: '', contact_no: '', tenant_or_contractor: 'tenant',
          job_date_from: '', job_date_to: '', job_time_from: '', job_time_to: '', job_type: 'maintenance', job_description: '', requested_by: ''
        };
      } catch (e) {
        this.error = true;
      }
    }
  }
}
</script>

<style>
.permit-form { max-width: 600px; margin: 2rem auto; background: #fff; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 8px #eee; }
.form-row { margin-bottom: 1rem; display: flex; flex-direction: column; }
label { margin-bottom: 0.3rem; font-weight: bold; }
input, select, textarea { padding: 0.5rem; border: 1px solid #ccc; border-radius: 4px; }
button { padding: 0.7rem 2rem; background: #007bff; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
.success { color: green; margin-top: 1rem; }
.error { color: red; margin-top: 1rem; }
</style> 