<script lang="ts">
// Module-scope counter: every chart instance needs its own SVG gradient ids.
// Duplicated ids would make both charts render the first instance's gradient.
let chartUid = 0
</script>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface ChartPoint {
  label: string
  value: number
}

const props = withDefaults(
  defineProps<{
    points: ChartPoint[]
    unit: string
    ariaLabel: string
    year: number
    colorFrom?: string
    colorTo?: string
    decimals?: number
    emptyText?: string
  }>(),
  {
    colorFrom: '#6366f1',
    colorTo: '#8b5cf6',
    decimals: 2,
    emptyText: 'Нет данных для графика за выбранный год',
  }
)

const uid = chartUid++
const areaFillId = `chartAreaFill-${uid}`
const lineGradId = `chartLineGrad-${uid}`

const CHART_W = 640
const CHART_H = 280
const PAD_LEFT = 52
const PAD_RIGHT = 16
const PAD_TOP = 16
const PAD_BOTTOM = 34
const BASELINE_Y = CHART_H - PAD_BOTTOM

const chartAreaW = CHART_W - PAD_LEFT - PAD_RIGHT
const chartAreaH = CHART_H - PAD_TOP - PAD_BOTTOM

const values = computed(() => props.points.map((p) => p.value))

// Scale the y-axis from the data range (plus a little headroom) instead of from 0,
// so month-to-month differences are actually visible.
const yMin = computed(() => {
  const t = values.value
  if (!t.length) return 0
  const mn = Math.min(...t)
  const mx = Math.max(...t)
  if (mx === mn) return mn - 1
  return Math.max(0, mn - (mx - mn) * 0.15)
})
const yMax = computed(() => {
  const t = values.value
  if (!t.length) return 1
  const mn = Math.min(...t)
  const mx = Math.max(...t)
  if (mx === mn) return mx + 1
  return mx + (mx - mn) * 0.1
})
const ySpan = computed(() => yMax.value - yMin.value || 1)

const chartPoints = computed(() => {
  const span = ySpan.value
  const n = props.points.length || 1
  const slotW = chartAreaW / n
  return props.points.map((p, i) => {
    const x = PAD_LEFT + slotW * i + slotW / 2
    const y = PAD_TOP + chartAreaH - ((p.value - yMin.value) / span) * chartAreaH
    return { x, y, value: p.value, label: p.label }
  })
})

// <path> accepts M/L commands, unlike <polyline> which only accepts plain coordinate pairs.
const chartLinePath = computed(() =>
  chartPoints.value.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
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
    const y = PAD_TOP + chartAreaH - ((value - yMin.value) / span) * chartAreaH
    lines.push({ y, value })
  }
  return lines
})

function formatValue(value: number): string {
  return value.toLocaleString('ru-RU', {
    minimumFractionDigits: props.decimals,
    maximumFractionDigits: props.decimals,
  })
}

function formatCompact(value: number): string {
  const abs = Math.abs(value)
  if (abs >= 1000) {
    return `${(value / 1000).toFixed(abs >= 10000 ? 0 : 1)}k`
  }
  if (abs < 10 && props.decimals > 0) return value.toFixed(1)
  return value.toFixed(0)
}

// Hover tooltip for the chart
interface ChartTooltip {
  x: number
  y: number
  label: string
  value: number
}
const tooltip = ref<ChartTooltip | null>(null)

function onPointEnter(p: { label: string; value: number }, ev: MouseEvent) {
  tooltip.value = {
    x: ev.clientX,
    y: ev.clientY,
    label: p.label,
    value: p.value,
  }
}

function onPointLeave() {
  tooltip.value = null
}
</script>

<template>
  <div v-if="points.length" class="chart-box" :style="{ '--chart-color': colorFrom }">
    <svg
      :viewBox="`0 0 ${CHART_W} ${CHART_H}`"
      class="chart-svg"
      role="img"
      :aria-label="ariaLabel"
    >
      <defs>
        <linearGradient :id="areaFillId" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" :stop-color="colorFrom" stop-opacity="0.18" />
          <stop offset="1" :stop-color="colorFrom" stop-opacity="0" />
        </linearGradient>
        <linearGradient :id="lineGradId" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" :stop-color="colorFrom" />
          <stop offset="1" :stop-color="colorTo" />
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

      <path :d="chartAreaPath" :fill="`url(#${areaFillId})`" />
      <path :d="chartLinePath" fill="none" :stroke="`url(#${lineGradId})`" class="chart-line" />

      <circle
        v-for="p in chartPoints"
        :key="p.label"
        :cx="p.x"
        :cy="p.y"
        r="4.5"
        class="chart-dot"
        @mouseenter="onPointEnter(p, $event)"
        @mouseleave="onPointLeave"
      ></circle>
      <text
        v-for="p in chartPoints"
        :key="`plabel-${p.label}`"
        :x="p.x"
        :y="CHART_H - PAD_BOTTOM + 18"
        text-anchor="middle"
        class="chart-axis chart-month"
      >{{ p.label }}</text>
    </svg>

    <div
      v-if="tooltip"
      class="chart-tooltip"
      :style="{ left: tooltip.x + 14 + 'px', top: tooltip.y + 14 + 'px' }"
    >
      <p class="tip-title">{{ tooltip.label }} {{ year }}</p>
      <p class="tip-value">{{ formatValue(tooltip.value) }} {{ unit }}</p>
    </div>
  </div>
  <p v-else class="empty-note">{{ emptyText }}</p>
</template>

<style scoped>
.chart-box {
  position: relative;
  --chart-color: #6366f1;
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
  stroke: var(--chart-color);
  stroke-width: 2.2;
  cursor: pointer;
  transition: fill 0.15s ease;
}

.chart-dot:hover {
  fill: var(--chart-color);
  stroke: var(--surface);
}

.chart-tooltip {
  position: fixed;
  z-index: 50;
  pointer-events: none;
  min-width: 130px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--chart-color);
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
</style>
