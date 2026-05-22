import { computed } from 'vue'
import { useThemeStore } from '../stores/theme'

export function useChartColors() {
  const theme = useThemeStore()
  const isDark = computed(() => theme.current === 'dark')

  // Tooltip
  const tooltipBg = computed(() =>
    isDark.value ? 'rgba(28,28,30,0.88)' : 'rgba(255,255,255,0.80)')
  const tooltipBorder = computed(() =>
    isDark.value ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)')
  const tooltipText = computed(() =>
    isDark.value ? '#f5f5f7' : '#1d1d1f')
  const tooltipTextSecondary = computed(() =>
    isDark.value ? '#98989d' : '#86868b')
  const tooltipDivider = computed(() =>
    isDark.value ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.05)')
  const tooltipInputBg = computed(() =>
    isDark.value ? 'rgba(0,113,227,0.25)' : 'rgba(0,113,227,0.18)')
  const tooltipOutputBg = computed(() =>
    isDark.value ? 'rgba(0,113,227,0.10)' : 'rgba(0,113,227,0.06)')
  const tooltipTotalBg = computed(() =>
    isDark.value ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.03)')

  // Axes
  const axisLine = computed(() =>
    isDark.value ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)')
  const axisLabel = computed(() =>
    isDark.value ? '#98989d' : '#86868b')
  const splitLine = computed(() =>
    isDark.value ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.04)')
  const yAxisLabel = computed(() =>
    isDark.value ? '#f5f5f7' : '#1d1d1f')

  // DataZoom
  const dataZoomBorder = computed(() =>
    isDark.value ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)')
  const dataZoomBg = computed(() =>
    isDark.value ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.02)')
  const dataZoomFiller = computed(() =>
    isDark.value ? 'rgba(0,113,227,0.15)' : 'rgba(0,113,227,0.08)')
  const dataZoomText = computed(() =>
    isDark.value ? '#98989d' : '#86868b')
  const dataZoomHandle = computed(() =>
    isDark.value ? 'rgba(0,113,227,0.6)' : 'rgba(0,113,227,0.5)')
  const dataZoomHandleBorder = computed(() =>
    isDark.value ? 'rgba(0,113,227,0.4)' : 'rgba(0,113,227,0.3)')

  // Pie
  const pieBorder = computed(() =>
    isDark.value ? '#1c1c1e' : '#ffffff')

  // Scatter
  const scatterTooltipBg = computed(() =>
    isDark.value ? 'rgba(28,28,30,0.94)' : 'rgba(255,255,255,0.94)')
  const scatterGridLine = computed(() =>
    isDark.value ? 'rgba(255,255,255,0.06)' : '#f0f0f0')
  const scatterMarkLine = computed(() =>
    isDark.value ? 'rgba(255,255,255,0.12)' : '#d0d0d0')

  // Glass tooltip extraCssText
  const tooltipExtraCss = computed(() =>
    isDark.value
      ? 'backdrop-filter: saturate(180%) blur(20px);-webkit-backdrop-filter: saturate(180%) blur(20px);box-shadow: 0 8px 32px rgba(0,0,0,0.4);'
      : 'backdrop-filter: saturate(180%) blur(20px);-webkit-backdrop-filter: saturate(180%) blur(20px);box-shadow: 0 8px 32px rgba(0,0,0,0.08);')

  return {
    isDark,
    tooltipBg,
    tooltipBorder,
    tooltipText,
    tooltipTextSecondary,
    tooltipDivider,
    tooltipInputBg,
    tooltipOutputBg,
    tooltipTotalBg,
    axisLine,
    axisLabel,
    splitLine,
    yAxisLabel,
    dataZoomBorder,
    dataZoomBg,
    dataZoomFiller,
    dataZoomText,
    dataZoomHandle,
    dataZoomHandleBorder,
    pieBorder,
    scatterTooltipBg,
    scatterGridLine,
    scatterMarkLine,
    tooltipExtraCss,
  }
}
