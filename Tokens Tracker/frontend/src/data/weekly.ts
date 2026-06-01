export interface WeeklyItem {
  slug: string
  title: string
  summary: string
  category: 'model' | 'industry' | 'openSource' | 'tool' | 'china'
  impact: 'High' | 'Medium' | 'Watch'
  readingTime: string
  publishedAt: string
  body: string[]
  takeaways: string[]
}

export const weeklyHighlights = [
  'Frontier model updates are increasingly focused on agent reliability, coding accuracy, and lower-latency inference.',
  'Open-source releases continue to narrow the gap for coding, long-context, and on-device deployment scenarios.',
  'Pricing and context-window changes remain important signals for choosing models in production workflows.',
]

export const weeklyItems: WeeklyItem[] = [
  {
    slug: 'model-releases-shift-to-workflow-reliability',
    title: 'Model releases keep shifting from raw scores to workflow reliability',
    summary: 'The most relevant updates this week emphasize tool use, coding agents, and stable multi-step execution rather than benchmark wins alone.',
    category: 'model',
    impact: 'High',
    readingTime: '4 min read',
    publishedAt: '2026-05-27',
    body: [
      'The most interesting model updates are no longer only about a higher leaderboard score. Providers are increasingly describing progress through reliability in real workflows: multi-step coding, tool calling, browser actions, and long-running task execution.',
      'For teams choosing models, this changes the evaluation question. A model that is slightly lower on a benchmark but more stable under retries, file edits, and tool use may be the better production choice. This is especially true for agentic coding, where a single failed step can erase the benefit of stronger raw reasoning.',
      'Token usage also becomes more important in this environment. Reliable workflows often require planning, tool observations, retries, and review passes. Tracking total cost across these steps gives a more realistic picture than comparing single-call prices.',
    ],
    takeaways: [
      'Treat workflow reliability as a first-class model selection metric.',
      'Compare total task cost, not only price per million tokens.',
      'Use leaderboard scores as a starting point, then validate on your own tasks.',
    ],
  },
  {
    slug: 'coding-assistants-move-to-autonomous-execution',
    title: 'AI coding assistants continue moving toward autonomous task execution',
    summary: 'Developer tools are adding deeper repo context, terminal actions, and review loops, making token cost visibility more important for teams.',
    category: 'industry',
    impact: 'High',
    readingTime: '3 min read',
    publishedAt: '2026-05-27',
    body: [
      'AI coding products are becoming less like autocomplete and more like task runners. The key product direction is clear: understand the repository, make edits, run checks, review diffs, and continue until the requested outcome is complete.',
      'This expands the value of coding assistants, but it also makes usage harder to reason about. A single visible request can trigger many model calls behind the scenes. Without usage tracking, teams may underestimate the cost of repeated test runs, long context windows, and review loops.',
      'The practical next step is to evaluate coding assistants by completed task quality, latency, and token spend together. Looking at only one of those dimensions gives an incomplete picture.',
    ],
    takeaways: [
      'Autonomous coding workflows make token observability more valuable.',
      'Completed task cost is a better unit than per-message cost.',
      'Teams should compare assistant behavior on real repository tasks.',
    ],
  },
  {
    slug: 'open-models-for-private-workloads',
    title: 'Open models gain traction for private and cost-sensitive workloads',
    summary: 'Teams are evaluating open-weight models where data control, predictable hosting cost, or offline use matters more than top leaderboard rank.',
    category: 'openSource',
    impact: 'Medium',
    readingTime: '3 min read',
    publishedAt: '2026-05-27',
    body: [
      'Open-weight models continue to improve in areas that matter for internal deployments: coding, long-context summarization, structured extraction, and private data workflows. Even when they do not lead every benchmark, they can be attractive because deployment constraints are different from public chatbot constraints.',
      'The biggest advantage is control. Organizations can tune inference infrastructure, isolate sensitive data, and forecast cost using their own traffic patterns. This matters for teams with compliance requirements or high-volume repetitive workloads.',
      'The tradeoff remains operational complexity. Running models well requires infrastructure, monitoring, evaluation, and upgrade planning. Open models are not automatically cheaper unless the workload is stable enough to justify that operational investment.',
    ],
    takeaways: [
      'Open models are strongest when privacy or predictable cost matters.',
      'Infrastructure cost should be compared against hosted API spend.',
      'Operational maturity determines whether self-hosting pays off.',
    ],
  },
  {
    slug: 'ai-tool-stacks-converge-on-observability',
    title: 'AI tool stacks are converging around evaluation and observability',
    summary: 'More products are pairing prompts, traces, evals, and usage analytics so teams can compare quality, latency, and spend together.',
    category: 'tool',
    impact: 'Medium',
    readingTime: '4 min read',
    publishedAt: '2026-05-27',
    body: [
      'The AI tooling market is consolidating around a common workflow: capture prompts and responses, trace tool calls, run evaluations, and attach cost metrics. This reflects a maturing view of AI applications as systems that need measurement, not just prompts that need editing.',
      'For product teams, the useful insight is that model quality cannot be separated from operations. A feature may look good in a demo but fail under real traffic because of latency, inconsistent outputs, or cost spikes. Observability makes those tradeoffs visible.',
      'Usage analytics are becoming part of this stack because cost is now a product constraint. Teams want to know which features, users, models, and providers are responsible for spend before optimization work begins.',
    ],
    takeaways: [
      'Prompt management, evals, traces, and cost tracking are merging.',
      'AI product decisions should compare quality, latency, and spend together.',
      'Usage visibility helps identify which optimizations are worth doing.',
    ],
  },
  {
    slug: 'chinese-providers-compete-on-price-performance',
    title: 'Chinese AI providers remain strong in price-performance competition',
    summary: 'Domestic models continue to stand out in cost-efficient inference, coding assistants, and localized product integrations.',
    category: 'china',
    impact: 'Watch',
    readingTime: '3 min read',
    publishedAt: '2026-05-27',
    body: [
      'Chinese AI providers remain highly competitive in price-performance, particularly for workloads where latency, cost, Chinese language quality, or local ecosystem integration are important. The market is moving quickly, with frequent model updates and aggressive inference pricing.',
      'For developers, the opportunity is practical: compare domestic models for coding assistance, structured extraction, summarization, and customer-facing Chinese language experiences. In many cases, the best model is not the global benchmark leader but the one that fits deployment and cost constraints.',
      'The main challenge is keeping comparisons current. Rankings, prices, context limits, and API availability can shift quickly. A weekly review cadence is usually more realistic than relying on one-time model selection.',
    ],
    takeaways: [
      'Domestic models are especially worth testing for Chinese-language and cost-sensitive use cases.',
      'Price-performance can matter more than absolute benchmark rank.',
      'Revisit model choices regularly because this segment changes quickly.',
    ],
  },
]

export const modelMovements = [
  'Watch for new high-context models entering production pricing tiers.',
  'Compare speed and output price before switching coding workloads.',
  'Re-check Chinese model rankings when using the China AI filter.',
]

export function findWeeklyItem(slug: string) {
  return weeklyItems.find((item) => item.slug === slug)
}
