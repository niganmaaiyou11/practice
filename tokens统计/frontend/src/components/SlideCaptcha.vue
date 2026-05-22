<template>
  <div class="slide-captcha" :class="{ 'is-verified': verified }">
    <div ref="trackRef" class="slide-captcha__track">
      <div class="slide-captcha__progress" :style="{ width: progressWidth + 'px' }" />
      <span class="slide-captcha__label" :style="{ opacity: labelOpacity }">
        {{ verified ? t.auth.verifySuccess : t.auth.slideToVerify }}
      </span>
    </div>
    <div
      ref="handleRef"
      class="slide-captcha__handle"
      :class="{ 'is-dragging': dragging, 'is-verified': verified }"
      :style="{ left: handleLeft + 'px' }"
      @pointerdown.prevent="onPointerDown"
    >
      <svg
        v-if="!verified"
        class="handle-icon"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M5 12h14M12 5l7 7-7 7" />
      </svg>
      <svg
        v-else
        class="handle-icon check-icon"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <polyline points="20 6 9 17 4 12" />
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useLocaleStore } from '../stores/locale'

const emit = defineEmits<{
  verify: [token: string]
}>()

const authStore = useAuthStore()
const localeStore = useLocaleStore()
const t = localeStore.t

const trackRef = ref<HTMLElement | null>(null)
const handleRef = ref<HTMLElement | null>(null)

const handleLeft = ref(0)
const dragging = ref(false)
const verified = ref(false)
const captchaToken = ref('')

const trackWidth = ref(300)
const handleWidth = 48
const maxLeft = computed(() => trackWidth.value - handleWidth)

const progressWidth = computed(() => handleLeft.value + handleWidth / 2)
const labelOpacity = computed(() => {
  const ratio = handleLeft.value / maxLeft.value
  return Math.max(0, 1 - ratio * 2)
})

function loadCaptcha() {
  authStore.fetchCaptcha().then((token) => {
    captchaToken.value = token
  })
}

function onPointerDown(e: PointerEvent) {
  if (verified.value) return
  dragging.value = true
  ;(e.target as HTMLElement).setPointerCapture(e.pointerId)
}

function onPointerMove(e: PointerEvent) {
  if (!dragging.value || !trackRef.value) return
  const rect = trackRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left - handleWidth / 2
  handleLeft.value = Math.max(0, Math.min(x, maxLeft.value))
}

function onPointerUp(_e: PointerEvent) {
  if (!dragging.value) return
  dragging.value = false

  if (handleLeft.value >= maxLeft.value * 0.95) {
    handleLeft.value = maxLeft.value
    verified.value = true
    emit('verify', captchaToken.value)
  } else {
    handleLeft.value = 0
  }
}

function updateTrackWidth() {
  if (trackRef.value) {
    trackWidth.value = trackRef.value.clientWidth
  }
}

defineExpose({
  reset() {
    verified.value = false
    handleLeft.value = 0
    captchaToken.value = ''
    loadCaptcha()
  },
})

onMounted(() => {
  loadCaptcha()
  updateTrackWidth()
  window.addEventListener('resize', updateTrackWidth)
  document.addEventListener('pointermove', onPointerMove)
  document.addEventListener('pointerup', onPointerUp)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateTrackWidth)
  document.removeEventListener('pointermove', onPointerMove)
  document.removeEventListener('pointerup', onPointerUp)
})
</script>

<style scoped>
.slide-captcha {
  display: flex;
  align-items: center;
  position: relative;
  height: 48px;
}

.slide-captcha__track {
  position: relative;
  width: 100%;
  height: 100%;
  background: var(--color-bg-primary, #f5f5f7);
  border-radius: var(--radius-md, 12px);
  overflow: hidden;
}

.slide-captcha__progress {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: linear-gradient(135deg, var(--color-accent, #0071e3), #42a5f5);
  border-radius: var(--radius-md, 12px);
  transition: width 100ms linear;
}

.slide-captcha__label {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-sm, 13px);
  font-weight: var(--font-weight-medium, 500);
  color: var(--color-text-secondary, #86868b);
  letter-spacing: var(--letter-spacing-normal, -0.016em);
  pointer-events: none;
  transition: opacity 150ms ease;
  user-select: none;
}

.slide-captcha.is-verified .slide-captcha__label {
  color: #fff;
}

.slide-captcha__handle {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md, 12px);
  background: var(--color-bg-secondary, #fff);
  border: 1px solid var(--color-border, rgba(0, 0, 0, 0.08));
  box-shadow: var(--shadow-md, 0 4px 12px rgba(0, 0, 0, 0.06));
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
  touch-action: none;
  transition: left 400ms cubic-bezier(0.175, 0.885, 0.32, 1.275),
              box-shadow 150ms ease,
              background 200ms ease;
  z-index: 2;
  user-select: none;
}

.slide-captcha__handle:active {
  cursor: grabbing;
}

.slide-captcha__handle.is-dragging {
  box-shadow: var(--shadow-hover, 0 12px 40px rgba(0, 0, 0, 0.1));
  transition: box-shadow 150ms ease;
}

.slide-captcha__handle.is-verified {
  background: var(--color-accent, #0071e3);
  border-color: var(--color-accent, #0071e3);
  cursor: default;
}

.handle-icon {
  width: 20px;
  height: 20px;
  color: var(--color-text-secondary, #86868b);
  transition: color 200ms ease, transform 200ms ease;
}

.slide-captcha__handle.is-dragging .handle-icon {
  color: var(--color-accent, #0071e3);
}

.check-icon {
  color: #fff;
  animation: check-pop 300ms cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes check-pop {
  0% {
    transform: scale(0.5);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
