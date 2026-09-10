<template>
  <div>
    <div class="page-head">
      <div>
        <h1 class="page-title">Обзор</h1>
        <p class="page-sub">Динамика расходов на квартиру</p>
      </div>
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
    </div>

    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="loading && !summary" class="loading"><span class="spinner"></span> Загрузка данных…</div>

    <p v-if="!loading && !summary && !error" class="empty-note">
      Добавьте первые показания на странице «Показания», чтобы увидеть расчёты.
    </p>

    <template v-if="summary">
      <div class="stats-grid">
        <article class="stat tone-indigo">
          <span class="stat-chip">
            <svg viewBox="0 0 24 24" width="21" height="21" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M21 12V7H5a2 2 0 0 1 0-4h14v4" />
              <path d="M3 5v14a2 2 0 0 0 2 2h16v-5" />
              <path d="M18 12a2 2 0 0 0 0 4h4v-4Z" />
            </svg>
          </span>
          <div class="stat-info">
            <p class="stat-label">Итого за год</p>
            <p class="stat-value">{{ formatMoney(summary.grand_total) }} <small>₽</small></p>
            <p class="stat-note">Все ресурсы и аренда</p>
          </div>
        </article>

        <article class="stat tone-teal">
          <span class="stat-chip">
            <svg viewBox="0 0 24 24" width="21" height="21" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="m22 7-8.5 8.5-5-5L2 17" />
              <path d="M16 7h6v6" />
            </svg>
          </span>
          <div class="stat-info">
            <p class="stat-label">Средний платёж в месяц</p>
            <p class="stat-value">{{ formatMoney(avgMonthly) }} <small>₽</small></p>
            <p class="stat-note">Из периодов с данными</p>
          </div>
        </article>

        <article class="stat tone-sky">
          <span class="stat-chip">
            <svg viewBox="0 0 24 24" width="21" height="21" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M12 2.7S6.5 8 6.5 13a5.5 5.5 0 0 0 11 0C17.5 8 12 2.7 12 2.7Z" />
            </svg>
          </span>
          <div class="stat-info">
            <p class="stat-label">Коммунальные услуги</p>
            <p class="stat-value">{{ formatMoney(utilitiesTotal) }} <small>₽</small></p>
            <p class="stat-note">ХВС + ГВС + электричество</p>
          </div>
        </article>

        <article class="stat tone-rose">
          <span class="stat-chip">
            <svg viewBox="0 0 24 24" width="21" height="21" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M2 7h20v10H2Z" />
              <path d="M5 17c0-1.38-1.12-2.5-2.5-2.5" />
              <path d="M5 7c0 1.38-1.12 2.5-2.5 2.5" />
              <path d="M19 17c0-1.38 1.12-2.5 2.5-2.5" />
              <path d="M19 7c0 1.38 1.12 2.5 2.5 2.5" />
              <path d="M12 10.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3Z" />
            </svg>
          </span>
          <div class="stat-info">
            <p class="stat-label">Аренда за год</p>
            <p class="stat-value">{{ formatMoney(summary.total_rent) }} <small>₽</small></p>
            <p class="stat-note">Фиксированный платёж</p>
          </div>
        </article>
      </div>

      <div class="card chart-card">
        <h2>Сумма по месяцам</h2>
        <LineChart
          :points="costPoints"
          unit="₽"
          :year="selectedYear"
          :ariaLabel="'График изменения суммарной оплаты квартиры по месяцам'"
        />
      </div>

      <div class="card chart-card">
        <h2>
          Расход по месяцам
          <span class="segmented chart-switch" role="group" aria-label="Выбор коммунальной услуги">
            <button
              v-for="r in RESOURCES"
              :key="r.key"
              :class="{ active: selectedResource === r.key }"
              :aria-pressed="selectedResource === r.key"
              @click="selectedResource = r.key"
            >{{ r.label }}</button>
          </span>
        </h2>
        <LineChart
          :points="consumptionPoints"
          :unit="activeResource.unit"
          :decimals="activeResource.decimals"
          :color-from="activeResource.colorFrom"
          :color-to="activeResource.colorTo"
          :year="selectedYear"
          :ariaLabel="`График расхода ${activeResource.fullLabel} по месяцам`"
        />
      </div>

      <div class="card table-card">
        <h2>Расходы по месяцам</h2>
        <div class="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Месяц</th>
                <th>ХВС, м³</th>
                <th>ГВС, м³</th>
                <th>Эл-во, кВт·ч</th>
                <th>ХВС, ₽</th>
                <th>ГВС, ₽</th>
                <th>Эл-во, ₽</th>
                <th>Аренда, ₽</th>
                <th>Итого, ₽</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in summary.months" :key="m.period">
                <td class="month-cell">{{ formatMonth(m.period) }}</td>
                <td>{{ m.xvs_consumption.toFixed(2) }}</td>
                <td>{{ m.gvs_consumption.toFixed(2) }}</td>
                <td>{{ m.electric_consumption.toFixed(0) }}</td>
                <td>{{ formatMoney(m.xvs_cost) }}</td>
                <td>{{ formatMoney(m.gvs_cost) }}</td>
                <td>{{ formatMoney(m.electric_cost) }}</td>
                <td>{{ formatMoney(m.rent) }}</td>
                <td class="cell-total">{{ formatMoney(m.total) }}</td>
              </tr>
              <tr v-if="!summary.months.length">
                <td colspan="9" class="table-empty">Нет данных за выбранный год</td>
              </tr>
            </tbody>
            <tfoot v-if="summary.months.length">
              <tr>
                <td>Итого за год</td>
                <td></td>
                <td></td>
                <td></td>
                <td>{{ formatMoney(summary.total_xvs_cost) }}</td>
                <td>{{ formatMoney(summary.total_gvs_cost) }}</td>
                <td>{{ formatMoney(summary.total_electric_cost) }}</td>
                <td>{{ formatMoney(summary.total_rent) }}</td>
                <td class="cell-total">{{ formatMoney(summary.grand_total) }}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { api, type YearSummary } from '../api'
import LineChart from '../components/LineChart.vue'

const MONTHS_RU = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']

const selectedYear = ref(0)
const availableYears = ref<number[]>([])
const summary = ref<YearSummary | null>(null)
const loading = ref(false)
const error = ref('')

async function loadYears() {
  try {
    availableYears.value = await api.getReadingYears()
  } catch {
    availableYears.value = []
  }
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

async function loadData() {
  if (!selectedYear.value) return
  loading.value = true
  error.value = ''
  try {
    summary.value = await api.getSummary(selectedYear.value)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Не удалось загрузить данные'
  } finally {
    loading.value = false
  }
}

const avgMonthly = computed(() =>
  summary.value?.months.length
    ? summary.value.grand_total / summary.value.months.length
    : 0
)

const utilitiesTotal = computed(() =>
  summary.value
    ? summary.value.total_xvs_cost + summary.value.total_gvs_cost + summary.value.total_electric_cost
    : 0
)

// --- Charts ---
const costPoints = computed(() =>
  (summary.value?.months ?? []).map((m) => ({
    label: MONTHS_RU[new Date(m.period).getMonth()],
    value: m.total,
  }))
)

type ResourceKey = 'xvs' | 'gvs' | 'electric'

interface ResourceConfig {
  key: ResourceKey
  label: string
  fullLabel: string
  field: 'xvs_consumption' | 'gvs_consumption' | 'electric_consumption'
  unit: string
  decimals: number
  colorFrom: string
  colorTo: string
}

// Display order and units follow the monthly table below.
const RESOURCES: ResourceConfig[] = [
  {
    key: 'xvs',
    label: 'ХВС',
    fullLabel: 'холодной воды',
    field: 'xvs_consumption',
    unit: 'м³',
    decimals: 2,
    colorFrom: '#0284c7',
    colorTo: '#38bdf8',
  },
  {
    key: 'gvs',
    label: 'ГВС',
    fullLabel: 'горячей воды',
    field: 'gvs_consumption',
    unit: 'м³',
    decimals: 2,
    colorFrom: '#e11d48',
    colorTo: '#fb7185',
  },
  {
    key: 'electric',
    label: 'Электро',
    fullLabel: 'электроэнергии',
    field: 'electric_consumption',
    unit: 'кВт·ч',
    decimals: 0,
    colorFrom: '#6366f1',
    colorTo: '#8b5cf6',
  },
]

const selectedResource = ref<ResourceKey>('xvs')
const activeResource = computed(
  () => RESOURCES.find((r) => r.key === selectedResource.value) ?? RESOURCES[0]
)

const consumptionPoints = computed(() =>
  (summary.value?.months ?? []).map((m) => ({
    label: MONTHS_RU[new Date(m.period).getMonth()],
    value: m[activeResource.value.field],
  }))
)

function formatMoney(value: number): string {
  return value.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatMonth(period: string): string {
  const date = new Date(period)
  return `${MONTHS_RU[date.getMonth()]} ${date.getFullYear()}`
}

onMounted(async () => {
  await loadYears()
  await loadData()
})
</script>

<style scoped>
/* Stat cards */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 18px;
}

.stat {
  position: relative;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-m);
  box-shadow: var(--shadow-xs);
  overflow: hidden;
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}

.stat::after {
  content: '';
  position: absolute;
  top: -40px;
  right: -40px;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--tone-2) 14%, transparent);
  pointer-events: none;
}

.stat:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-m);
  border-color: color-mix(in srgb, var(--tone-1) 30%, var(--border));
}

.tone-indigo {
  --tone-1: #6366f1;
  --tone-2: #8b5cf6;
}
.tone-teal {
  --tone-1: #0d9488;
  --tone-2: #14b8a6;
}
.tone-sky {
  --tone-1: #0284c7;
  --tone-2: #38bdf8;
}
.tone-rose {
  --tone-1: #e11d48;
  --tone-2: #fb7185;
}

.stat-chip {
  flex: none;
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  border-radius: 14px;
  color: #fff;
  background: linear-gradient(135deg, var(--tone-1), var(--tone-2));
  box-shadow: 0 10px 18px -8px color-mix(in srgb, var(--tone-2) 55%, transparent);
}

.stat-info {
  min-width: 0;
}

.stat p {
  margin: 0;
}

.stat-label {
  font-size: 0.82rem;
  color: var(--text-muted);
  font-weight: 600;
  white-space: nowrap;
}

.stat-value {
  margin-top: 2px;
  font-size: 1.32rem;
  font-weight: 750;
  letter-spacing: -0.01em;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.stat-value small {
  font-size: 0.62em;
  font-weight: 650;
  color: var(--text-muted);
  margin-left: 2px;
}

.stat-note {
  margin-top: 3px;
  font-size: 0.78rem;
  color: var(--text-faint);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Chart */
.chart-card > h2 {
  flex-wrap: wrap;
}

.chart-switch {
  margin-left: auto;
  font-weight: 600;
}

/* Monthly table */
.month-cell {
  font-weight: 650;
  white-space: nowrap;
}

.cell-total {
  color: var(--accent);
  font-weight: 700;
}

@media (max-width: 1080px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 560px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
