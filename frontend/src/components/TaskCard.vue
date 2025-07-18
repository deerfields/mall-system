<template>
  <div class="task-card">
    <h2>{{ title }}</h2>
    <p>Status: {{ status }}</p>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  status: String
});
</script>

<style scoped>
.task-card {
  border: 1px solid #ccc;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 8px;
}
</style> 