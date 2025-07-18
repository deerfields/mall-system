<template>
  <form @submit.prevent="submitRental">
    <label>مغازه:
      <input v-model="rental.shop_id" required />
    </label>
    <label>مستاجر:
      <input v-model="rental.tenant" required />
    </label>
    <label>مبلغ:
      <input v-model="rental.amount" />
    </label>
    <button type="submit">ثبت اجاره</button>
  </form>
</template>

<script setup>
import { ref } from 'vue';
const rental = ref({ shop_id: '', tenant: '', amount: '' });
function submitRental() {
  // TODO: ارسال به بک‌اند
  alert('اجاره ثبت شد!');
}
</script> 