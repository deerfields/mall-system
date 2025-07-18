<template>
  <div>
    <h2>لیست مغازه‌ها</h2>
    <ul>
      <li v-for="shop in shops" :key="shop.id">
        {{ shop.name }} - {{ shop.location }} - {{ shop.size }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
const shops = ref([]);
onMounted(async () => {
  // TODO: fetch from backend
  shops.value = [
    { id: '1', name: 'مغازه ۱', location: 'طبقه اول', size: '۲۰ متر' },
    { id: '2', name: 'مغازه ۲', location: 'طبقه دوم', size: '۳۰ متر' }
  ];
});
</script> 