<template>
  <div class="chart-card anim-fade-up" style="animation-delay: 300ms">
    <div class="chart-card-header">
      <h3 class="chart-card-title">{{ loc.t.charts.dailyTrend }}</h3>
      <div class="chart-header-right">
        <div class="chart-legend">
          <span class="legend-dot legend-input"></span>
          <span class="legend-label">{{ loc.t.charts.input }}</span>
          <span class="legend-dot legend-output"></span>
          <span class="legend-label">{{ loc.t.charts.output }}</span>
          <template v-if="showCostOverlay && selectedMetric === 'tokens'">
            <span class="legend-dot legend-cost"></span>
            <span class="legend-label">{{ loc.t.charts.cost }}</span>
          </template>
        </div>
        <div class="chart-type-switcher">
          <button
            v-for="opt in metricOptions"
            :key="opt.key"
            class="type-btn"
            :class="{ active: selectedMetric === opt.key }"
            @click="selectedMetric = opt.key"
          >
            {{ opt.label }}
          </button>
        </div>
        <button
          v-if="selectedMetric === 'tokens'"
          class="type-btn cost-toggle"
          :class="{ active: showCostOverlay }"
          @click="showCostOverlay = !showCostOverlay"
        >
          💲 {{ loc.t.charts.showCostOverlay }}
        </button>
        <div class="chart-type-switcher">
          <button
            v-for="opt in typeOptions"
            :key="opt.key"
            class="type-btn"
            :class="{ active: selectedType === opt.key }"
            @click="selectedType = opt.key"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>
    </div>
    <div v-if="store.dailySummary.length === 0" class="chart-empty">
      <el-empty :description="loc.t.charts.noData" />
    </div>
    <v-chart
      v-show="store.dailySummary.length > 0"
      :option="chartOption"
      :autoresize="true"
      class="chart-instance"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import * as echarts from 'echarts/core'
import { useTokenRecordsStore } from '../stores/tokenRecords'
import { useLocaleStore } from '../stores/locale'
import { useChartColors } from '../composables/useChartColors'

type ChartType = 'area' | 'line' | 'bar'
type Metric = 'tokens' | 'cost'

const store = useTokenRecordsStore()
const loc = useLocaleStore()
const c = useChartColors()
const selectedType = ref<ChartType>('area')
const selectedMetric = ref<Metric>('tokens')
const showCostOverlay = ref(false)

const typeOptions = computed(() => [
  { key: 'area' as ChartType, label: loc.t.charts.typeArea },
  { key: 'line' as ChartType, label: loc.t.charts.typeLine },
  { key: 'bar' as ChartType, label: loc.t.charts.typeBar },
])

const metricOptions = computed(() => [
  { key: 'tokens' as Metric, label: loc.t.charts.metricTokens },
  { key: 'cost' as Metric, label: loc.t.charts.metricCost },
])

const fmt = (v: number) => {
  if (selectedMetric.value === 'cost') return '$' + v.toFixed(v >= 10 ? 1 : 4)
  if (v >= 1_000_000) return (v / 1_000_000).toFixed(1) + 'M'
  if (v >= 1_000) return (v / 1_000).toFixed(0) + 'K'
  return String(v)
}

const baseTooltip = computed(() => ({
  trigger: 'axis' as const,
  backgroundColor: c.tooltipBg.value,
  borderColor: c.tooltipBorder.value,
  borderWidth: 1,
  borderRadius: 18,
  padding: [14, 18],
  extraCssText: c.tooltipExtraCss.value,
  textStyle: {
    color: c.tooltipText.value,
    fontSize: 13,
    fontFamily:
      "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  },
  formatter: (params: any[]) => {
    const raw = params[0]?.axisValue || ''
    const p = raw.split('-')
    const date = p.length === 3 ? parseInt(p[1]) + '.' + parseInt(p[2]) : raw
    let html = `<div style="font-weight:600;font-size:14px;margin-bottom:8px;color:${c.tooltipText.value};">${date}</div>`
    for (const p of params) {
      const isCost = p.seriesName === loc.t.charts.cost
      const val = isCost ? ('$' + (p.value >= 1 ? p.value.toFixed(2) : p.value.toFixed(4))) : fmt(p.value)
      html += `<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
        <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${p.color};"></span>
        <span style="color:${c.tooltipTextSecondary.value};">${p.seriesName}</span>
        <span style="font-weight:600;margin-left:auto;color:${c.tooltipText.value};">${val}</span>
      </div>`
    }
    return html
  },
}))

const baseXAxis = (dates: string[]) => ({
  type: 'category' as const,
  boundaryGap: selectedType.value === 'bar',
  data: dates,
  axisLine: { lineStyle: { color: c.axisLine.value } },
  axisTick: { show: false },
  axisLabel: {
    color: c.axisLabel.value,
    fontSize: 11,
    fontFamily: 'var(--font-family)',
    interval: dates.length > 14 ? 'auto' : 0,
    rotate: dates.length > 14 ? 30 : 0,
    formatter: (v: string) => {
      const parts = v.split('-')
      return parseInt(parts[1]) + '.' + parseInt(parts[2])
    },
  },
})

const baseYAxis = computed(() => ({
  type: 'value' as const,
  splitLine: {
    lineStyle: { color: c.splitLine.value, type: 'dashed' as const },
  },
  axisLabel: {
    color: c.axisLabel.value,
    fontSize: 11,
    formatter: (v: number) => fmt(v),
    fontFamily: 'var(--font-family)',
  },
}))

const dataZoom = computed(() => {
  const len = store.dailySummary.length
  const start = len > 31 ? Math.round(100 - (31 / len) * 100) : 0
  const minSpan = len > 0
    ? Math.min(100 - start, Math.max(2, Math.round((7 / len) * 100)))
    : 5
  return [
    {
      type: 'inside' as const,
      start,
      end: 100,
      minSpan,
      zoomOnMouseWheel: true,
      moveOnMouseMove: true,
    },
    {
      type: 'slider' as const,
      start,
      end: 100,
      minSpan,
      height: 24,
      borderColor: c.dataZoomBorder.value,
      backgroundColor: c.dataZoomBg.value,
      fillerColor: c.dataZoomFiller.value,
      handleStyle: { color: c.dataZoomHandle.value, borderColor: c.dataZoomHandleBorder.value },
      textStyle: { color: c.dataZoomText.value, fontSize: 10, fontFamily: 'var(--font-family)' },
    },
  ]
})

const costColor = 'rgba(255,149,0,1)'

const costOverlayAxis = computed(() => {
  if (!(showCostOverlay.value && selectedMetric.value === 'tokens')) return null
  return {
    type: 'value' as const,
    splitLine: { show: false },
    axisLabel: {
      color: costColor,
      fontSize: 11,
      formatter: (v: number) => '$' + (v >= 1 ? v.toFixed(2) : v.toFixed(4)),
      fontFamily: 'var(--font-family)',
    },
  }
})

const costOverlaySeries = computed(() => {
  if (!(showCostOverlay.value && selectedMetric.value === 'tokens')) return []
  const costs = store.dailySummary.map((d) => d.total_cost)
  const type = selectedType.value

  if (type === 'bar') {
    return [
      {
        name: loc.t.charts.cost,
        type: 'bar',
        yAxisIndex: 1,
        data: costs,
        barWidth: '35%',
        itemStyle: { color: costColor, borderRadius: [6, 6, 0, 0] },
        emphasis: { focus: 'series' as const },
      },
    ]
  }

  return [
    {
      name: loc.t.charts.cost,
      type: 'line',
      yAxisIndex: 1,
      smooth: 0.4,
      symbol: type === 'area' ? 'none' : 'circle',
      symbolSize: 5,
      data: costs,
      lineStyle: { color: costColor, width: 2, type: 'dashed' as const },
      itemStyle: { color: costColor },
      emphasis: { focus: 'series' as const },
    },
  ]
})

const chartOption = computed(() => {
  const data = store.dailySummary
  const dates = data.map((d) => d.date)
  const inputs = data.map((d) => selectedMetric.value === 'cost' ? d.total_input_cost : d.total_input_tokens)
  const outputs = data.map((d) => selectedMetric.value === 'cost' ? d.total_output_cost : d.total_output_tokens)
  const type = selectedType.value
  const hasOverlay = costOverlayAxis.value !== null

  const inputColor = 'rgba(0,113,227,1)'
  const outputColor = 'rgba(0,113,227,0.50)'

  const yAxis = hasOverlay
    ? [baseYAxis.value, costOverlayAxis.value]
    : [baseYAxis.value]

  const gridRight = hasOverlay ? 60 : 24

  if (type === 'line') {
    return {
      animationDuration: 600,
      animationEasing: 'cubicOut' as const,
      grid: { left: 52, right: gridRight, top: 16, bottom: 60, containLabel: false },
      xAxis: baseXAxis(dates),
      yAxis,
      tooltip: baseTooltip.value,
      dataZoom: dataZoom.value,
      series: [
        {
          name: loc.t.charts.input,
          type: 'line',
          smooth: 0.4,
          symbol: 'circle',
          symbolSize: 6,
          data: inputs,
          lineStyle: { color: inputColor, width: 2 },
          itemStyle: { color: inputColor },
          emphasis: { focus: 'series' as const },
        },
        {
          name: loc.t.charts.output,
          type: 'line',
          smooth: 0.4,
          symbol: 'circle',
          symbolSize: 6,
          data: outputs,
          lineStyle: { color: outputColor, width: 2 },
          itemStyle: { color: outputColor },
          emphasis: { focus: 'series' as const },
        },
        ...costOverlaySeries.value,
      ],
    }
  }

  if (type === 'bar') {
    return {
      animationDuration: 600,
      animationEasing: 'cubicOut' as const,
      grid: { left: 52, right: gridRight, top: 16, bottom: 60, containLabel: false },
      xAxis: baseXAxis(dates),
      yAxis,
      tooltip: baseTooltip.value,
      dataZoom: dataZoom.value,
      series: [
        {
          name: loc.t.charts.input,
          type: 'bar',
          data: inputs,
          barWidth: '35%',
          barGap: '10%',
          itemStyle: {
            color: inputColor,
            borderRadius: [6, 6, 0, 0],
          },
          emphasis: { focus: 'series' as const },
        },
        {
          name: loc.t.charts.output,
          type: 'bar',
          data: outputs,
          barWidth: '35%',
          itemStyle: {
            color: outputColor,
            borderRadius: [6, 6, 0, 0],
          },
          emphasis: { focus: 'series' as const },
        },
        ...costOverlaySeries.value,
      ],
    }
  }

  // default: area (stacked)
  return {
    animationDuration: 600,
    animationEasing: 'cubicOut' as const,
    grid: { left: 52, right: gridRight, top: 16, bottom: 60, containLabel: false },
    xAxis: { ...baseXAxis(dates), boundaryGap: false },
    yAxis,
    tooltip: baseTooltip.value,
    dataZoom: dataZoom.value,
    series: [
      {
        name: loc.t.charts.input,
        type: 'line',
        smooth: 0.4,
        symbol: 'none',
        data: inputs,
        stack: 'total',
        lineStyle: { color: inputColor, width: 0 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0,113,227,0.55)' },
            { offset: 1, color: 'rgba(0,113,227,0.02)' },
          ]),
        },
        emphasis: { focus: 'series' as const },
      },
      {
        name: loc.t.charts.output,
        type: 'line',
        smooth: 0.4,
        symbol: 'none',
        data: outputs,
        stack: 'total',
        lineStyle: { color: outputColor, width: 0 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0,113,227,0.22)' },
            { offset: 1, color: 'rgba(0,113,227,0.01)' },
          ]),
        },
        emphasis: { focus: 'series' as const },
      },
      ...costOverlaySeries.value,
    ],
  }
})
</script>

<style scoped>
.chart-card {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: box-shadow var(--transition-smooth);
}
.chart-card:hover {
  box-shadow: var(--shadow-md);
}

.chart-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-divider);
  flex-wrap: wrap;
  gap: 8px;
}

.chart-card-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  white-space: nowrap;
}

.chart-header-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.chart-legend {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.legend-input {
  background: rgba(0, 113, 227, 0.55);
}

.legend-output {
  background: rgba(0, 113, 227, 0.22);
}

.legend-cost {
  background: rgba(255, 149, 0, 1);
}

.legend-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin-right: 8px;
}

.chart-type-switcher {
  display: flex;
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
  padding: 2px;
  gap: 1px;
}

.type-btn {
  border: none;
  background: transparent;
  padding: 4px 12px;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  border-radius: calc(var(--radius-md) - 2px);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: inherit;
  letter-spacing: var(--letter-spacing-normal);
  white-space: nowrap;
}

.type-btn:hover {
  color: var(--color-text-primary);
}

.type-btn.active {
  color: var(--color-accent);
  background: var(--color-bg-secondary);
  box-shadow: var(--shadow-sm);
}

.cost-toggle {
  border: 1px solid var(--color-divider);
  font-size: var(--font-size-xs);
}

.cost-toggle.active {
  color: rgba(255, 149, 0, 1);
  border-color: rgba(255, 149, 0, 0.3);
  background: rgba(255, 149, 0, 0.08);
  box-shadow: none;
}

.chart-instance {
  width: 100%;
  height: 380px;
}

.chart-empty {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
