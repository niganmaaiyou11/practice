<template>
  <div class="landing">
    <!-- Section 1: Hero -->
    <section class="hero">
      <div class="hero-bg" />
      <div class="hero-glow hero-glow--left" />
      <div class="hero-glow hero-glow--right" />
      <div class="hero-inner">
        <div class="hero-content">
          <p class="hero-eyebrow" :class="{ 'anim-reveal': true }">
            {{ t.landing?.eyebrow || 'AI Token Analytics' }}
          </p>
          <h1 class="hero-title" :class="{ 'anim-reveal': true }">
            <span class="hero-title__line">{{ t.landing?.heroTitleLine1 || 'Every token.' }}</span>
            <span class="hero-title__line hero-title__line--gradient">{{ t.landing?.heroTitleLine2 || 'Incredibly fast.' }}</span>
          </h1>
          <p class="hero-subtitle" :class="{ 'anim-reveal': true }">
            {{ t.landing?.heroSubtitle || 'Track and visualize your AI token usage across every major provider. Built for the age of intelligence.' }}
          </p>
          <div class="hero-cta" :class="{ 'anim-reveal': true }">
            <router-link to="/auth" class="cta-primary">
              {{ t.landing?.heroCTA || 'Get Started' }}
            </router-link>
            <a href="#section-track" class="cta-secondary">
              {{ t.landing?.heroSecondaryCTA || 'Learn More' }}
            </a>
          </div>
        </div>
        <div class="hero-visual" :style="heroParallaxStyle">
          <div class="hero-card-wrapper">
            <div class="hero-card">
              <div class="hero-card__dots">
                <span class="dot dot--red" />
                <span class="dot dot--yellow" />
                <span class="dot dot--green" />
              </div>
              <div class="hero-card__header">
                <span class="hero-card__title">Token Usage</span>
                <span class="hero-card__badge">Live</span>
              </div>
              <div class="hero-card__bars">
                <div class="bar" v-for="h in bars" :key="h" :style="{ height: h + '%' }" />
              </div>
              <div class="hero-card__stats">
                <div class="hero-card__stat">
                  <span class="hero-card__stat-val">2.4M</span>
                  <span class="hero-card__stat-label">Input</span>
                </div>
                <div class="hero-card__stat">
                  <span class="hero-card__stat-val">1.8M</span>
                  <span class="hero-card__stat-label">Output</span>
                </div>
                <div class="hero-card__stat">
                  <span class="hero-card__stat-val">4.2M</span>
                  <span class="hero-card__stat-label">Total</span>
                </div>
              </div>
            </div>
            <div
              v-for="(badge, i) in providerBadges"
              :key="i"
              class="provider-badge"
              :style="badgeStyle(badge)"
            >
              <ProviderIcon :provider="badge.provider" :size="40" />
            </div>
          </div>
        </div>
      </div>
      <div class="hero-scroll-indicator">
        <span class="hero-scroll-indicator__line" />
      </div>
    </section>

    <!-- Section 2: Track Everything -->
    <section
      id="section-track"
      class="section-feature"
      ref="trackRef"
      data-section="track"
    >
      <div class="section-feature__grid">
        <div class="section-feature__text">
          <p class="section-eyebrow" :class="{ 'anim-fade-up': sectionVisible.track }">
            {{ t.landing?.trackEyebrow || 'Unified Tracking' }}
          </p>
          <h2 class="section-headline" :class="{ 'anim-fade-up': sectionVisible.track }">
            {{ t.landing?.trackHeadline || 'All your AI usage. One place.' }}
          </h2>
          <p class="section-body" :class="{ 'anim-fade-up': sectionVisible.track }">
            {{ t.landing?.trackSubheadline || 'Track tokens across every major AI provider — from OpenAI to DeepSeek, all in a single dashboard.' }}
          </p>
          <ul class="feature-points" :class="{ 'anim-fade-up': sectionVisible.track }">
            <li>
              <span class="feature-points__icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              </span>
              {{ t.landing?.trackPt1 || 'Manual entry with smart provider detection' }}
            </li>
            <li>
              <span class="feature-points__icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              </span>
              {{ t.landing?.trackPt2 || 'Unlimited records for all your projects' }}
            </li>
            <li>
              <span class="feature-points__icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              </span>
              {{ t.landing?.trackPt3 || '7-language interface, switch anytime' }}
            </li>
          </ul>
        </div>
        <div class="section-feature__visual">
          <div class="provider-grid">
            <div
              v-for="(p, i) in providerCards"
              :key="i"
              class="provider-card"
              :class="{ 'anim-fade-up': sectionVisible.track }"
              :style="{ animationDelay: (300 + i * 100) + 'ms' }"
            >
              <div class="provider-card__icon">
                <ProviderIcon :provider="p.name" :size="36" />
              </div>
              <span class="provider-card__name">{{ p.name }}</span>
              <span class="provider-card__count">{{ p.count }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Section 3: Beautiful Analytics -->
    <section
      class="section-feature section-feature--alt"
      ref="analyticsRef"
      data-section="analytics"
    >
      <div class="section-feature__grid">
        <div class="section-feature__visual section-feature__visual--order-last">
          <div class="chart-mockup">
            <div class="chart-mockup__header">
              <div class="chart-mockup__header-left">
                <span class="chart-mockup__title">{{ t.landing?.chartLabel || 'Daily Trend' }}</span>
                <span class="chart-mockup__subtitle">Tokens</span>
              </div>
              <span class="chart-mockup__badge">7D</span>
            </div>
            <div class="chart-mockup__body">
              <div class="chart-mockup__plot">
                <div class="chart-mockup__grid">
                  <div class="chart-mockup__grid-line" v-for="n in 5" :key="n" />
                </div>
                <svg class="chart-mockup__area-svg" viewBox="0 0 400 200" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="inputGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stop-color="#0071e3" stop-opacity="0.3" />
                      <stop offset="100%" stop-color="#0071e3" stop-opacity="0" />
                    </linearGradient>
                    <linearGradient id="outputGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stop-color="#bf5af2" stop-opacity="0.2" />
                      <stop offset="100%" stop-color="#bf5af2" stop-opacity="0" />
                    </linearGradient>
                  </defs>
                  <path
                    d="M0,160 C20,150 40,140 60,130 C80,120 100,110 120,100 C140,90 160,80 180,75 C200,70 220,60 240,55 C260,50 280,45 300,40 C320,35 340,30 360,28 C380,26 400,22 400,22 L400,200 L0,200 Z"
                    fill="url(#inputGrad)"
                  />
                  <path
                    d="M0,180 C20,175 40,168 60,160 C80,152 100,148 120,142 C140,136 160,128 180,122 C200,118 220,110 240,105 C260,100 280,98 300,95 C320,90 340,85 360,80 C380,76 400,72 400,72 L400,200 L0,200 Z"
                    fill="url(#outputGrad)"
                  />
                  <path
                    d="M0,160 C20,150 40,140 60,130 C80,120 100,110 120,100 C140,90 160,80 180,75 C200,70 220,60 240,55 C260,50 280,45 300,40 C320,35 340,30 360,28 C380,26 400,22"
                    fill="none" stroke="#0071e3" stroke-width="2" vector-effect="non-scaling-stroke"
                  />
                  <path
                    d="M0,180 C20,175 40,168 60,160 C80,152 100,148 120,142 C140,136 160,128 180,122 C200,118 220,110 240,105 C260,100 280,98 300,95 C320,90 340,85 360,80 C380,76 400,72"
                    fill="none" stroke="#bf5af2" stroke-width="2" vector-effect="non-scaling-stroke"
                  />
                </svg>
              </div>
            </div>
            <div class="chart-mockup__axis">
              <span v-for="d in axisDays" :key="d">{{ d }}</span>
            </div>
          </div>
        </div>
        <div class="section-feature__text">
          <p class="section-eyebrow" :class="{ 'anim-fade-up': sectionVisible.analytics }">
            {{ t.landing?.analyticsEyebrow || 'Visual Analytics' }}
          </p>
          <h2 class="section-headline" :class="{ 'anim-fade-up': sectionVisible.analytics }">
            {{ t.landing?.analyticsHeadline || 'Beautiful charts. Zero hassle.' }}
          </h2>
          <p class="section-body" :class="{ 'anim-fade-up': sectionVisible.analytics }">
            {{ t.landing?.analyticsSubheadline || 'Stunning visualizations that make your token usage patterns crystal clear.' }}
          </p>
          <ul class="feature-points" :class="{ 'anim-fade-up': sectionVisible.analytics }">
            <li>
              <span class="feature-points__icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></span>
              {{ t.landing?.analyticsPt1 || 'Daily token trend with smooth area charts' }}
            </li>
            <li>
              <span class="feature-points__icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></span>
              {{ t.landing?.analyticsPt2 || 'Model breakdown by provider colors' }}
            </li>
            <li>
              <span class="feature-points__icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></span>
              {{ t.landing?.analyticsPt3 || 'Switch between area, line, bar, and pie views' }}
            </li>
          </ul>
        </div>
      </div>
    </section>

    <!-- Section 4: AI Leaderboard -->
    <section
      class="section-feature"
      ref="leaderboardRef"
      data-section="leaderboard"
    >
      <div class="section-feature__grid">
        <div class="section-feature__text">
          <p class="section-eyebrow" :class="{ 'anim-fade-up': sectionVisible.leaderboard }">
            {{ t.landing?.leaderboardEyebrow || 'Model Intelligence' }}
          </p>
          <h2 class="section-headline" :class="{ 'anim-fade-up': sectionVisible.leaderboard }">
            {{ t.landing?.leaderboardHeadline || 'Know the best. Build with confidence.' }}
          </h2>
          <p class="section-body" :class="{ 'anim-fade-up': sectionVisible.leaderboard }">
            {{ t.landing?.leaderboardSubheadline || 'Live AI model rankings powered by llm-stats.com. Compare reasoning, coding, knowledge, and more.' }}
          </p>
          <ul class="feature-points" :class="{ 'anim-fade-up': sectionVisible.leaderboard }">
            <li>
              <span class="feature-points__icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></span>
              {{ t.landing?.leaderboardPt1 || 'LLM Stats Score v1.0 — 6-axis comprehensive rating' }}
            </li>
            <li>
              <span class="feature-points__icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></span>
              {{ t.landing?.leaderboardPt2 || 'Quality vs Speed scatter plot visualization' }}
            </li>
            <li>
              <span class="feature-points__icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></span>
              {{ t.landing?.leaderboardPt3 || 'Filter by reasoning, coding, knowledge, and more' }}
            </li>
          </ul>
        </div>
        <div class="section-feature__visual">
          <div class="quadrant-chart">
            <div class="quadrant-chart__inner">
              <div class="quadrant-chart__axis-h" />
              <div class="quadrant-chart__axis-v" />
              <span class="quadrant-chart__label quadrant-chart__label--speed">Speed →</span>
              <span class="quadrant-chart__label quadrant-chart__label--quality">Quality ↑</span>
              <span class="quadrant-chart__quad quadrant-chart__quad--elite">Elite</span>
              <span class="quadrant-chart__quad quadrant-chart__quad--value">Value</span>
              <div
                v-for="(dot, i) in scatterDots"
                :key="i"
                class="quadrant-dot"
                :class="{
                  'quadrant-dot--pulse': dot.pulse,
                  'anim-fade-up': sectionVisible.leaderboard,
                }"
                :style="{
                  left: dot.x + '%',
                  bottom: dot.y + '%',
                  width: dot.size + 'px',
                  height: dot.size + 'px',
                  background: dot.color,
                  animationDelay: (dot.pulse ? 800 + i * 80 : i * 50) + 'ms',
                }"
              />
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Section 5: Email Auto-Sync -->
    <section
      class="section-feature section-feature--alt"
      ref="emailRef"
      data-section="email"
    >
      <div class="section-feature__grid">
        <div class="section-feature__visual section-feature__visual--order-last">
          <div class="email-flow">
            <div class="email-flow__line">
              <div class="email-flow__line-inner" />
            </div>
            <div
              v-for="(node, i) in emailNodes"
              :key="i"
              class="email-flow__node"
              :class="{ 'anim-fade-up': sectionVisible.email }"
              :style="{ animationDelay: (i * 250) + 'ms' }"
            >
              <div class="email-flow__dot" :style="{ background: node.color }">
                <component :is="node.icon" />
              </div>
              <div class="email-flow__info">
                <span class="email-flow__title">{{ node.title }}</span>
                <span class="email-flow__desc">{{ node.desc }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="section-feature__text">
          <p class="section-eyebrow" :class="{ 'anim-fade-up': sectionVisible.email }">
            {{ t.landing?.emailEyebrow || 'Auto Sync' }}
          </p>
          <h2 class="section-headline" :class="{ 'anim-fade-up': sectionVisible.email }">
            {{ t.landing?.emailHeadline || 'Set it and forget it.' }}
          </h2>
          <p class="section-body" :class="{ 'anim-fade-up': sectionVisible.email }">
            {{ t.landing?.emailSubheadline || 'Connect Gmail or any IMAP inbox. AI-powered parsing extracts token usage automatically.' }}
          </p>
          <ul class="feature-points" :class="{ 'anim-fade-up': sectionVisible.email }">
            <li>
              <span class="feature-points__icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></span>
              {{ t.landing?.emailPt1 || 'One-click Gmail OAuth connection' }}
            </li>
            <li>
              <span class="feature-points__icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></span>
              {{ t.landing?.emailPt2 || 'Automatic sync every 30 minutes' }}
            </li>
            <li>
              <span class="feature-points__icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></span>
              {{ t.landing?.emailPt3 || 'AI-powered usage extraction from emails' }}
            </li>
          </ul>
        </div>
      </div>
    </section>

    <!-- Section 6: Stats + Final CTA -->
    <section class="stats-cta">
      <p class="section-eyebrow" :class="{ 'anim-fade-up': sectionVisible.stats }">
        {{ t.landing?.statsEyebrow || 'Trusted Worldwide' }}
      </p>
      <h2 class="section-headline stats-headline" :class="{ 'anim-fade-up': sectionVisible.stats }">
        {{ t.landing?.statsHeadline || 'Thousands of developers track smarter.' }}
      </h2>
      <div class="stats-grid" ref="statsRef" data-section="stats">
        <div class="stat-item" v-for="(stat, i) in stats" :key="i">
          <span class="stat-number" :style="{ color: stat.colors?.[0] || '#0071e3' }">
            <span class="stat-number__gradient" :style="{ background: `linear-gradient(135deg, ${stat.colors?.[0] || '#0071e3'}, ${stat.colors?.[1] || '#bf5af2'})`, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }">{{ statDisplays[i] }}{{ i === 3 ? '+' : '' }}</span>
          </span>
          <span class="stat-label">{{ stat.label }}</span>
        </div>
      </div>
      <div class="cta-block" :class="{ 'anim-fade-up': sectionVisible.cta }">
        <h3 class="cta-headline">
          {{ t.landing?.ctaHeadline || 'Ready to take control?' }}
        </h3>
        <p class="cta-body">
          {{ t.landing?.ctaSubheadline || 'Start tracking in seconds. Free. No credit card required.' }}
        </p>
        <router-link to="/auth" class="cta-primary cta-primary--lg">
          {{ t.landing?.heroCTA || 'Get Started' }}
        </router-link>
      </div>
    </section>

    <!-- Footer -->
    <footer class="app-footer">
      <div class="app-footer__inner">
        <p class="footer-text">
          {{ t.landing?.footerText || '© 2026 AI Token Tracker. All rights reserved.' }}
        </p>
        <el-select
          v-model="localeStore.current"
          class="footer-locale"
          @change="onLocaleChange"
          size="small"
        >
          <el-option
            v-for="(name, code) in localeStore.localeNames"
            :key="code"
            :label="name"
            :value="code"
          />
        </el-select>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, h, onMounted, onUnmounted } from 'vue'
import { useLocaleStore } from '../stores/locale'
import { useModelsStore } from '../stores/models'
import { useCountUp } from '../composables/useCountUp'
import ProviderIcon from '../components/ProviderIcon.vue'
import axios from 'axios'
import type { Locale } from '../locales'

const localeStore = useLocaleStore()
const t = localeStore.t
const modelsStore = useModelsStore()

function onLocaleChange(locale: Locale) {
  localeStore.setLocale(locale)
  window.location.reload()
}

// Hero
const bars = [35, 55, 40, 70, 50, 85, 60, 75, 45, 65, 80, 55, 70, 40, 60, 50, 75, 65, 85, 90]

const scrollY = ref(0)
function onScroll() {
  scrollY.value = window.scrollY
}
const heroParallaxStyle = computed(() => ({
  transform: `translateY(${Math.min(scrollY.value * 0.04, 60)}px)`,
}))

const providerBadges = [
  { provider: 'OpenAI', orbitRadius: 170, duration: 22, offset: 0 },
  { provider: 'Anthropic', orbitRadius: 200, duration: 26, offset: 60 },
  { provider: 'Google', orbitRadius: 150, duration: 19, offset: 120 },
  { provider: 'DeepSeek', orbitRadius: 185, duration: 24, offset: 180 },
  { provider: 'Mistral', orbitRadius: 160, duration: 21, offset: 240 },
  { provider: 'Cohere', orbitRadius: 195, duration: 28, offset: 300 },
]

function badgeStyle(badge: typeof providerBadges[0]) {
  return {
    '--orbit-radius': badge.orbitRadius + 'px',
    '--orbit-duration': badge.duration + 's',
    '--orbit-offset': badge.offset + 'deg',
  }
}

// Provider cards
const providerCards = [
  { name: 'OpenAI', count: '12 models' },
  { name: 'Anthropic', count: '6 models' },
  { name: 'Google', count: '8 models' },
  { name: 'DeepSeek', count: '5 models' },
  { name: 'Mistral', count: '7 models' },
  { name: 'Cohere', count: '4 models' },
]

// Chart
const axisDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

// Scatter dots
const scatterDots = [
  { x: 12, y: 15, size: 14, color: '#10a37f', pulse: false },
  { x: 25, y: 35, size: 10, color: '#4285f4', pulse: false },
  { x: 18, y: 60, size: 10, color: '#7c3aed', pulse: false },
  { x: 35, y: 50, size: 12, color: '#d97706', pulse: false },
  { x: 48, y: 28, size: 10, color: '#0d9488', pulse: false },
  { x: 55, y: 72, size: 16, color: '#4f46e5', pulse: true },
  { x: 42, y: 80, size: 12, color: '#e11d48', pulse: false },
  { x: 62, y: 55, size: 14, color: '#10a37f', pulse: false },
  { x: 70, y: 40, size: 10, color: '#4285f4', pulse: false },
  { x: 78, y: 85, size: 18, color: '#d97706', pulse: true },
  { x: 58, y: 18, size: 10, color: '#7c3aed', pulse: false },
  { x: 85, y: 68, size: 16, color: '#4f46e5', pulse: true },
  { x: 72, y: 22, size: 10, color: '#0d9488', pulse: false },
  { x: 90, y: 48, size: 12, color: '#10a37f', pulse: false },
  { x: 50, y: 45, size: 10, color: '#e11d48', pulse: false },
]

// Email flow nodes
const emailNodes = computed(() => [
  {
    title: t.landing?.emailPt1 || 'One-click Gmail OAuth',
    desc: 'Connect in seconds',
    color: '#0071e3',
    icon: () =>
      h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round', innerHTML: '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>' }),
  },
  {
    title: t.landing?.emailPt3 || 'AI-Powered Parsing',
    desc: 'Extracts tokens automatically',
    color: '#bf5af2',
    icon: () =>
      h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round', innerHTML: '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>' }),
  },
  {
    title: t.landing?.emailPt2 || 'Auto Sync',
    desc: 'Every 30 minutes',
    color: '#ff375f',
    icon: () =>
      h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round', innerHTML: '<polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>' }),
  },
])

// Stats
const stats = computed(() => [
  { value: leaderProviders.value ?? modelsStore.providerCount, label: t.landing?.statsProviders || 'Providers', colors: ['#0071e3', '#bf5af2'] },
  { value: leaderModels.value ?? modelsStore.modelCount, label: t.landing?.statsModels || 'Models', colors: ['#bf5af2', '#ff375f'] },
  { value: 7, label: t.landing?.statsLanguages || 'Languages', colors: ['#ff375f', '#ff9f0a'] },
  { value: 999, label: t.landing?.statsRecords || 'Records Tracked', colors: ['#30d158', '#0071e3'] },
])

const statsVisible = ref(false)
const dataReady = ref(false)
const statsRef = ref<HTMLElement | null>(null)

const statTargets = Array.from({ length: 4 }, () => ref<number | undefined>(undefined))
const statDisplays = statTargets.map((t) => useCountUp(t, { duration: 2000 }))

const leaderModels = ref<number | null>(null)
const leaderProviders = ref<number | null>(null)
const leaderRecords = ref<number | null>(null)

async function fetchPublicStats() {
  try {
    const res = await axios.get('/api/leaderboard/public/summary')
    const data = res.data || {}
    leaderModels.value = data.total_models ?? null
    leaderProviders.value = data.total_providers ?? null
    leaderRecords.value = data.total_models ?? null
  } catch { /* fallback */ }
  dataReady.value = true
  if (statsVisible.value) triggerAnimation()
}

function triggerAnimation() {
  statTargets.forEach((t, i) => {
    setTimeout(() => { t.value = stats.value[i].value }, i * 200)
  })
}

// IntersectionObserver
const sectionVisible = reactive({
  track: false,
  analytics: false,
  leaderboard: false,
  email: false,
  stats: false,
  cta: false,
})

const trackRef = ref<HTMLElement | null>(null)
const analyticsRef = ref<HTMLElement | null>(null)
const leaderboardRef = ref<HTMLElement | null>(null)
const emailRef = ref<HTMLElement | null>(null)

let mainObserver: IntersectionObserver | null = null
let statsObserver: IntersectionObserver | null = null

onMounted(async () => {
  const apiPromise = fetchPublicStats()

  mainObserver = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          const key = (entry.target as HTMLElement).dataset.section as keyof typeof sectionVisible
          if (key && !sectionVisible[key]) {
            sectionVisible[key] = true
          }
        }
      }
    },
    { threshold: 0.12, rootMargin: '0px 0px -40px 0px' },
  )

  const sectionRefs: Record<string, HTMLElement | null> = {
    track: trackRef.value,
    analytics: analyticsRef.value,
    leaderboard: leaderboardRef.value,
    email: emailRef.value,
  }

  for (const [, el] of Object.entries(sectionRefs)) {
    if (el) mainObserver.observe(el)
  }

  statsObserver = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        statsVisible.value = true
        sectionVisible.stats = true
        if (dataReady.value) triggerAnimation()
        statsObserver?.disconnect()
        setTimeout(() => { sectionVisible.cta = true }, 800)
      }
    },
    { threshold: 0.2 },
  )
  if (statsRef.value) statsObserver.observe(statsRef.value)

  window.addEventListener('scroll', onScroll, { passive: true })
  await apiPromise
})

onUnmounted(() => {
  mainObserver?.disconnect()
  statsObserver?.disconnect()
  window.removeEventListener('scroll', onScroll)
})
</script>

<style scoped>
.landing {
  background: #000;
  color: #f5f5f7;
}

/* ========== HERO ========== */
.hero {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 120px 48px 80px;
  background: #000;
  position: relative;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 60% at 30% 20%, rgba(0, 113, 227, 0.08) 0%, transparent 60%),
    radial-gradient(ellipse 60% 70% at 70% 60%, rgba(191, 90, 242, 0.06) 0%, transparent 60%),
    radial-gradient(ellipse 50% 50% at 50% 80%, rgba(255, 55, 95, 0.04) 0%, transparent 50%);
}

.hero-glow {
  position: absolute;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.15;
  pointer-events: none;
}

.hero-glow--left {
  top: -200px;
  left: -100px;
  background: radial-gradient(circle, rgba(0, 113, 227, 0.6), transparent);
}

.hero-glow--right {
  bottom: -200px;
  right: -100px;
  background: radial-gradient(circle, rgba(191, 90, 242, 0.5), transparent);
}

.hero-inner {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 100px;
  max-width: 1300px;
  width: 100%;
}

.hero-content {
  max-width: 560px;
}

.hero-eyebrow {
  font-size: 14px;
  font-weight: 500;
  color: #0071e3;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: 20px;
  animation-delay: 0ms;
}

.hero-title {
  font-size: 72px;
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 0.98;
  margin-bottom: 28px;
}

.hero-title__line {
  display: block;
  color: #f5f5f7;
}

.hero-title__line--gradient {
  background: linear-gradient(135deg, #0071e3 0%, #bf5af2 50%, #ff375f 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 20px;
  font-weight: 400;
  color: #98989d;
  line-height: 1.45;
  margin-bottom: 36px;
  letter-spacing: -0.016em;
  animation-delay: 200ms;
}

.hero-cta {
  display: flex;
  align-items: center;
  gap: 20px;
  animation-delay: 400ms;
}

.cta-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 52px;
  padding: 0 28px;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  background: #0071e3;
  border-radius: 28px;
  text-decoration: none;
  transition: all 250ms cubic-bezier(0.25, 0.1, 0.25, 1);
  letter-spacing: -0.016em;
}

.cta-primary:hover {
  background: #0077ed;
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 113, 227, 0.4);
}

.cta-primary--lg {
  height: 60px;
  padding: 0 48px;
  font-size: 18px;
  border-radius: 32px;
  background: linear-gradient(135deg, #0071e3, #5856d6);
}

.cta-primary--lg:hover {
  background: linear-gradient(135deg, #0077ed, #6b69e8);
  box-shadow: 0 12px 40px rgba(0, 113, 227, 0.5);
}

.cta-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 52px;
  padding: 0 28px;
  font-size: 16px;
  font-weight: 500;
  color: #0071e3;
  background: transparent;
  border: 1px solid rgba(0, 113, 227, 0.3);
  border-radius: 28px;
  text-decoration: none;
  transition: all 250ms cubic-bezier(0.25, 0.1, 0.25, 1);
  letter-spacing: -0.016em;
}

.cta-secondary:hover {
  background: rgba(0, 113, 227, 0.08);
  border-color: rgba(0, 113, 227, 0.5);
}

/* Hero scroll indicator */
.hero-scroll-indicator {
  position: absolute;
  bottom: 32px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2;
}

.hero-scroll-indicator__line {
  display: block;
  width: 1px;
  height: 48px;
  background: linear-gradient(180deg, rgba(255,255,255,0.3), rgba(255,255,255,0));
  animation: scroll-float 2.5s ease-in-out infinite;
}

@keyframes scroll-float {
  0%, 100% { transform: translateY(0); opacity: 0.3; }
  50% { transform: translateY(8px); opacity: 1; }
}

/* Hero visual */
.hero-visual {
  position: relative;
  flex-shrink: 0;
}

.hero-card-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 420px;
  height: 480px;
}

.hero-card {
  background: #1c1c1e;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.04) inset;
  width: 340px;
  position: relative;
  z-index: 2;
  backdrop-filter: blur(20px);
}

.hero-card__dots {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.dot { width: 12px; height: 12px; border-radius: 50%; }
.dot--red { background: #ff5f57; }
.dot--yellow { background: #febc2e; }
.dot--green { background: #28c840; }

.hero-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.hero-card__title {
  font-size: 15px;
  font-weight: 600;
  color: #f5f5f7;
}

.hero-card__badge {
  font-size: 11px;
  font-weight: 600;
  color: #30d158;
  background: rgba(48, 209, 88, 0.12);
  padding: 3px 10px;
  border-radius: 10px;
}

.hero-card__bars {
  display: flex;
  align-items: flex-end;
  gap: 5px;
  height: 160px;
  margin-bottom: 20px;
}

.bar {
  flex: 1;
  background: linear-gradient(180deg, #0071e3, rgba(0, 113, 227, 0.15));
  border-radius: 3px 3px 0 0;
  animation: bar-rise 600ms cubic-bezier(0, 0, 0.58, 1) both;
}
.bar:nth-child(1) { animation-delay: 0ms; }
.bar:nth-child(2) { animation-delay: 30ms; }
.bar:nth-child(3) { animation-delay: 60ms; }
.bar:nth-child(4) { animation-delay: 90ms; }
.bar:nth-child(5) { animation-delay: 120ms; }
.bar:nth-child(6) { animation-delay: 150ms; }
.bar:nth-child(7) { animation-delay: 180ms; }
.bar:nth-child(8) { animation-delay: 210ms; }
.bar:nth-child(9) { animation-delay: 240ms; }
.bar:nth-child(10) { animation-delay: 270ms; }
.bar:nth-child(11) { animation-delay: 300ms; }
.bar:nth-child(12) { animation-delay: 330ms; }
.bar:nth-child(13) { animation-delay: 360ms; }
.bar:nth-child(14) { animation-delay: 390ms; }
.bar:nth-child(15) { animation-delay: 420ms; }
.bar:nth-child(16) { animation-delay: 450ms; }
.bar:nth-child(17) { animation-delay: 480ms; }
.bar:nth-child(18) { animation-delay: 510ms; }
.bar:nth-child(19) { animation-delay: 540ms; }
.bar:nth-child(20) { animation-delay: 570ms; }

@keyframes bar-rise {
  from { transform: scaleY(0); }
  to { transform: scaleY(1); }
}

.hero-card__stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.hero-card__stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.hero-card__stat-val {
  font-size: 18px;
  font-weight: 700;
  color: #f5f5f7;
  letter-spacing: -0.022em;
}

.hero-card__stat-label {
  font-size: 11px;
  color: #86868b;
  font-weight: 500;
}

/* Provider badges orbit */
.provider-badge {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  z-index: 1;
  animation: orbit var(--orbit-duration, 22s) linear infinite;
  animation-delay: calc(var(--orbit-offset, 0deg) * -1s / 360 * var(--orbit-duration, 22s));
}

.provider-badge :deep(.provider-icon) {
  transform: translate(-50%, -50%) translateX(var(--orbit-radius, 170px));
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.5);
  border-radius: 50%;
}

@keyframes orbit {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ========== SECTIONS ========== */
.section-feature {
  padding: 140px 48px;
  background: #000;
}

.section-feature--alt {
  background: #0a0a0a;
}

.section-feature__grid {
  max-width: 1300px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 100px;
  align-items: center;
}

.section-eyebrow {
  font-size: 14px;
  font-weight: 500;
  color: #0071e3;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: 16px;
}

.section-headline {
  font-size: 52px;
  font-weight: 700;
  letter-spacing: -0.025em;
  line-height: 1.05;
  margin-bottom: 24px;
  color: #f5f5f7;
}

.section-body {
  font-size: 18px;
  font-weight: 400;
  color: #98989d;
  line-height: 1.5;
  margin-bottom: 32px;
  letter-spacing: -0.016em;
}

/* Feature points */
.feature-points {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-points li {
  font-size: 15px;
  color: #98989d;
  line-height: 1.5;
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.feature-points__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(0, 113, 227, 0.1);
  color: #0071e3;
  flex-shrink: 0;
  margin-top: 1px;
}

/* ========== PROVIDER GRID ========== */
.provider-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  width: 100%;
  max-width: 480px;
}

.provider-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 12px;
  background: #1c1c1e;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 20px;
  transition: transform 300ms cubic-bezier(0.25, 0.1, 0.25, 1),
              border-color 300ms cubic-bezier(0.25, 0.1, 0.25, 1),
              box-shadow 300ms cubic-bezier(0.25, 0.1, 0.25, 1);
}

.provider-card:hover {
  transform: translateY(-4px);
  border-color: rgba(255, 255, 255, 0.12);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
}

.provider-card__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
}

.provider-card__name {
  font-size: 13px;
  font-weight: 600;
  color: #f5f5f7;
}

.provider-card__count {
  font-size: 11px;
  color: #86868b;
}

/* ========== CHART MOCKUP ========== */
.chart-mockup {
  background: #1c1c1e;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 24px;
  padding: 28px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
}

.chart-mockup__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.chart-mockup__header-left {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.chart-mockup__title {
  font-size: 15px;
  font-weight: 600;
  color: #f5f5f7;
}

.chart-mockup__subtitle {
  font-size: 12px;
  color: #86868b;
}

.chart-mockup__badge {
  font-size: 11px;
  font-weight: 600;
  color: #0071e3;
  background: rgba(0, 113, 227, 0.1);
  padding: 4px 12px;
  border-radius: 12px;
}

.chart-mockup__body {
  position: relative;
  margin-bottom: 16px;
}

.chart-mockup__plot {
  position: relative;
  height: 200px;
}

.chart-mockup__grid {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-bottom: 20px;
}

.chart-mockup__grid-line {
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.chart-mockup__area-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.chart-mockup__tooltip {
  position: absolute;
  right: 14%;
  top: 8%;
  background: rgba(0, 113, 227, 0.15);
  border: 1px solid rgba(0, 113, 227, 0.25);
  border-radius: 8px;
  padding: 6px 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  opacity: 0;
  transform: translateY(8px);
  transition: all 400ms cubic-bezier(0.175, 0.885, 0.32, 1.275);
  animation: tooltip-float 4s ease-in-out infinite;
}

.chart-mockup__tooltip--show {
  opacity: 1;
  transform: translateY(0);
  transition-delay: 1200ms;
}

@keyframes tooltip-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.chart-mockup__tooltip-label {
  font-size: 11px;
  color: #98989d;
}

.chart-mockup__tooltip-val {
  font-size: 13px;
  font-weight: 700;
  color: #0071e3;
}

.chart-mockup__axis {
  display: flex;
  justify-content: space-between;
  padding: 0 4px;
}

.chart-mockup__axis span {
  font-size: 10px;
  color: #86868b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 500;
}

/* ========== QUADRANT CHART ========== */
.quadrant-chart {
  background: #1c1c1e;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 24px;
  padding: 36px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
}

.quadrant-chart__inner {
  position: relative;
  width: 100%;
  padding-bottom: 100%;
}

.quadrant-chart__axis-h {
  position: absolute;
  bottom: 50%;
  left: 0;
  right: 0;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.quadrant-chart__axis-v {
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  border-left: 1px solid rgba(255, 255, 255, 0.08);
}

.quadrant-chart__label {
  position: absolute;
  font-size: 11px;
  color: #86868b;
  font-weight: 500;
}

.quadrant-chart__label--speed { bottom: -24px; right: 8px; }
.quadrant-chart__label--quality { left: -8px; top: -20px; writing-mode: vertical-lr; }

.quadrant-chart__quad {
  position: absolute;
  font-size: 10px;
  font-weight: 500;
  color: #86868b;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.quadrant-chart__quad--elite { top: 8%; right: 8%; color: #30d158; }
.quadrant-chart__quad--value { bottom: 8%; left: 8%; color: #ff9f0a; }

.quadrant-dot {
  position: absolute;
  border-radius: 50%;
  transform: translate(-50%, 50%);
  opacity: 0.85;
  transition: opacity 300ms cubic-bezier(0.25, 0.1, 0.25, 1);
}

.quadrant-dot:hover { opacity: 1; }

@keyframes pulse-ring {
  0% { box-shadow: 0 0 0 0 rgba(0, 113, 227, 0.4); }
  70% { box-shadow: 0 0 0 14px rgba(0, 113, 227, 0); }
  100% { box-shadow: 0 0 0 0 rgba(0, 113, 227, 0); }
}

.quadrant-dot--pulse {
  animation: pulse-ring 2.5s ease-out infinite;
}

/* ========== EMAIL FLOW ========== */
.email-flow {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 44px;
  width: 100%;
  max-width: 400px;
  padding: 20px 0;
}

.email-flow__node {
  display: flex;
  align-items: center;
  gap: 20px;
  position: relative;
  z-index: 2;
}

.email-flow__dot {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.email-flow__dot :deep(svg) {
  width: 24px;
  height: 24px;
}

.email-flow__info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.email-flow__title {
  font-size: 16px;
  font-weight: 600;
  color: #f5f5f7;
}

.email-flow__desc {
  font-size: 13px;
  color: #98989d;
}

.email-flow__line {
  position: absolute;
  left: 25px;
  top: 60px;
  bottom: 60px;
  width: 2px;
  background: rgba(255, 255, 255, 0.06);
  z-index: 1;
}

.email-flow__line-inner {
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, #0071e3 0%, #bf5af2 50%, #ff375f 100%);
  background-size: 100% 200%;
  animation: flow 3s ease-in-out infinite;
}

@keyframes flow {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 0% 100%; }
}

/* ========== STATS + CTA ========== */
.stats-cta {
  padding: 160px 48px 100px;
  background: #000;
  text-align: center;
}

.stats-headline {
  font-size: 48px;
  max-width: 700px;
  margin: 0 auto 64px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 32px;
  max-width: 900px;
  margin: 0 auto 100px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-number {
  font-size: 56px;
  font-weight: 700;
  letter-spacing: -0.025em;
  font-variant-numeric: tabular-nums;
  line-height: 1;
}

.stat-number__gradient {
  display: inline;
}

.stat-label {
  font-size: 14px;
  color: #98989d;
  font-weight: 500;
}

.cta-block {
  padding: 60px 0 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.cta-headline {
  font-size: 40px;
  font-weight: 700;
  color: #f5f5f7;
  letter-spacing: -0.025em;
}

.cta-body {
  font-size: 18px;
  color: #98989d;
  letter-spacing: -0.016em;
  margin-bottom: 16px;
}

/* ========== FOOTER ========== */
.app-footer {
  padding: 32px 48px;
  background: #000;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.app-footer__inner {
  max-width: 1300px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.footer-text {
  font-size: 12px;
  color: #86868b;
}

.footer-locale {
  width: 120px;
}

.footer-locale :deep(.el-input__wrapper) {
  border-radius: 8px !important;
  background: rgba(255, 255, 255, 0.06);
  border: none;
  box-shadow: none !important;
}

.footer-locale :deep(.el-input__wrapper:hover) {
  background: rgba(255, 255, 255, 0.1);
}

/* ========== ANIMATIONS ========== */
@keyframes fade-up {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

.anim-fade-up {
  animation: fade-up 600ms cubic-bezier(0, 0, 0.58, 1) both;
}

@keyframes reveal {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}

.anim-reveal {
  animation: reveal 800ms cubic-bezier(0.22, 0.61, 0.36, 1) both;
}

.anim-reveal:nth-child(1) { animation-delay: 0ms; }
.anim-reveal:nth-child(2) { animation-delay: 100ms; }
.anim-reveal:nth-child(3) { animation-delay: 200ms; }
.anim-reveal:nth-child(4) { animation-delay: 300ms; }

/* ========== RESPONSIVE ========== */
@media (max-width: 1200px) {
  .hero-title { font-size: 56px; }
  .section-headline { font-size: 42px; }
  .section-feature__grid { gap: 60px; }
  .hero-inner { gap: 60px; }
}

@media (max-width: 1024px) {
  .section-feature__grid {
    grid-template-columns: 1fr;
    gap: 48px;
  }

  .section-feature__visual--order-last {
    order: -1;
  }

  .hero-inner {
    flex-direction: column;
    gap: 48px;
    text-align: center;
  }

  .hero-content {
    max-width: 100%;
  }

  .hero-cta {
    justify-content: center;
  }

  .hero-title {
    font-size: 48px;
  }

  .hero-card-wrapper {
    width: 360px;
    height: 400px;
  }

  .section-headline {
    font-size: 36px;
  }

  .section-feature {
    padding: 100px 32px;
  }

  .stats-headline {
    font-size: 36px;
  }

  .stat-number {
    font-size: 44px;
  }
}

@media (max-width: 768px) {
  .hero {
    padding: 100px 24px 60px;
    min-height: auto;
  }

  .hero-title {
    font-size: 40px;
  }

  .hero-subtitle {
    font-size: 17px;
  }

  .hero-eyebrow {
    font-size: 12px;
  }

  .hero-card-wrapper {
    width: 300px;
    height: 360px;
  }

  .hero-card {
    width: 280px;
    padding: 18px;
  }

  .hero-card__bars {
    height: 120px;
  }

  .section-feature {
    padding: 80px 24px;
  }

  .section-feature__grid {
    gap: 40px;
  }

  .section-headline {
    font-size: 32px;
  }

  .section-body {
    font-size: 16px;
  }

  .section-eyebrow {
    font-size: 12px;
  }

  .provider-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    max-width: 320px;
  }

  .chart-mockup {
    padding: 20px;
  }

  .chart-mockup__plot {
    height: 160px;
  }

  .quadrant-chart {
    padding: 24px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 28px;
  }

  .stat-number {
    font-size: 40px;
  }

  .stats-headline {
    font-size: 28px;
  }

  .cta-headline {
    font-size: 28px;
  }

  .cta-body {
    font-size: 16px;
  }

  .stats-cta {
    padding: 100px 24px 60px;
  }

  .app-footer__inner {
    flex-direction: column;
    gap: 12px;
  }

  .section-feature--alt .section-feature__grid {
    display: flex;
    flex-direction: column;
  }

  .section-feature--alt .section-feature__visual {
    order: -1;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 34px;
  }

  .stats-grid {
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }

  .stat-number {
    font-size: 34px;
  }

  .hero-card-wrapper {
    width: 260px;
    height: 320px;
  }

  .hero-card {
    width: 250px;
  }

  .hero-cta {
    flex-direction: column;
    gap: 12px;
  }

  .cta-primary, .cta-secondary {
    width: 100%;
    max-width: 280px;
  }
}
</style>
