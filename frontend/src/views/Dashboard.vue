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
        <div v-if="chartPoints.length" class="chart-box">
          <svg
            :viewBox="`0 0 ${CHART_W} ${CHART_H}`"
            class="chart-svg"
            role="img"
            aria-label="График изменения суммарной оплаты квартиры по месяцам"
          >
            <defs>
              <linearGradient id="chartAreaFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0" stop-color="#6366f1" stop-opacity="0.18" />
                <stop offset="1" stop-color="#6366f1" stop-opacity="0" />
              </linearGradient>
              <linearGradient id="chartLineGrad" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0" stop-color="#6366f1" />
                <stop offset="1" stop-color="#8b5cf6" />
              </linearGradient>
            </defs>

            <line
              v-for="g in chartGrid"
              :key="`grid-${g.y}`"
              :x1="PAD_LEFT"
              :x2="CHART_W - PAD_RIGHT"
              :y1="g.y"
              :y2="g.y"
              class="chart-grid"
            />
            <text
              v-for="g in chartGrid"
              :key="`glabel-${g.y}`"
              :x="PAD_LEFT - 6"
              :y="g.y + 4"
              text-anchor="end"
              class="chart-axis"
            >{{ formatCompact(g.value) }}</text>

            <path :d="chartAreaPath" fill="url(#chartAreaFill)" />
            <path :d="chartLinePath" fill="none" stroke="url(#chartLineGrad)" class="chart-line" />

            <circle
              v-for="p in chartPoints"
              :key="p.month"
              :cx="p.x"
              :cy="p.y"
              r="4.5"
              class="chart-dot"
              @mouseenter="onPointEnter(p, $event)"
              @mouseleave="onPointLeave"
            ></circle>
            <text
              v-for="p in chartPoints"
              :key="`plabel-${p.month}`"
              :x="p.x"
              :y="CHART_H - PAD_BOTTOM + 18"
              text-anchor="middle"
              class="chart-axis chart-month"
            >{{ p.month }}</text>
          </svg>

          <div
            v-if="tooltip"
            class="chart-tooltip"
            :style="{ left: tooltip.x + 14 + 'px', top: tooltip.y + 14 + 'px' }"
          >
            <p class="tip-title">{{ tooltip.month }} {{ tooltip.year }}</p>
            <p class="tip-value">{{ formatMoney(tooltip.value) }} ₽</p>
          </div>
        </div>
        <p v-else class="empty-note">Нет данных для графика за выбранный год</p>
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
                <th>Пометка</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in summary.months" :key="m.period">
                <td class="month-cell">{{ formatMonth(m.period) }}</td>
                <td>{{ m.hws_consumption.toFixed(2) }}</td>
                <td>{{ m.cws_consumption.toFixed(2) }}</td>
                <td>{{ m.electric_consumption.toFixed(0) }}</td>
                <td>{{ formatMoney(m.hws_cost) }}</td>
                <td>{{ formatMoney(m.cws_cost) }}</td>
                <td>{{ formatMoney(m.electric_cost) }}</td>
                <td>{{ formatMoney(m.rent) }}</td>
                <td class="cell-total">{{ formatMoney(m.total) }}</td>
                <td>{{ m.note || '—' }}</td>
              </tr>
              <tr v-if="!summary.months.length">
                <td colspan="10" class="table-empty">Нет данных за выбранный год</td>
              </tr>
            </tbody>
            <tfoot v-if="summary.months.length">
              <tr>
                <td>Итого за год</td>
                <td></td>
                <td></td>
                <td></td>
                <td>{{ formatMoney(summary.total_hws_cost) }}</td>
                <td>{{ formatMoney(summary.total_cws_cost) }}</td>
                <td>{{ formatMoney(summary.total_electric_cost) }}</td>
                <td>{{ formatMoney(summary.total_rent) }}</td>
                <td class="cell-total">{{ formatMoney(summary.grand_total) }}</td>
                <td></td>
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
    ? summary.value.total_hws_cost + summary.value.total_cws_cost + summary.value.total_electric_cost
    : 0
)

// --- Monthly chart ---
const CHART_W = 640
const CHART_H = 280
const PAD_LEFT = 52
const PAD_RIGHT = 16
const PAD_TOP = 16
const PAD_BOTTOM = 34
const BASELINE_Y = CHART_H - PAD_BOTTOM

const chartAreaW = computed(() => CHART_W - PAD_LEFT - PAD_RIGHT)
const chartAreaH = computed(() => CHART_H - PAD_TOP - PAD_BOTTOM)

const monthTotals = computed(() => (summary.value?.months ?? []).map((m) => m.total))

// Scale the y-axis from the data range (plus a little headroom) instead of from 0,
// so month-to-month differences are actually visible.
const yMin = computed(() => {
  const t = monthTotals.value
  if (!t.length) return 0
  const mn = Math.min(...t)
  const mx = Math.max(...t)
  if (mx === mn) return mn - 1
  return Math.max(0, mn - (mx - mn) * 0.15)
})
const yMax = computed(() => {
  const t = monthTotals.value
  if (!t.length) return 1
  const mn = Math.min(...t)
  const mx = Math.max(...t)
  if (mx === mn) return mx + 1
  return mx + (mx - mn) * 0.1
})
const ySpan = computed(() => yMax.value - yMin.value || 1)

const chartPoints = computed(() => {
  const months = summary.value?.months ?? []
  const span = ySpan.value
  const n = months.length || 1
  const slotW = chartAreaW.value / n
  return months.map((m, i) => {
    const x = PAD_LEFT + slotW * i + slotW / 2
    const y = PAD_TOP + chartAreaH.value - ((m.total - yMin.value) / span) * chartAreaH.value
    return { x, y, value: m.total, month: MONTHS_RU[new Date(m.period).getMonth()] }
  })
})

// <path> accepts M/L commands, unlike <polyline> which only accepts plain coordinate pairs.
const chartLinePath = computed(() =>
  chartPoints.value
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`)
    .join(' ')
)

const chartAreaPath = computed(() => {
  const pts = chartPoints.value
  if (pts.length < 2) return ''
  const head = pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
  return `${head} L ${pts[pts.length - 1].x} ${BASELINE_Y} L ${pts[0].x} ${BASELINE_Y} Z`
})

const chartGrid = computed(() => {
  const lines = []
  const steps = 4
  const span = ySpan.value
  for (let i = 0; i <= steps; i++) {
    const value = yMin.value + (span / steps) * i
    const y = PAD_TOP + chartAreaH.value - ((value - yMin.value) / span) * chartAreaH.value
    lines.push({ y, value })
  }
  return lines
})

function formatMoney(value: number): string {
  return value.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatCompact(value: number): string {
  const abs = Math.abs(value)
  if (abs >= 1000) {
    return `${(value / 1000).toFixed(abs >= 10000 ? 0 : 1)}k`
  }
  return value.toFixed(0)
}

function formatMonth(period: string): string {
  const date = new Date(period)
  return `${MONTHS_RU[date.getMonth()]} ${date.getFullYear()}`
}

// Hover tooltip for the chart
interface ChartTooltip {
  x: number
  y: number
  month: string
  value: number
  year: number
}
const tooltip = ref<ChartTooltip | null>(null)

function onPointEnter(p: { month: string; value: number; x: number; y: number }, ev: MouseEvent) {
  tooltip.value = {
    x: ev.clientX,
    y: ev.clientY,
    month: p.month,
    value: p.value,
    year: selectedYear.value,
  }
}

function onPointLeave() {
  tooltip.value = null
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
.chart-box {
  position: relative;
}

.chart-svg {
  width: 100%;
  height: auto;
  display: block;
  overflow: visible;
}

.chart-grid {
  stroke: var(--border);
  stroke-width: 1;
  stroke-dasharray: 3 6;
}

.chart-axis {
  fill: var(--text-faint);
  font-size: 11px;
}

.chart-month {
  font-weight: 600;
}

.chart-line {
  stroke-width: 2.6;
  stroke-linecap: round;
  stroke-linejoin: round;
  filter: drop-shadow(0 8px 12px var(--accent-glow));
}

.chart-dot {
  fill: var(--surface);
  stroke: var(--brand-1);
  stroke-width: 2.2;
  cursor: pointer;
  transition: fill 0.15s ease;
}

.chart-dot:hover {
  fill: var(--brand-1);
  stroke: var(--surface);
}

.chart-tooltip {
  position: fixed;
  z-index: 50;
  pointer-events: none;
  min-width: 130px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--brand-1);
  border-radius: 10px;
  padding: 7px 12px;
  box-shadow: var(--shadow-s);
}

.chart-tooltip p {
  margin: 0;
}

.tip-title {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.tip-value {
  font-size: 1rem;
  font-weight: 750;
  font-variant-numeric: tabular-nums;
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
