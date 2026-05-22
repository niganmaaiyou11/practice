<template>
  <div
    ref="trackRef"
    class="theme-track"
    :style="trackStyle"
    @click="onTrackClick"
  >
    <span class="track-label label-left" :style="leftLabelStyle">Light</span>
    <span class="track-label label-right" :style="rightLabelStyle">Dark</span>
    <div
      ref="sliderRef"
      class="theme-slider"
      :class="{ dragging: isDragging, pressed: isPressed }"
      :style="sliderStyle"
      @mousedown.prevent="onPointerDown"
      @touchstart.prevent="onPointerDown"
      @mouseenter="isHovering = true"
      @mouseleave="isHovering = false"
    >
      <svg class="icon-cloud" viewBox="0 0 24 24" :style="cloudIconStyle">
        <path
          d="M19.35 10.04A7.49 7.49 0 0 0 12 4C9.11 4 6.6 5.64 5.35 8.04A5.994 5.994 0 0 0 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z"
          fill="currentColor"
        />
      </svg>
      <svg class="icon-sun" viewBox="0 0 24 24" :style="sunIconStyle">
        <circle cx="12" cy="12" r="4.5" fill="currentColor" />
        <g stroke="currentColor" stroke-width="1.8" stroke-linecap="round" opacity="0.9">
          <line x1="12" y1="1" x2="12" y2="3" />
          <line x1="12" y1="21" x2="12" y2="23" />
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
          <line x1="1" y1="12" x2="3" y2="12" />
          <line x1="21" y1="12" x2="23" y2="12" />
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
        </g>
      </svg>
      <svg class="icon-moon" viewBox="0 0 24 24" :style="moonIconStyle">
        <path
          d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"
          fill="currentColor"
        />
      </svg>
      <svg class="icon-stars" viewBox="0 0 24 24" :style="starsIconStyle">
        <circle cx="3" cy="3" r="1.3" fill="#FFD700" />
        <circle cx="19" cy="2" r="0.9" fill="#87CEEB" />
        <circle cx="21" cy="9" r="0.8" fill="#FF69B4" />
        <circle cx="5" cy="12" r="1.1" fill="#FFD966" />
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from 'vue'
import { useThemeStore } from '../stores/theme'

const theme = useThemeStore()

// ---- dimensions ----
const TRACK_W = 80
const TRACK_H = 28
const SLIDER_D = 24
const SLIDER_PAD = (TRACK_H - SLIDER_D) / 2
const MAX_LEFT = TRACK_W - SLIDER_D - SLIDER_PAD * 2
const DRAG_THRESHOLD = 3

const isHovering = ref(false)
const isDragging = ref(false)
const isPressed = ref(false)
const dragProgress = ref<number | null>(null)

const trackRef = ref<HTMLElement | null>(null)
const sliderRef = ref<HTMLElement | null>(null)

let dragStartX = 0
let dragStartLeft = 0
let hasMoved = false

// ---- helpers ----
function lerp(a: number, b: number, t: number) { return a + (b - a) * t }
function clamp(v: number, lo: number, hi: number) { return v < lo ? lo : v > hi ? hi : v }

function lerpHex(hexA: string, hexB: string, t: number): string {
  const ah = parseInt(hexA.slice(1), 16)
  const bh = parseInt(hexB.slice(1), 16)
  const ar = (ah >> 16) & 0xff
  const ag = (ah >> 8) & 0xff
  const aBlue = ah & 0xff
  const br = (bh >> 16) & 0xff
  const bGreen = (bh >> 8) & 0xff
  const bBlue = bh & 0xff
  const r = Math.round(lerp(ar, br, t))
  const g = Math.round(lerp(ag, bGreen, t))
  const b = Math.round(lerp(aBlue, bBlue, t))
  return `#${((1 << 24) | (r << 16) | (g << 8) | b).toString(16).slice(1)}`
}

function lerpRgba(from: number[], to: number[], t: number): string {
  const r = Math.round(lerp(from[0], to[0], t))
  const g = Math.round(lerp(from[1], to[1], t))
  const b = Math.round(lerp(from[2], to[2], t))
  const alpha = lerp(from[3], to[3], t)
  return `rgba(${r},${g},${b},${alpha.toFixed(2)})`
}

// ---- colour stops ----
const LIGHT_BG = '#f5f5f7'
const DARK_BG = '#000000'
const LIGHT_TRACK = '#4da6ff'
const DARK_TRACK = '#2d1b4e'
const LIGHT_SLIDER = [135, 206, 250, 0.55]
const DARK_SLIDER = [100, 60, 160, 0.55]
const LIGHT_HIGHLIGHT = [200, 230, 255, 0.78]
const DARK_HIGHLIGHT = [160, 120, 220, 0.78]
const LIGHT_CLOUD = '#b4d2f0'
const DARK_CLOUD = '#8c64c8'
const LIGHT_SUN_COLOR = 'rgba(255,190,40,0.92)'
const DARK_MOON_COLOR = 'rgba(220,170,240,0.92)'

function currentProgress(): number {
  if (dragProgress.value !== null) return dragProgress.value
  // 0 = light (slider left), 1 = dark (slider right)
  return theme.current === 'dark' ? 1 : 0
}

function applyBodyBg(progress: number) {
  document.body.style.backgroundColor = lerpHex(LIGHT_BG, DARK_BG, progress)
}

function clearBodyBg() {
  document.body.style.transition = ''
  document.body.style.backgroundColor = ''
}

// ---- pointer events ----
function getClientX(e: MouseEvent | TouchEvent): number {
  if ('touches' in e) return e.touches[0].clientX
  return e.clientX
}

function onPointerDown(e: MouseEvent | TouchEvent) {
  if (!trackRef.value) return
  isPressed.value = true
  hasMoved = false
  dragStartX = getClientX(e)
  dragStartLeft = sliderRef.value!.offsetLeft

  document.addEventListener('mousemove', onPointerMove)
  document.addEventListener('mouseup', onPointerUp)
  document.addEventListener('touchmove', onPointerMove, { passive: false })
  document.addEventListener('touchend', onPointerUp)
}

function onPointerMove(e: MouseEvent | TouchEvent) {
  if (!trackRef.value) return
  const dx = getClientX(e) - dragStartX
  if (!hasMoved && Math.abs(dx) < DRAG_THRESHOLD) return

  if (!hasMoved) {
    hasMoved = true
    isDragging.value = true
    isPressed.value = false
    document.body.style.transition = 'none'
  }

  const rawLeft = dragStartLeft + dx
  const clampedLeft = clamp(rawLeft, 0, MAX_LEFT)
  dragProgress.value = MAX_LEFT > 0 ? clampedLeft / MAX_LEFT : 0

  applyBodyBg(dragProgress.value)
}

function onPointerUp() {
  document.removeEventListener('mousemove', onPointerMove)
  document.removeEventListener('mouseup', onPointerUp)
  document.removeEventListener('touchmove', onPointerMove)
  document.removeEventListener('touchend', onPointerUp)

  isPressed.value = false

  if (isDragging.value) {
    isDragging.value = false
    const p = dragProgress.value ?? (theme.current === 'dark' ? 1 : 0)
    const snapped = p >= 0.5 ? 'dark' : 'light'
    dragProgress.value = null
    theme.setTheme(snapped)
  }

  clearBodyBg()
}

function onTrackClick() {
  if (hasMoved) return
  theme.toggle()
}

onBeforeUnmount(() => {
  document.removeEventListener('mousemove', onPointerMove)
  document.removeEventListener('mouseup', onPointerUp)
  document.removeEventListener('touchmove', onPointerMove)
  document.removeEventListener('touchend', onPointerUp)
})

// ---- reactive styles ----
const trackStyle = computed(() => {
  const p = dragProgress.value
  if (p !== null) {
    return { background: lerpHex(LIGHT_TRACK, DARK_TRACK, p), transition: 'none' }
  }
  return {}
})

const sliderStyle = computed(() => {
  const p = currentProgress()
  const leftPx = p * MAX_LEFT
  const glass = lerpRgba(LIGHT_SLIDER, DARK_SLIDER, p)
  const highlight = lerpRgba(LIGHT_HIGHLIGHT, DARK_HIGHLIGHT, p)

  const style: Record<string, string> = {
    left: `${leftPx}px`,
    background: glass,
    boxShadow: `
      0 2px 8px rgba(0,0,0,${(0.15 + p * 0.2).toFixed(2)}),
      inset 0 1px 0 ${highlight},
      inset 0 -1px 0 rgba(255,255,255,0.15)
    `,
    borderColor: highlight,
  }

  if (dragProgress.value !== null) style.transition = 'none'

  return style
})

const cloudIconStyle = computed(() => ({
  color: lerpHex(LIGHT_CLOUD, DARK_CLOUD, currentProgress()),
  transition: dragProgress.value !== null ? 'none' : undefined,
}))

const sunIconStyle = computed(() => ({
  opacity: 1 - currentProgress(), // sun visible in light mode (p=0)
  transition: dragProgress.value !== null ? 'none' : undefined,
  color: LIGHT_SUN_COLOR,
}))

const moonIconStyle = computed(() => ({
  opacity: currentProgress(), // moon visible in dark mode (p=1)
  transition: dragProgress.value !== null ? 'none' : undefined,
  color: DARK_MOON_COLOR,
}))

const starsIconStyle = computed(() => {
  const p = currentProgress()
  // stars fade in near dark side (last 30%)
  const starsOpacity = p > 0.7 ? clamp((p - 0.7) / 0.3, 0, 1) : 0
  return {
    opacity: starsOpacity,
    transition: dragProgress.value !== null ? 'none' : undefined,
  }
})

// left="Light" visible when dark (p=1), right="Dark" visible when light (p=0)
const leftLabelStyle = computed(() => ({
  opacity: currentProgress(),
  transition: dragProgress.value !== null ? 'none' : undefined,
}))

const rightLabelStyle = computed(() => ({
  opacity: 1 - currentProgress(),
  transition: dragProgress.value !== null ? 'none' : undefined,
}))
</script>

<style scoped>
.theme-track {
  position: relative;
  width: 80px;
  height: 28px;
  border-radius: 14px;
  background: var(--color-track, #4da6ff);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.15);
  cursor: pointer;
  flex-shrink: 0;
  transition: background 300ms cubic-bezier(0.25, 0.1, 0.25, 1),
    box-shadow 300ms cubic-bezier(0.25, 0.1, 0.25, 1);
  display: flex;
  align-items: center;
  user-select: none;
}

.track-label {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: #fff;
  pointer-events: none;
  transition: opacity 300ms ease;
  z-index: 1;
}

.label-left {
  left: 10px;
}

.label-right {
  right: 10px;
}

/* ---- slider knob ---- */
.theme-slider {
  position: absolute;
  top: 2px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 1.5px solid rgba(255, 255, 255, 0.25);
  cursor: grab;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  transition: left 300ms cubic-bezier(0.34, 1.56, 0.64, 1),
    background 300ms cubic-bezier(0.25, 0.1, 0.25, 1),
    box-shadow 300ms cubic-bezier(0.25, 0.1, 0.25, 1),
    border-color 300ms cubic-bezier(0.25, 0.1, 0.25, 1),
    transform 300ms cubic-bezier(0.25, 0.1, 0.25, 1);
  overflow: visible;
}

.theme-slider.dragging {
  cursor: grabbing;
}

.theme-slider:hover:not(.dragging) {
  transform: scale(1.08);
}

.theme-slider.pressed {
  transform: scale(0.95);
}

/* ---- icons ---- */
.icon-cloud,
.icon-sun,
.icon-moon,
.icon-stars {
  position: absolute;
  pointer-events: none;
  transition: opacity 300ms ease, color 300ms ease;
}

.icon-cloud {
  width: 16px;
  height: 16px;
}

.icon-sun {
  width: 18px;
  height: 18px;
}

.icon-moon {
  width: 12px;
  height: 12px;
  transform: translate(1px, -1px);
}

.icon-stars {
  width: 22px;
  height: 22px;
}
</style>
