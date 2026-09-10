<template>
  <div>
    <div class="page-head">
      <div>
        <h1 class="page-title">Показания</h1>
        <p class="page-sub">Показания счётчиков ХВС, ГВС и электричества</p>
      </div>
      <div class="page-actions">
        <div v-if="availableYears.length" class="segmented" role="group" aria-label="Выбор года">
          <button
            v-for="y in availableYears"
            :key="y"
            type="button"
            :class="{ active: y === selectedYear }"
            @click="chooseYear(y)"
          >
            {{ y }}
          </button>
        </div>
        <button class="primary" @click="toggleForm">
          {{ showForm ? 'Закрыть форму' : '+ Добавить показания' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="showForm" class="card">
      <h2>{{ editingId ? 'Редактировать показания' : 'Новые показания' }}</h2>
      <form @submit.prevent="save">
        <div class="form-grid">
          <label>
            Месяц
            <input v-model="form.period" type="date" required />
          </label>
          <label>
            ХВС, м³
            <input v-model.number="form.xvs_value" type="number" step="0.001" min="0" required />
          </label>
          <label>
            ГВС, м³
            <input v-model.number="form.gvs_value" type="number" step="0.001" min="0" required />
          </label>
          <label>
            Электричество, кВт·ч
            <input v-model.number="form.electric_value" type="number" step="0.1" min="0" required />
          </label>
        </div>
        <div class="form-actions">
          <button type="submit" class="primary">Сохранить</button>
          <button type="button" @click="closeForm">Отмена</button>
        </div>
      </form>
    </div>

    <div class="card table-card">
      <h2>История показаний <span class="count-pill">{{ readings.length }}</span></h2>
      <div v-if="loading" class="loading"><span class="spinner"></span> Загрузка…</div>
      <div class="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Период</th>
              <th>ХВС, м³</th>
              <th>ГВС, м³</th>
              <th>Эл-во, кВт·ч</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in readings" :key="r.id">
              <td class="period-cell">{{ formatPeriod(r.period) }}</td>
              <td>{{ r.xvs_value.toFixed(3) }}</td>
              <td>{{ r.gvs_value.toFixed(3) }}</td>
              <td>{{ r.electric_value.toFixed(1) }}</td>
              <td>
                <button class="icon-btn" aria-label="Редактировать" title="Редактировать" @click="edit(r)">
                  <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21.174 6.812a1.5 1.5 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497Z" />
                  </svg>
                </button>
                <button class="icon-btn danger" aria-label="Удалить" title="Удалить" @click="remove(r.id)">
                  <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6M6 6V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v2" />
                    <path d="M10 11v6M14 11v6" />
                  </svg>
                </button>
              </td>
            </tr>
            <tr v-if="!readings.length && !loading">
              <td colspan="5" class="table-empty">
                За выбранный год нет показаний. Добавьте первое показание.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api, type Reading } from '../api'

const selectedYear = ref(0)
const availableYears = ref<number[]>([])
const readings = ref<Reading[]>([])
const loading = ref(false)
const error = ref('')
const showForm = ref(false)
const editingId = ref<number | null>(null)

async function loadYears() {
  availableYears.value = await api.getReadingYears()
  if (availableYears.value.length) {
    if (!availableYears.value.includes(selectedYear.value)) {
      selectedYear.value = availableYears.value[availableYears.value.length - 1]
    }
  } else {
    selectedYear.value = 0
  }
}

function chooseYear(y: number) {
  selectedYear.value = y
  loadData()
}

const form = ref({
  period: new Date().toISOString().slice(0, 10),
  xvs_value: 0,
  gvs_value: 0,
  electric_value: 0,
})

function formatPeriod(period: string): string {
  const MONTHS_RU = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
  const date = new Date(period)
  return `${MONTHS_RU[date.getMonth()]} ${date.getFullYear()}`
}

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    readings.value = await api.getReadings(selectedYear.value || undefined)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Не удалось загрузить данные'
  } finally {
    loading.value = false
  }
}

function toggleForm() {
  showForm.value = !showForm.value
  editingId.value = null
}

function closeForm() {
  showForm.value = false
  editingId.value = null
}

function edit(reading: Reading) {
  editingId.value = reading.id
  form.value = {
    period: reading.period,
    xvs_value: reading.xvs_value,
    gvs_value: reading.gvs_value,
    electric_value: reading.electric_value,
  }
  showForm.value = true
}

async function save() {
  error.value = ''
  try {
    if (editingId.value) {
      await api.updateReading(editingId.value, {
        period: form.value.period,
        xvs_value: form.value.xvs_value,
        gvs_value: form.value.gvs_value,
        electric_value: form.value.electric_value,
      })
    } else {
      await api.createReading(form.value)
    }
    closeForm()
    await loadData()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Не удалось сохранить'
  }
}

async function remove(id: number) {
  if (!window.confirm('Удалить это показание?')) return
  error.value = ''
  try {
    await api.deleteReading(id)
    await loadData()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Не удалось удалить'
  }
}

onMounted(async () => {
  await loadYears()
  await loadData()
})
</script>

<style scoped>
.period-cell {
  font-weight: 650;
  white-space: nowrap;
}
</style>
