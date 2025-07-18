<template>
  <div>
    <h2>داشبورد قراردادها</h2>
    <form @submit.prevent="submitContract">
      <label>مستاجر:
        <input v-model="form.tenant_id" required />
      </label>
      <label>مغازه:
        <input v-model="form.shop_id" required />
      </label>
      <label>تاریخ شروع:
        <input type="date" v-model="form.start_date" required />
      </label>
      <label>تاریخ پایان:
        <input type="date" v-model="form.end_date" required />
      </label>
      <label>مبلغ:
        <input type="number" v-model="form.amount" required />
      </label>
      <button type="submit">ثبت قرارداد</button>
    </form>
    <hr />
    <h3>لیست قراردادها</h3>
    <table border="1">
      <thead>
        <tr>
          <th>کد</th>
          <th>مستاجر</th>
          <th>مغازه</th>
          <th>تاریخ شروع</th>
          <th>تاریخ پایان</th>
          <th>مبلغ</th>
          <th>وضعیت</th>
          <th>PDF</th>
          <th>QR</th>
          <th>تاریخچه</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="c in contracts" :key="c.id">
          <td>{{ c.id }}</td>
          <td>{{ c.tenant_id }}</td>
          <td>{{ c.shop_id }}</td>
          <td>{{ c.start_date.split('T')[0] }}</td>
          <td>{{ c.end_date.split('T')[0] }}</td>
          <td>{{ c.amount }}</td>
          <td>{{ c.status }}</td>
          <td><a :href="`/api/contracts/${c.id}/pdf`" target="_blank">PDF</a></td>
          <td><a :href="`/api/contracts/${c.id}/qrcode`" target="_blank">QR</a></td>
          <td><button @click="showHistory(c.id)">نمایش</button></td>
        </tr>
      </tbody>
    </table>
    <div v-if="historyDialog">
      <h4>تاریخچه گردش کار قرارداد</h4>
      <ul>
        <li v-for="h in contractHistory" :key="h">{{ h }}</li>
      </ul>
      <button @click="historyDialog = false">بستن</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
const contracts = ref([])
const form = ref({ tenant_id: '', shop_id: '', start_date: '', end_date: '', amount: '' })
const contractHistory = ref([])
const historyDialog = ref(false)

async function fetchContracts() {
  const res = await fetch('/api/contracts')
  contracts.value = await res.json()
}
onMounted(fetchContracts)

async function submitContract() {
  await fetch('/api/contracts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form.value)
  })
  form.value = { tenant_id: '', shop_id: '', start_date: '', end_date: '', amount: '' }
  await fetchContracts()
}

async function showHistory(id) {
  const res = await fetch(`/api/contracts/${id}/workflow`)
  contractHistory.value = await res.json()
  historyDialog.value = true
}
</script>

<style scoped>
table { width: 100%; margin-top: 1em; }
th, td { padding: 0.5em; text-align: center; }
form { margin-bottom: 2em; }
</style> 