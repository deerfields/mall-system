<template>
  <div class="notification-manager">
    <h2>ارسال اطلاعیه جدید</h2>
    <form @submit.prevent="sendNotification">
      <div>
        <label>عنوان:</label>
        <input v-model="form.title" required />
      </div>
      <div>
        <label>متن پیام:</label>
        <textarea v-model="form.message" required></textarea>
      </div>
      <div>
        <label>دریافت‌کنندگان:</label>
        <select v-model="form.recipient_ids" multiple required>
          <option v-for="tenant in tenants" :key="tenant.id" :value="tenant.id">
            {{ tenant.shop_name }} ({{ tenant.user?.username }})
          </option>
        </select>
      </div>
      <div>
        <label><input type="checkbox" v-model="form.send_email" /> ارسال ایمیل</label>
      </div>
      <button type="submit">ارسال اطلاعیه</button>
    </form>

    <hr />
    <h2>لیست اطلاعیه‌ها</h2>
    <ul>
      <li v-for="n in notifications" :key="n.id">
        <strong>{{ n.title }}</strong> - {{ n.message }}<br />
        <small>تاریخ: {{ formatDate(n.created_at) }} | ارسال‌کننده: {{ n.sent_by }} | ایمیل: {{ n.email_sent }}</small>
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  name: 'NotificationManager',
  data() {
    return {
      form: {
        title: '',
        message: '',
        recipient_ids: [],
        send_email: true,
      },
      tenants: [],
      notifications: [],
    };
  },
  methods: {
    async fetchTenants() {
      // فرض بر این است که API مستاجران وجود دارد
      const res = await axios.get('/api/tenants');
      this.tenants = res.data;
    },
    async fetchNotifications() {
      const res = await axios.get('/api/notifications');
      this.notifications = res.data;
    },
    async sendNotification() {
      try {
        await axios.post('/api/notifications', this.form);
        alert('اطلاعیه با موفقیت ارسال شد!');
        this.form.title = '';
        this.form.message = '';
        this.form.recipient_ids = [];
        this.fetchNotifications();
      } catch (e) {
        alert('خطا در ارسال اطلاعیه');
      }
    },
    formatDate(date) {
      return new Date(date).toLocaleString('fa-IR');
    },
  },
  mounted() {
    this.fetchTenants();
    this.fetchNotifications();
  },
};
</script>

<style scoped>
.notification-manager {
  max-width: 600px;
  margin: 2rem auto;
  padding: 1rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px #eee;
}
.notification-manager form > div {
  margin-bottom: 1rem;
}
.notification-manager ul {
  list-style: none;
  padding: 0;
}
.notification-manager li {
  margin-bottom: 1rem;
  padding: 0.5rem;
  background: #f9f9f9;
  border-radius: 4px;
}
</style> 