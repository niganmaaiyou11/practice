<template>
  <div class="chart-card anim-fade-up" style="animation-delay: 450ms">
    <div class="chart-card-header">
      <h3 class="chart-card-title">{{ loc.t.charts.providerBreakdown }}</h3>
      <div class="chart-header-right">
        <div class="chart-legend" v-if="selectedType !== 'pie'">
          <span class="legend-dot legend-input"></span>
          <span class="legend-label">{{ loc.t.charts.input }}</span>
          <span class="legend-dot legend-output"></span>
          <span class="legend-label">{{ loc.t.charts.output }}</span>
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
    <div v-if="store.providerBreakdown.length === 0" class="chart-empty">
      <el-empty :description="loc.t.charts.noData" />
    </div>
    <v-chart
      v-show="store.providerBreakdown.length > 0"
      :option="chartOption"
      :autoresize="true"
      class="chart-instance"
      :style="{ height: chartHeight + 'px' }"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useTokenRecordsStore } from '../stores/tokenRecords'
import { useLocaleStore } from '../stores/locale'
import { useModelsStore } from '../stores/models'
import { useChartColors } from '../composables/useChartColors'

type ChartType = 'hbar' | 'pie'
type Metric = 'tokens' | 'cost'

const store = useTokenRecordsStore()
const loc = useLocaleStore()
const modelsStore = useModelsStore()
const c = useChartColors()
const selectedType = ref<ChartType>('hbar')
const selectedMetric = ref<Metric>('tokens')

const typeOptions = computed(() => [
  { key: 'hbar' as ChartType, label: loc.t.charts.typeHBar },
  { key: 'pie' as ChartType, label: loc.t.charts.typePie },
])

const metricOptions = computed(() => [
  { key: 'tokens' as Metric, label: loc.t.charts.metricTokens },
  { key: 'cost' as Metric, label: loc.t.charts.metricCost },
])

const providerColors = computed(() => modelsStore.providerColors)

const chartHeight = computed(() => {
  if (selectedType.value === 'pie') return 420
  return Math.max(300, store.providerBreakdown.length * 38 + 80)
})

const fmt = (v: number) => {
  if (selectedMetric.value === 'cost') return '$' + v.toFixed(v >= 10 ? 1 : 4)
  if (v >= 1_000_000) return (v / 1_000_000).toFixed(1) + 'M'
  if (v >= 1_000) return (v / 1_000).toFixed(0) + 'K'
  return String(v)
}

const sortedData = computed(() => {
  const totalKey = selectedMetric.value === 'cost' ? 'total_cost' : 'total_tokens'
  return [...store.providerBreakdown].sort((a, b) => b[totalKey] - a[totalKey])
})

const chartOption = computed(() => {
  const data = sortedData.value
  if (data.length === 0) return {}

  const names = data.map((d) => d.provider)
  const inputs = data.map((d) => selectedMetric.value === 'cost' ? d.total_input_cost : d.total_input_tokens)
  const outputs = data.map((d) => selectedMetric.value === 'cost' ? d.total_output_cost : d.total_output_tokens)

  if (selectedType.value === 'pie') {
    return buildPieOption(names, inputs, outputs)
  }

  return buildHorizontalBarOption(names, inputs, outputs)
})

function buildPieOption(names: string[], inputs: number[], outputs: number[]) {
  const pieData = names.map((name, i) => ({
    name,
    value: inputs[i] + outputs[i],
    inputVal: inputs[i],
    outputVal: outputs[i],
    itemStyle: {
      color: providerColors.value[name] || '#86868b',
    },
  }))

  return {
    animationDuration: 500,
    animationEasing: 'cubicOut' as const,
    xAxis: { show: false },
    yAxis: { show: false },
    grid: { show: false },
    tooltip: {
      trigger: 'item' as const,
      backgroundColor: c.tooltipBg.value,
      borderColor: c.tooltipBorder.value,
      borderWidth: 1,
      borderRadius: 18,
      padding: [14, 18],
      extraCssText: c.tooltipExtraCss.value,
      textStyle: {
        color: c.tooltipText.value,
        fontSize: 13,
        fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      },
      formatter: (params: any) => {
        const d = params.data
        const total = d.value
        const pct = params.percent.toFixed(1)
        return `
          <div style="min-width:160px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
              <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${d.itemStyle.color};"></span>
              <span style="font-size:14px;font-weight:600;color:${c.tooltipText.value};">${d.name}</span>
            </div>
            <div style="display:flex;gap:0;background:${c.tooltipTotalBg.value};border-radius:10px;overflow:hidden;margin-top:8px;">
              <div style="flex:${d.inputVal};padding:8px 12px;text-align:center;min-width:55px;">
                <div style="font-size:10px;color:${c.tooltipTextSecondary.value};text-transform:uppercase;">${loc.t.charts.input}</div>
                <div style="font-size:13px;font-weight:700;color:${c.tooltipText.value};">${fmt(d.inputVal)}</div>
              </div>
              <div style="flex:${d.outputVal};padding:8px 12px;text-align:center;min-width:55px;">
                <div style="font-size:10px;color:${c.tooltipTextSecondary.value};text-transform:uppercase;">${loc.t.charts.output}</div>
                <div style="font-size:13px;font-weight:700;color:${c.tooltipText.value};">${fmt(d.outputVal)}</div>
              </div>
            </div>
            <div style="margin-top:10px;padding-top:8px;border-top:1px solid ${c.tooltipDivider.value};text-align:center;">
              <span style="font-size:11px;color:${c.tooltipTextSecondary.value};">${selectedMetric.value === 'cost' ? loc.t.charts.totalCostLabel : loc.t.charts.totalTokensLabel} </span>
              <span style="font-size:14px;font-weight:700;color:${c.tooltipText.value};">${fmt(total)}</span>
              <span style="font-size:11px;color:${c.tooltipTextSecondary.value};"> (${pct}%)</span>
            </div>
          </div>
        `
      },
    },
    legend: {
      orient: 'vertical' as const,
      right: 10,
      top: 'center',
      itemGap: 6,
      itemWidth: 8,
      itemHeight: 8,
      borderRadius: 4,
      textStyle: {
        color: c.axisLabel.value,
        fontSize: 11,
        fontFamily: 'var(--font-family)',
      },
    },
    series: [
      {
        type: 'pie',
        radius: ['52%', '78%'],
        center: ['40%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 6,
          borderColor: c.pieBorder.value,
          borderWidth: 2,
        },
        label: { show: false },
        emphasis: {
          label: { show: true, fontSize: 13, fontWeight: 600 },
          scaleSize: 8,
        },
        labelLine: { show: false },
        data: pieData,
      },
    ],
  }
}

function buildHorizontalBarOption(names: string[], inputs: number[], outputs: number[]) {
  return {
    animationDuration: 500,
    animationEasing: 'cubicOut' as const,
    grid: { left: 8, right: 24, top: 8, bottom: 8, containLabel: true },
    xAxis: {
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
    },
    yAxis: {
      type: 'category' as const,
      data: names,
      inverse: true,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: c.yAxisLabel.value,
        fontSize: 12,
        fontWeight: 500,
        fontFamily: 'var(--font-family)',
        width: 100,
        overflow: 'truncate',
        ellipsis: '...',
      },
    },
    tooltip: {
      trigger: 'axis' as const,
      backgroundColor: c.tooltipBg.value,
      borderColor: c.tooltipBorder.value,
      borderWidth: 1,
      borderRadius: 18,
      padding: 0,
      extraCssText: c.tooltipExtraCss.value,
      formatter: (params: any[]) => {
        const idx = params[0]?.dataIndex ?? 0
        const name = names[idx] || ''
        const input = inputs[idx] || 0
        const output = outputs[idx] || 0
        const total = input + output
        const pctInput = total > 0 ? Math.round((input / total) * 100) : 0
        const pctOutput = total > 0 ? Math.round((output / total) * 100) : 0
        const pColor = providerColors.value[name] || '#86868b'

        return `
          <div style="padding:16px 20px;min-width:180px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
              <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${pColor};"></span>
              <span style="font-size:14px;font-weight:600;color:${c.tooltipText.value};">${name}</span>
            </div>
            <div style="display:flex;gap:0;background:${c.tooltipTotalBg.value};border-radius:10px;overflow:hidden;">
              <div style="flex:${input};padding:10px 12px;text-align:center;min-width:60px;">
                <div style="font-size:10px;color:${c.tooltipTextSecondary.value};text-transform:uppercase;letter-spacing:0.04em;margin-bottom:2px;">${loc.t.charts.input}</div>
                <div style="font-size:14px;font-weight:700;color:${c.tooltipText.value};">${fmt(input)}</div>
                <div style="font-size:10px;color:${c.tooltipTextSecondary.value};">${pctInput}%</div>
              </div>
              <div style="flex:${output};padding:10px 12px;text-align:center;min-width:60px;">
                <div style="font-size:10px;color:${c.tooltipTextSecondary.value};text-transform:uppercase;letter-spacing:0.04em;margin-bottom:2px;">${loc.t.charts.output}</div>
                <div style="font-size:14px;font-weight:700;color:${c.tooltipText.value};">${fmt(output)}</div>
                <div style="font-size:10px;color:${c.tooltipTextSecondary.value};">${pctOutput}%</div>
              </div>
            </div>
            <div style="margin-top:10px;padding-top:8px;border-top:1px solid ${c.tooltipDivider.value};text-align:center;">
              <span style="font-size:11px;color:${c.tooltipTextSecondary.value};">${selectedMetric.value === 'cost' ? loc.t.charts.totalCostLabel : loc.t.charts.totalTokensLabel} </span>
              <span style="font-size:14px;font-weight:700;color:${c.tooltipText.value};">${fmt(total)}</span>
            </div>
          </div>
        `
      },
    },
    series: [
      {
        name: loc.t.charts.input,
        type: 'bar',
        stack: 'total',
        data: inputs.map((v, i) => {
          const pc = providerColors.value[names[i]] || '#86868b'
          return {
            value: v,
            itemStyle: {
              color: pc + 'CC',
              borderRadius: v > 0 ? [0, 0, 0, 0] : [6, 6, 6, 6],
              borderWidth: 0,
            },
          }
        }),
        barWidth: 16,
      },
      {
        name: loc.t.charts.output,
        type: 'bar',
        stack: 'total',
        data: outputs.map((v, i) => {
          const pc = providerColors.value[names[i]] || '#86868b'
          return {
            value: v,
            itemStyle: {
              color: pc + '55',
              borderRadius: [6, 6, 0, 0],
              borderWidth: 0,
            },
          }
        }),
        barWidth: 16,
      },
    ],
  }
}
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
  background: rgba(0, 113, 227, 0.70);
}

.legend-output {
  background: rgba(0, 113, 227, 0.30);
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

.chart-instance {
  width: 100%;
}

.chart-empty {
  min-height: 260px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
