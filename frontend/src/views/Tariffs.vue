<template>
  <div>
    <div class="page-head">
      <div>
        <h1 class="page-title">Тарифы</h1>
        <p class="page-sub">Ставки для расчёта стоимости ресурсов и аренды</p>
      </div>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <div class="card">
      <h2>Действующие тарифы</h2>
      <div v-if="loading" class="loading"><span class="spinner"></span> Загрузка…</div>
      <div v-else-if="tiles.length" class="tile-grid">
        <div v-for="t in tiles" :key="t.id" class="tariff-tile" :class="`tone-${t.tone}`">
          <span class="tile-chip">
            <svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path :d="t.icon" />
            </svg>
          </span>
          <div class="tile-body">
            <p class="tile-name">{{ t.name }}</p>
            <p class="tile-rate">
              {{ t.rate }} <small>₽</small>
              <span class="tile-unit">/ {{ t.unit }}</span>
            </p>
            <p class="tile-from">действует с {{ t.from }}</p>
          </div>
        </div>
      </div>
      <p v-else class="empty-note">
        Тарифы пока не заданы — добавьте первый тариф ниже.
      </p>
    </div>

    <div class="card">
      <h2>Обновить тариф</h2>
      <form @submit.prevent="save">
        <div class="form-grid">
          <label>
            Ресурс
            <select v-model="form.resource_type">
              <option value="hws">ХВС — холодная вода</option>
              <option value="cws">ГВС — горячая вода</option>
              <option value="electric">Электричество</option>
              <option value="rent">Аренда</option>
            </select>
          </label>
          <label>
            Ставка, ₽
            <input v-model.number="form.rate" type="number" step="0.01" min="0.01" required />
          </label>
          <label>
            Действует с
            <input v-model="form.effective_from" type="date" required />
          </label>
        </div>
        <div class="form-actions">
          <button type="submit" class="primary">Сохранить тариф</button>
        </div>
      </form>
    </div>

    <div class="card table-card">
      <h2>История тарифов <span class="count-pill">{{ tariffs.length }}</span></h2>
      <div class="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Ресурс</th>
              <th>Ставка</th>
              <th>Действует с</th>
              <th>По</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in tariffs" :key="t.id">
              <td>{{ resourceNames[t.resource_type] || t.resource_type }}</td>
              <td>{{ t.rate }} ₽</td>
              <td>{{ formatDate(t.effective_from) }}</td>
              <td>{{ t.effective_to ? formatDate(t.effective_to) : '—' }}</td>
            </tr>
            <tr v-if="!tariffs.length && !loading">
              <td colspan="4" class="table-empty">Тарифов пока нет</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { api, type Tariff } from '../api'

const resourceNames: Record<string, string> = {
  hws: 'ХВС (холодная вода)',
  cws: 'ГВС (горячая вода)',
  electric: 'Электричество',
  rent: 'Аренда',
}

type Resource = Tariff['resource_type']

const meta: Record<Resource, { name: string; unit: string; tone: string; icon: string }> = {
  hws: {
    name: 'ХВС — холодная вода',
    unit: 'м³',
    tone: 'sky',
    icon: 'M12 2.7S6.5 8 6.5 13a5.5 5.5 0 0 0 11 0C17.5 8 12 2.7 12 2.7Z',
  },
  cws: {
    name: 'ГВС — горячая вода',
    unit: 'м³',
    tone: 'rose',
    icon: 'M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z',
  },
  electric: {
    name: 'Электричество',
    unit: 'кВт·ч',
    tone: 'amber',
    icon: 'M13 2 3 14h9l-1 8 10-12h-9l1-8Z',
  },
  rent: {
    name: 'Аренда',
    unit: 'мес',
    tone: 'violet',
    icon: 'M2 7h20v10H2ZM5 17c0-1.38-1.12-2.5-2.5-2.5M5 7c0 1.38-1.12 2.5-2.5 2.5M19 17c0-1.38 1.12-2.5 2.5-2.5M19 7c0 1.38 1.12 2.5 2.5 2.5M12 10.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3Z',
  },
}

const tariffs = ref<Tariff[]>([])
const loading = ref(false)
const error = ref('')

const activeTariffs = computed(() => tariffs.value.filter((t) => !t.effective_to))

interface TariffTile {
  id: number
  name: string
  unit: string
  tone: string
  icon: string
  rate: string
  from: string
}

const tiles = computed<TariffTile[]>(() =>
  activeTariffs.value.map((t) => {
    const m = meta[t.resource_type]
    return {
      id: t.id,
      name: m.name,
      unit: m.unit,
      tone: m.tone,
      icon: m.icon,
      rate: t.rate.toLocaleString('ru-RU', { maximumFractionDigits: 3 }),
      from: formatDate(t.effective_from),
    }
  })
)

function formatDate(value: string): string {
  const d = new Date(value)
  return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const form = ref({
  resource_type: 'hws' as Resource,
  rate: 0,
  effective_from: new Date().toISOString().slice(0, 10),
})

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    tariffs.value = await api.getTariffs()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Не удалось загрузить тарифы'
  } finally {
    loading.value = false
  }
}

async function save() {
  error.value = ''
  try {
    await api.upsertTariff(form.value)
    await loadData()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Не удалось сохранить тариф'
  }
}

onMounted(loadData)
</script>

<style scoped>
/* Active tariffs tiles */
.tile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 14px;
}

.tariff-tile {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-m);
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}

.tariff-tile:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-s);
  border-color: color-mix(in srgb, var(--tone-1) 35%, var(--border));
}

.tone-sky {
  --tone-1: #0284c7;
  --tone-2: #38bdf8;
}
.tone-rose {
  --tone-1: #e11d48;
  --tone-2: #fb7185;
}
.tone-amber {
  --tone-1: #d97706;
  --tone-2: #f59e0b;
}
.tone-violet {
  --tone-1: #4f46e5;
  --tone-2: #7c3aed;
}

.tile-chip {
  flex: none;
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 12px;
  color: #fff;
  background: linear-gradient(135deg, var(--tone-1), var(--tone-2));
  box-shadow: 0 8px 16px -8px color-mix(in srgb, var(--tone-2) 55%, transparent);
}

.tile-body {
  min-width: 0;
}

.tile-name {
  margin: 0;
  font-size: 0.84rem;
  font-weight: 650;
  color: var(--text-muted);
}

.tile-rate {
  margin: 2px 0 0;
  font-size: 1.2rem;
  font-weight: 750;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.01em;
}

.tile-rate small {
  font-size: 0.65em;
  color: var(--text-muted);
}

.tile-unit {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-faint);
}

.tile-from {
  margin: 3px 0 0;
  font-size: 0.78rem;
  color: var(--text-faint);
}
</style>
