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
  slug: string
  colorVariant: boolean
  brandColor: string
  abbr: string
}

// Map a display provider name to a lobehub icon slug, brand color, and
// a two-letter abbreviation used by the fallback avatar. `colorVariant`
// switches between `<slug>-color` (full-color brand mark) and `<slug>`
// (monochrome glyph) depending on which one each provider ships.
const PROVIDERS: Record<string, ProviderEntry> = {
  OpenAI:           { slug: 'openai',     colorVariant: false, brandColor: '#10A37F', abbr: 'OA' },
  Anthropic:        { slug: 'claude',     colorVariant: true,  brandColor: '#D97757', abbr: 'AN' },
  Google:           { slug: 'gemini',     colorVariant: true,  brandColor: '#4285F4', abbr: 'GO' },
  Meta:             { slug: 'meta',       colorVariant: true,  brandColor: '#0467DF', abbr: 'ME' },
  DeepSeek:         { slug: 'deepseek',   colorVariant: true,  brandColor: '#4D6BFE', abbr: 'DS' },
  xAI:              { slug: 'xai',        colorVariant: false, brandColor: '#000000', abbr: 'XA' },
  Mistral:          { slug: 'mistral',    colorVariant: true,  brandColor: '#FA520F', abbr: 'MI' },
  NVIDIA:           { slug: 'nvidia',     colorVariant: true,  brandColor: '#76B900', abbr: 'NV' },
  Alibaba:          { slug: 'qwen',       colorVariant: true,  brandColor: '#615CED', abbr: 'AL' },
  'Alibaba (Qwen)': { slug: 'qwen',       colorVariant: true,  brandColor: '#615CED', abbr: 'AL' },
  Qwen:             { slug: 'qwen',       colorVariant: true,  brandColor: '#615CED', abbr: 'QW' },
  'Moonshot AI':    { slug: 'kimi',       colorVariant: true,  brandColor: '#3D3D3D', abbr: 'MO' },
  Moonshot:         { slug: 'kimi',       colorVariant: true,  brandColor: '#3D3D3D', abbr: 'MO' },
  Kimi:             { slug: 'kimi',       colorVariant: true,  brandColor: '#3D3D3D', abbr: 'KM' },
  'Zhipu AI':       { slug: 'chatglm',    colorVariant: true,  brandColor: '#1E2EFF', abbr: 'ZA' },
  Zhipu:            { slug: 'chatglm',    colorVariant: true,  brandColor: '#1E2EFF', abbr: 'ZA' },
  Cohere:           { slug: 'cohere',     colorVariant: true,  brandColor: '#39594D', abbr: 'CO' },
  Perplexity:       { slug: 'perplexity', colorVariant: true,  brandColor: '#22B8CD', abbr: 'PE' },
  Amazon:           { slug: 'aws',        colorVariant: true,  brandColor: '#FF9900', abbr: 'AM' },
  'AI21 Labs':      { slug: 'ai21',       colorVariant: false, brandColor: '#E91E63', abbr: 'A2' },
  AI21:             { slug: 'ai21',       colorVariant: false, brandColor: '#E91E63', abbr: 'A2' },
  'Stability AI':   { slug: 'stability',  colorVariant: true,  brandColor: '#660091', abbr: 'SB' },
  Stability:        { slug: 'stability',  colorVariant: true,  brandColor: '#660091', abbr: 'SB' },
  ByteDance:        { slug: 'doubao',     colorVariant: true,  brandColor: '#0089FF', abbr: 'BY' },
  Doubao:           { slug: 'doubao',     colorVariant: true,  brandColor: '#0089FF', abbr: 'DB' },
  MiniMax:          { slug: 'minimax',    colorVariant: true,  brandColor: '#F23F5D', abbr: 'MM' },
  StepFun:          { slug: 'stepfun',    colorVariant: true,  brandColor: '#003EFB', abbr: 'ST' },
  Baidu:            { slug: 'baidu',      colorVariant: true,  brandColor: '#2932E1', abbr: 'BD' },
  Grok:             { slug: 'grok',       colorVariant: false, brandColor: '#000000', abbr: 'GR' },
  Gemma:            { slug: 'gemma',      colorVariant: true,  brandColor: '#1E88E5', abbr: 'GM' },
}

const ICON_CDN = 'https://registry.npmmirror.com/@lobehub/icons-static-svg/latest/files/icons'

const entry = computed<ProviderEntry | null>(() => {
  if (!props.provider) return null
  return PROVIDERS[props.provider] || PROVIDERS[props.provider.trim()] || null
})

const iconUrl = computed(() => {
  const e = entry.value
  if (!e) return null
  const slug = e.colorVariant ? `${e.slug}-color` : e.slug
  return `${ICON_CDN}/${slug}.svg`
})

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
