import { ref, watch, onUnmounted, type Ref } from 'vue'

function easeOutCubic(t: number): number {
  return 1 - Math.pow(1 - t, 3)
}

export function useCountUp(
  target: Ref<number | undefined>,
  options?: { duration?: number }
): Ref<string> {
  const display = ref('0')
  const duration = options?.duration ?? 800
  let animId = 0
  let startVal = 0
  let startTime = 0

  function animate(timestamp: number) {
    if (!startTime) startTime = timestamp
    const elapsed = timestamp - startTime
    const progress = Math.min(elapsed / duration, 1)
    const eased = easeOutCubic(progress)
    const current = Math.round(startVal + (endVal - startVal) * eased)
    display.value = current.toLocaleString()

    if (progress < 1) {
      animId = requestAnimationFrame(animate)
    }
  }

  let endVal = 0

  function startAnim(newTarget: number) {
    cancelAnimationFrame(animId)
    // Parse current display value for seamless chaining
    const parsed = parseInt(display.value.replace(/,/g, ''), 10)
    startVal = isNaN(parsed) ? 0 : parsed
    endVal = newTarget
    startTime = 0
    animId = requestAnimationFrame(animate)
  }

  watch(
    target,
    (val) => {
      if (val != null) startAnim(val)
    },
    { immediate: true }
  )

  onUnmounted(() => cancelAnimationFrame(animId))

  return display
}
