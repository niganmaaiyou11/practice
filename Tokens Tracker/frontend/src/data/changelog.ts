export interface ChangelogEntry {
  date: string
  summary: string
  details: string[]
}

export const changelog: ChangelogEntry[] = [
  {
    date: '2026-06-01',
    summary: '新增更新日志页面，记录网站维护与变更历史。',
    details: [
      '新增 Changelog 页面（/changelog），支持按天查看更新记录',
      '每条记录提供"大致摘要"和"详细说明"两种视图',
      '导航栏新增"更新日志"入口，位于设置旁',
      '页面仅对已登录用户可见',
    ],
  },
]
