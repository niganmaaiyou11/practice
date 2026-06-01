<template>
  <span
    class="provider-icon"
    :style="{
      width: sizePx,
      height: sizePx,
      borderRadius: radius,
      background: showFallback ? brandColor : '#ffffff',
    }"
    :title="provider"
  >
    <img
      v-if="iconUrl && !error"
      :src="iconUrl"
      :alt="provider"
      class="provider-icon__img"
      loading="lazy"
      @error="onError"
    />
    <span
      v-else
      class="provider-icon__letter"
      :style="{ fontSize: letterFontSize }"
    >
      {{ abbreviation }}
    </span>
  </span>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = withDefaults(defineProps<{
  provider: string
  size?: number
  radius?: string
}>(), {
  size: 32,
  radius: '8px',
})

const error = ref(false)

watch(() => props.provider, () => {
  error.value = false
})

interface ProviderEntry {
  iconUrl: string | null
  brandColor: string
  abbr: string
}

const LOBEHUB_ICON_CDN = 'https://registry.npmmirror.com/@lobehub/icons-static-svg/latest/files/icons'
const simpleIcon = (slug: string, color: string) => `https://cdn.simpleicons.org/${slug}/${color.replace('#', '')}`
const lobeIcon = (slug: string, color = true) => `${LOBEHUB_ICON_CDN}/${slug}${color ? '-color' : ''}.svg`

const PROVIDERS: Record<string, ProviderEntry> = {
  OpenAI:           { iconUrl: lobeIcon('openai', false), brandColor: '#10A37F', abbr: 'OA' },
  Anthropic:        { iconUrl: lobeIcon('claude'),        brandColor: '#D97757', abbr: 'AN' },
  Google:           { iconUrl: lobeIcon('gemini'),        brandColor: '#4285F4', abbr: 'GO' },
  Meta:             { iconUrl: lobeIcon('meta'),          brandColor: '#0467DF', abbr: 'ME' },
  DeepSeek:         { iconUrl: lobeIcon('deepseek'),      brandColor: '#4D6BFE', abbr: 'DS' },
  xAI:              { iconUrl: lobeIcon('xai', false),    brandColor: '#000000', abbr: 'XA' },
  Mistral:          { iconUrl: lobeIcon('mistral'),       brandColor: '#FA520F', abbr: 'MI' },
  NVIDIA:           { iconUrl: lobeIcon('nvidia'),        brandColor: '#76B900', abbr: 'NV' },
  Alibaba:          { iconUrl: lobeIcon('qwen'),          brandColor: '#615CED', abbr: 'AL' },
  'Alibaba (Qwen)': { iconUrl: lobeIcon('qwen'),          brandColor: '#615CED', abbr: 'AL' },
  Qwen:             { iconUrl: lobeIcon('qwen'),          brandColor: '#615CED', abbr: 'QW' },
  'Moonshot AI':    { iconUrl: lobeIcon('kimi'),          brandColor: '#3D3D3D', abbr: 'MO' },
  'Moonshot (Kimi)': { iconUrl: lobeIcon('kimi'),         brandColor: '#3D3D3D', abbr: 'MO' },
  Moonshot:         { iconUrl: lobeIcon('kimi'),          brandColor: '#3D3D3D', abbr: 'MO' },
  Kimi:             { iconUrl: lobeIcon('kimi'),          brandColor: '#3D3D3D', abbr: 'KM' },
  'Zhipu AI':       { iconUrl: lobeIcon('zhipu'),         brandColor: '#1E2EFF', abbr: 'ZA' },
  'Zhipu (GLM)':    { iconUrl: lobeIcon('zhipu'),         brandColor: '#1E2EFF', abbr: 'ZA' },
  Zhipu:            { iconUrl: lobeIcon('zhipu'),         brandColor: '#1E2EFF', abbr: 'ZA' },
  GLM:              { iconUrl: lobeIcon('zhipu'),         brandColor: '#1E2EFF', abbr: 'GL' },
  Cohere:           { iconUrl: lobeIcon('cohere'),        brandColor: '#39594D', abbr: 'CO' },
  Perplexity:       { iconUrl: lobeIcon('perplexity'),    brandColor: '#22B8CD', abbr: 'PE' },
  Amazon:           { iconUrl: lobeIcon('aws'),           brandColor: '#FF9900', abbr: 'AM' },
  'AI21 Labs':      { iconUrl: lobeIcon('ai21', false),   brandColor: '#E91E63', abbr: 'A2' },
  AI21:             { iconUrl: lobeIcon('ai21', false),   brandColor: '#E91E63', abbr: 'A2' },
  'Stability AI':   { iconUrl: lobeIcon('stability'),     brandColor: '#660091', abbr: 'SB' },
  Stability:        { iconUrl: lobeIcon('stability'),     brandColor: '#660091', abbr: 'SB' },
  ByteDance:        { iconUrl: lobeIcon('doubao'),        brandColor: '#0089FF', abbr: 'BY' },
  Doubao:           { iconUrl: lobeIcon('doubao'),        brandColor: '#0089FF', abbr: 'DB' },
  MiniMax:          { iconUrl: lobeIcon('minimax'),       brandColor: '#F23F5D', abbr: 'MM' },
  StepFun:          { iconUrl: lobeIcon('stepfun'),       brandColor: '#003EFB', abbr: 'ST' },
  Baidu:            { iconUrl: lobeIcon('baidu'),         brandColor: '#2932E1', abbr: 'BD' },
  'Baidu (ERNIE)':  { iconUrl: lobeIcon('baidu'),         brandColor: '#2932E1', abbr: 'BD' },
  Xiaomi:           { iconUrl: simpleIcon('xiaomi', '#FF6900'), brandColor: '#FF6900', abbr: 'MI' },
  MiMo:             { iconUrl: simpleIcon('xiaomi', '#FF6900'), brandColor: '#FF6900', abbr: 'MI' },
  Muse:             { iconUrl: null,                      brandColor: '#7C3AED', abbr: 'MU' },
  LongCat:          { iconUrl: null,                      brandColor: '#F59E0B', abbr: 'LC' },
  Grok:             { iconUrl: lobeIcon('grok', false),   brandColor: '#000000', abbr: 'GR' },
  Gemma:            { iconUrl: lobeIcon('gemma'),         brandColor: '#1E88E5', abbr: 'GM' },
}

const entry = computed<ProviderEntry | null>(() => {
  if (!props.provider) return null
  return PROVIDERS[props.provider] || PROVIDERS[props.provider.trim()] || null
})

const iconUrl = computed(() => entry.value?.iconUrl || null)

const brandColor = computed(() => entry.value?.brandColor || 'var(--color-bg-tertiary, #888)')
const abbreviation = computed(() => {
  if (entry.value) return entry.value.abbr
  if (!props.provider) return '?'
  return props.provider.slice(0, 2).toUpperCase()
})

const showFallback = computed(() => !iconUrl.value || error.value)
const sizePx = computed(() => `${props.size}px`)
const letterFontSize = computed(() => `${Math.max(10, Math.round(props.size * 0.38))}px`)

function onError() {
  error.value = true
}
</script>

<style scoped>
.provider-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: transform 0.15s ease-out;
}

.provider-icon__img {
  width: 72%;
  height: 72%;
  object-fit: contain;
  display: block;
}

.provider-icon__letter {
  font-weight: 700;
  color: #fff;
  letter-spacing: 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.15);
  line-height: 1;
}
</style>
