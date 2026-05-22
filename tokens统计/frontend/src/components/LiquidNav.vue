<template>
  <nav
    class="liquid-nav"
    ref="navRef"
    @mousemove="onMouseMove"
  >
    <div class="glass-surface" />
    <div class="liquid-pill" :style="pillStyle">
      <div class="pill-glow" />
    </div>
    <router-link
      v-for="item in items"
      :key="item.path"
      :to="item.path"
      class="nav-item"
      :class="{ active: activeMenu === item.path }"
    >
      <span
        v-for="(ch, i) in chars(item.label)"
        :key="i"
        :ref="(el: any) => setCharRef(item.path, i, el)"
        class="ch"
        :class="{ sp: ch === ' ' }"
      >{{ ch }}</span>
    </router-link>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'

interface NavItem { path: string; label: string }
const props = defineProps<{ items: NavItem[]; activeMenu: string }>()
const navRef = ref<HTMLElement | null>(null)
function chars(s: string) { return s.split('').map(c => c === ' ' ? ' ' : c) }

const charRefs: Record<string, HTMLElement> = {}
const charInfluences: Record<string, number> = {}
function setCharRef(path: string, i: number, el: HTMLElement | null) {
  if (el) charRefs[`${path}:${i}`] = el
}

// ---- Liquid pill (rAF lerp with edge squish) ----
const pillWidth = ref(0)
const navWidth = ref(0)
const rend = ref({ x: -200 })
const targ = ref({ x: -200 })

const pillStyle = computed(() => {
  const baseW = pillWidth.value
  const cx = rend.value.x
  const halfW = baseW / 2
  const navW = navWidth.value

  let left = cx - halfW
  let width = baseW
  let top = 4
  let bottom = 4
  let rTL = 999, rTR = 999, rBL = 999, rBR = 999

  if (navW > 0 && halfW > 0) {
    // Squish against left wall
    if (left < 0) {
      const overflow = Math.min(-left, halfW)
      width = baseW - overflow
      left = 0
      const bulge = overflow / halfW
      top -= bulge * 10
      bottom -= bulge * 7
      const flat = Math.max(20, 999 - overflow * 20)
      rTL = flat
      rBL = flat
    }

    // Squish against right wall
    const rightEdge = left + width
    if (rightEdge > navW) {
      const overflow = Math.min(rightEdge - navW, halfW)
      width = baseW - overflow
      const bulge = overflow / halfW
      top = Math.min(top, 4 - bulge * 10)
      bottom = Math.min(bottom, 4 - bulge * 7)
      const flat = Math.max(20, 999 - overflow * 20)
      rTR = flat
      rBR = flat
    }
  }

  return {
    left: `${left}px`,
    width: `${width}px`,
    top: `${top}px`,
    bottom: `${bottom}px`,
    borderRadius: `${rTL}px ${rTR}px ${rBR}px ${rBL}px`,
  }
})

let timer = 0
let frame = 0

function setPillWidthToWidest() {
  const items = navRef.value?.querySelectorAll('.nav-item')
  if (!items || items.length === 0) return
  let maxW = 0
  items.forEach((el) => { const w = el.getBoundingClientRect().width; if (w > maxW) maxW = w })
  pillWidth.value = maxW + 8
}

function tick() {
  frame++
  if (navRef.value) navWidth.value = navRef.value.getBoundingClientRect().width
  rend.value = {
    x: rend.value.x + (targ.value.x - rend.value.x) * 0.08,
  }
  updateChars()
}

// ---- Lens distortion on characters ----
function updateChars() {
  const nav = navRef.value
  if (!nav) return
  const nr = nav.getBoundingClientRect()
  const px = rend.value.x
  const halfW = pillWidth.value / 2
  if (halfW < 1) return

  for (const key of Object.keys(charRefs)) {
    const el = charRefs[key]
    const er = el.getBoundingClientRect()
    const cx = er.left + er.width / 2 - nr.left
    const dx = (cx - px) / halfW
    const dist = Math.abs(dx)
    const inf = Math.max(0, 1 - dist)

    const prev = charInfluences[key] ?? 0
    if (Math.abs(inf - prev) < 0.002) continue
    charInfluences[key] = inf

    // Recovery - outside the glass, instant reset
    if (inf < 0.008) {
      el.style.transform = ''
      el.style.color = ''
      el.style.fontWeight = ''
      el.style.textShadow = ''
      el.style.filter = ''
      continue
    }

    // Lens magnification
    const mag = 1 + inf * inf * 0.13

    // Edge displacement
    const edgePush = dist > 0.5 ? (dist - 0.5) / 0.5 * inf * 0.85 : 0
    const pushDir = dx >= 0 ? 1 : -1
    const pushPx = pushDir * edgePush * halfW * 0.28

    el.style.transform = `scale(${mag.toFixed(3)}) translateX(${pushPx.toFixed(1)}px)`

    // Color saturation & brightness
    const r = Math.round(134 - inf * 112)
    const g2 = Math.round(134 - inf * 106)
    const b2 = Math.round(139 - inf * 82)
    el.style.color = `rgb(${r},${g2},${b2})`
    el.style.fontWeight = inf > 0.25 ? '600' : '500'

    // Saturation lift
    el.style.filter = inf > 0.05 ? `saturate(${(1 + inf * 0.8).toFixed(2)})` : ''

    // Chromatic dispersion at the glass rim
    const chromaZone = dist > 0.35 ? Math.min((dist - 0.35) / 0.6, 1) : 0
    const chroma = chromaZone * inf * 0.85

    if (chroma > 0.01) {
      const rShift = -pushDir * chroma * 4.5
      const bShift = pushDir * chroma * 4.5
      el.style.textShadow = [
        `${rShift.toFixed(1)}px 0 0 rgba(255,40,40,${(chroma * 0.55).toFixed(2)})`,
        `${bShift.toFixed(1)}px 0 0 rgba(40,40,255,${(chroma * 0.55).toFixed(2)})`,
        `0 0 ${(inf * 8).toFixed(1)}px rgba(255,255,255,${(inf * 0.28).toFixed(2)})`,
      ].join(', ')
    } else if (inf > 0.03) {
      el.style.textShadow = `0 0 ${(inf * 8).toFixed(1)}px rgba(255,255,255,${(inf * 0.28).toFixed(2)})`
    } else {
      el.style.textShadow = ''
    }
  }
}

// ---- Mouse ----
function onMouseMove(e: MouseEvent) {
  if (!navRef.value) return
  const r = navRef.value.getBoundingClientRect()
  targ.value = { x: e.clientX - r.left }
}
function onWindowMouseMove(e: MouseEvent) {
  if (!navRef.value) return
  const r = navRef.value.getBoundingClientRect()
  const inBounds = e.clientY >= r.top && e.clientY <= r.bottom && e.clientX >= r.left && e.clientX <= r.right
  if (inBounds) {
    targ.value = { x: e.clientX - r.left }
    if (settleTimer) { clearTimeout(settleTimer); settleTimer = null }
  } else {
    scheduleSettle()
  }
}

function settle() {
  setPillWidthToWidest()
  const a = navRef.value?.querySelector('.nav-item.active') as HTMLElement | null
  if (a && navRef.value) {
    const nr = navRef.value.getBoundingClientRect()
    const ar = a.getBoundingClientRect()
    targ.value = { x: ar.left + ar.width / 2 - nr.left }
  } else {
    targ.value = { x: -200 }
  }
}
let settleTimer: ReturnType<typeof setTimeout> | null = null

function scheduleSettle() {
  if (!settleTimer) settleTimer = setTimeout(() => { settle(); settleTimer = null }, 350)
}

onMounted(() => {
  timer = window.setInterval(tick, 16)
  window.addEventListener('mousemove', onWindowMouseMove, { passive: true })
  nextTick(() => {
    if (navRef.value) navWidth.value = navRef.value.getBoundingClientRect().width
    settle(); rend.value = { ...targ.value }
  })
})
onUnmounted(() => {
  clearInterval(timer)
  window.removeEventListener('mousemove', onWindowMouseMove)
  if (settleTimer) clearTimeout(settleTimer)
})
watch(() => props.activeMenu, () => nextTick(settle))
watch(() => props.items, () => nextTick(settle), { deep: true })
</script>

<style scoped>
.liquid-nav {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1px;
  padding: 4px 5px;
  border-radius: 26px;
  flex: 1;
  overflow: hidden;
}

.glass-surface {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px) saturate(150%);
  -webkit-backdrop-filter: blur(20px) saturate(150%);
  border: 0.5px solid rgba(255, 255, 255, 0.7);
  box-shadow:
    0 2px 10px rgba(0, 0, 0, 0.06),
    0 0.5px 3px rgba(0, 0, 0, 0.04),
    inset 0 0.5px 0 rgba(255, 255, 255, 0.85),
    inset 0 -1px 2px rgba(0, 0, 0, 0.03);
  z-index: 0;
}

.glass-surface::before {
  content: '';
  position: absolute;
  z-index: 0;
  top: 30%;
  left: 50%;
  transform: translateX(-50%);
  width: calc(100% - 20px);
  height: calc(100% - 12px);
  border: 1px solid rgba(0, 0, 0, 0.7);
  border-radius: 999px;
  filter: blur(6px);
  pointer-events: none;
}

.glass-surface::after {
  content: '';
  position: absolute;
  z-index: 0;
  inset: 0;
  border-radius: inherit;
  filter: blur(2.5px);
  pointer-events: none;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.7) 0%,
    transparent 20%,
    transparent 80%,
    rgba(255, 255, 255, 0.7) 100%
  );
}

.liquid-pill {
  position: absolute;
  z-index: 1;
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  border: 1px double rgba(51, 51, 51, 0.08);
  box-shadow:
    inset 2px -2px 1px -1px rgba(255, 255, 255, 0.9),
    inset -2px 2px 1px -1px rgba(255, 255, 255, 0.9),
    inset 6px -6px 1px -6px rgba(255, 255, 255, 0.55),
    inset -6px 6px 1px -6px rgba(255, 255, 255, 0.55),
    inset 0 0 2px rgba(0, 0, 0, 0.8),
    0 2px 6px rgba(0, 0, 0, 0.12);
  pointer-events: none;
  will-change: left, width, top, bottom, border-radius;
  transition: border-radius 200ms ease-out;
}

.liquid-pill::before {
  content: '';
  position: absolute;
  inset: 3px;
  border: 1px solid rgba(0, 0, 0, 0.7);
  border-radius: 999px;
  filter: blur(5px);
  pointer-events: none;
}

.liquid-pill::after {
  content: '';
  position: absolute;
  inset: 1px;
  border-radius: 999px;
  filter: blur(2px);
  pointer-events: none;
  background: linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.75) 0%,
    transparent 20%,
    transparent 80%,
    rgba(255, 255, 255, 0.75) 100%
  );
}

.pill-glow {
  position: absolute;
  inset: 4px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 999px;
  filter: blur(1px);
  pointer-events: none;
}

.nav-item {
  position: relative;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  padding: 6px 15px;
  text-decoration: none;
  border-radius: 22px;
}
.nav-item:hover { text-decoration: none; }
.nav-item.active .ch {
  color: var(--color-text-primary);
  font-weight: var(--font-weight-semibold);
}

.ch {
  display: inline-block;
  white-space: pre;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  letter-spacing: var(--letter-spacing-normal);
  transform-origin: center center;
  transition:
    transform 120ms ease-out,
    color 280ms cubic-bezier(0.25, 0.1, 0.25, 1),
    text-shadow 180ms ease-out,
    filter 180ms ease-out;
  will-change: transform, color, text-shadow, font-weight, filter;
}
.ch.sp { width: 0.35em; }

@media (max-width: 768px) {
  .liquid-nav { padding: 3px; border-radius: 22px; gap: 0; }
  .nav-item { padding: 5px 9px; }
  .ch { font-size: var(--font-size-xs); }
}
</style>
