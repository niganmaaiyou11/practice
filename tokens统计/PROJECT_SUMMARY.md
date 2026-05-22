# AI Token 用量统计 - 项目总结

## 项目概述

一个用于手动统计每日各 AI 模型 Token 用量的 Web 应用，采用 Apple 风格设计语言和 DeepSeek API 平台风格的数据可视化。集成 **llm-stats.com 排行榜**，按 LLM Stats Score v1.0 综合得分排名。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端框架 | Vue 3 + TypeScript + Vite |
| UI 库 | Element Plus |
| 状态管理 | Pinia |
| 图表库 | ECharts + vue-echarts（树摇载入 LineChart / BarChart / PieChart / CanvasRenderer / Tooltip / Grid / Legend / DataZoom / ScatterChart） |
| HTTP 请求 | Axios |
| 国际化 | 自建 i18n（Pinia Store + 翻译文件） |
| 后端框架 | Python + FastAPI |
| 数据库 | SQLite |
| ORM | SQLAlchemy |

## 设计系统

- **Apple 风格设计语言**：浅灰背景 `#f5f5f7`，大圆角卡片（18-20px），微阴影层级，SF 风格字体排版
- **iOS 26 液态玻璃导航**：透明玻璃质感（`background: rgba(255,255,255,0.1)`），镜面高光边缘 + 浮动阴影定义玻璃形态，液态光斑自由滑动（rAF + lerp），字符级折射效果（CSS transition 400ms 平滑过渡）
- **玻璃拟态（Glassmorphism）**：粘性头部 `backdrop-filter: saturate(180%) blur(20px)`，图表悬浮提示同样采用毛玻璃效果
- **交互动画**：数字滚动动画（useCountUp composable）、卡片悬浮抬升、页面渐入过渡、图表数据切换动画、流动公告卡片轮播
- **CSS 自定义属性**：完整的设计令牌系统（颜色 / 字体 / 间距 / 圆角 / 阴影 / 过渡）

## 后端

### 目录结构

```
backend/
├── requirements.txt
├── token_tracker.db          # SQLite 数据库（自动创建）
├── data/
│   └── models.json           # 供应商/模型注册表（单一数据源）
├── scripts/
│   ├── sync_models.py        # 从 OpenRouter + LiteLLM 同步最新模型数据
│   └── scrape_llm_stats.py   # 从 llm-stats.com 爬取 AI 模型排行榜（含内置种子数据）
└── app/
    ├── __init__.py
    ├── main.py               # FastAPI 入口，CORS，启动建表 + 自动迁移 + 空库自动种子
    ├── database.py            # 数据库连接、Session、Base、run_migrations()
    ├── auth.py                # JWT 认证、密码哈希、CAPTCHA 令牌
    ├── models.py              # TokenUsage / User / LeaderboardEntry ORM 模型
    ├── schemas.py             # Pydantic 请求/响应模型（含排行榜 Schema）
    ├── crud.py                # CRUD + 聚合查询 + 排行榜排序/筛选/总结
    └── routers/
        ├── __init__.py
        ├── token_records.py   # Token 记录 API 路由
        ├── models.py          # 供应商/模型 API 路由
        ├── auth.py            # 认证 API 路由（登录/注册/刷新）
        └── leaderboard.py     # 排行榜 API 路由（列表/详情/同步/公共总结）
```

### 数据库模型

**表：`token_usage`**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键，自增 |
| date | Date | 日期，有索引 |
| model_name | String(100) | 模型名称 |
| provider | String(50) | 供应商，有索引 |
| input_tokens | Integer | 输入 Token 数，默认 0 |
| output_tokens | Integer | 输出 Token 数，默认 0 |
| total_tokens | Integer | 总 Token（写入时自动计算） |
| notes | String(500) | 备注，可空 |
| created_at | DateTime | 创建时间 |

复合索引：`(date, provider)`

**表：`users`**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键，自增 |
| email | String(255) | 邮箱，唯一，有索引 |
| password_hash | String(255) | bcrypt 密码哈希 |
| created_at | DateTime | 创建时间 |

**表：`leaderboard_entries`**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键，自增 |
| model_slug | String(200) | 模型唯一标识，有索引 |
| model_name | String(200) | 模型名称 |
| provider | String(100) | 供应商，有索引 |
| organization | String(200) | 组织/公司名 |
| overall_score | Float | LLM Stats Score v1.0 综合得分（0-1），有索引 |
| rank_overall | Integer | 综合得分排名 |
| score_gpqa | Float | GPQA Diamond 基准得分 |
| score_mmlu | Float | MMLU 基准得分 |
| score_mmlu_pro | Float | MMLU-Pro 基准得分 |
| score_math | Float | MATH 基准得分 |
| score_humaneval | Float | HumanEval 基准得分 |
| score_swebench | Float | SWE-Bench Verified 基准得分 |
| score_coding_arena | Float | Coding Arena 基准得分 |
| score_reasoning | Float | 推理轴得分（0-1） |
| score_coding | Float | 编程轴得分（0-1） |
| score_knowledge | Float | 知识轴得分（0-1） |
| score_tool_use | Float | 工具使用与智能体轴得分（0-1） |
| score_long_context | Float | 长上下文轴得分（0-1） |
| score_vision | Float | 视觉轴得分（0-1） |
| methodology_version | String(30) | 评分方法论版本（v1.0） |
| tokens_per_second | Float | 输出速度（tokens/s） |
| price_input | Float | 输入价格（$/M tokens） |
| price_output | Float | 输出价格（$/M tokens） |
| context_window | Integer | 上下文窗口大小 |
| max_output_tokens | Integer | 最大输出 Token 数 |
| knowledge_cutoff | String(50) | 知识截止日期 |
| modalities | String(200) | 支持模态（text, image, audio, video） |
| raw_data | Text | 原始 API JSON 数据 |
| fetched_at | DateTime | 数据获取时间 |

复合索引：`(provider, overall_score)`

### 排行榜评分体系 — LLM Stats Score v1.0

综合得分按 llm-stats.com v1.0 6 轴加权计算（0-100 分制）：

| 轴 | 权重 | 基准测试 |
|------|--------|------|
| **推理（Reasoning）** | 25% | GPQA Diamond, AIME 2025, FrontierMath |
| **编程（Coding）** | 25% | Coding Arena, SWE-Bench Verified, Terminal-Bench |
| **知识（Knowledge）** | 15% | HLE, MMMU-Pro, SimpleQA |
| **工具使用与智能体（Tool Use & Agents）** | 20% | TAU-Bench Retail, Toolathlon, MCP Atlas |
| **长上下文（Long Context）** | 10% | MRCR-v2, AA-LCR |
| **视觉（Vision）** | 5% | MMMU, ScreenSpot-Pro, CharXiv-R |

刮削时优先使用 API 返回的官方 `overall_score`，无法获取时回退到本地 v1.0 加权计算。支持按任意轴得分或基准测试排序。

### API 端点（前缀 `/api`）

| 方法 | 路径 | 说明 |
|------|------|------|
| **Token 记录** |
| GET | `/api/records` | 分页列表，支持按日期/供应商/模型筛选 |
| GET | `/api/records/{id}` | 单条记录 |
| POST | `/api/records` | 创建记录 |
| PUT | `/api/records/{id}` | 更新记录 |
| DELETE | `/api/records/{id}` | 删除记录 |
| **Token 统计** |
| GET | `/api/summary/daily` | 每日 Token 趋势 |
| GET | `/api/summary/by-model` | 按模型分布 |
| GET | `/api/summary/by-provider` | 按供应商分布 |
| GET | `/api/summary/totals` | 总统计数据 |
| **模型注册表** |
| GET | `/api/models` | 供应商/模型注册表（含配色、模型列表） |
| GET | `/api/models/providers` | 供应商名称列表 |
| POST | `/api/models/sync` | 触发模型同步（从 OpenRouter + LiteLLM 拉取） |
| **AI 排行榜** |
| GET | `/api/leaderboard/models` | 排行榜列表（分页 + 搜索 + 按任意字段排序） |
| GET | `/api/leaderboard/models/{id}` | 单模型详情 |
| GET | `/api/leaderboard/top` | Top N 模型（首页预览用） |
| GET | `/api/leaderboard/summary` | 排行榜统计（需认证） |
| GET | `/api/leaderboard/public/summary` | 排行榜统计（公开） |
| GET | `/api/leaderboard/providers` | 排行榜供应商列表 |
| POST | `/api/leaderboard/sync` | 触发 llm-stats.com 数据同步 |
| GET | `/api/leaderboard/last-updated` | 最后同步时间 |
| **认证** |
| GET | `/api/auth/captcha` | 获取 CAPTCHA 令牌 |
| POST | `/api/auth/register` | 注册 |
| POST | `/api/auth/login` | 登录 |
| POST | `/api/auth/refresh` | 刷新令牌 |
| GET | `/api/auth/me` | 获取当前用户信息 |
| **系统** |
| GET | `/api/health` | 健康检查 |

## 前端

### 目录结构

```
frontend/
├── index.html
├── package.json
├── vite.config.ts            # Vite 配置（含 /api 代理）
├── tsconfig.json
└── src/
    ├── main.ts               # 入口：注册 ElementPlus, Pinia, Router, ECharts
    ├── App.vue               # 根组件：液态玻璃导航 + 语言切换 + 路由过渡
    ├── env.d.ts              # TypeScript 声明
    ├── types/index.ts        # TypeScript 接口定义（含 LeaderboardEntry / LeaderboardSummary）
    ├── api/
    │   ├── tokenRecords.ts   # Axios 封装，Token 记录 API 调用
    │   ├── auth.ts           # 认证 API 调用
    │   └── leaderboard.ts    # 排行榜 API 调用（列表/详情/同步/公共总结）
    ├── router/index.ts       # 路由配置（/ 根据登录状态智能切换 Landing/Home）
    ├── stores/
    │   ├── tokenRecords.ts   # Pinia - Token 数据状态管理
    │   ├── locale.ts         # Pinia - 多语言状态管理
    │   ├── auth.ts           # Pinia - 认证状态管理
    │   ├── models.ts         # Pinia - 供应商/模型注册表缓存
    │   └── leaderboard.ts    # Pinia - 排行榜数据、筛选、排序、同步
    ├── locales/index.ts      # 7 种语言翻译文件（含排行榜 6 轴评分标注）
    ├── composables/
    │   └── useCountUp.ts     # 数字滚动动画 composable（requestAnimationFrame + easeOutCubic）
    ├── components/
    │   ├── LiquidNav.vue     # iOS 26 液态玻璃导航栏（透明玻璃 + rAF 液态光斑 + 字符折射）
    │   ├── AnnouncementCarousel.vue # 流动公告卡片轮播（CSS 无缝滚动 + 供应商配色）
    │   ├── FilterBar.vue     # 筛选栏（日期范围 + 供应商 + 筛选/重置）
    │   ├── RecordTable.vue   # 数据表格（分页、排序、编辑/删除操作）
    │   ├── RecordForm.vue    # 表单（新增/编辑记录，含模型同步刷新按钮）
    │   ├── SlideCaptcha.vue   # 滑动验证码组件
    │   ├── SummaryCards.vue  # 统计卡片（4 个指标，数字滚动动画，悬浮抬升）
    │   ├── DailyTrendChart.vue    # ECharts 波形面积图（平滑曲线 + 渐变填充 + 颜色深浅区分输入/输出）
    │   ├── ModelBreakdownChart.vue # ECharts 水平堆叠柱状图（供应商配色 + 毛玻璃悬浮提示）
    │   ├── LeaderboardPreview.vue  # 首页排行榜预览卡片（Top 5，金/银/铜排名）
    │   └── ProviderIcon.vue  # 供应商 SVG 图标组件
    ├── pages/
    │   ├── HomeRouter.vue    # / 路由包装器（根据登录态渲染 Landing 或 Home）
    │   ├── Home.vue          # 主页（欢迎语 + 统计卡片 + 流动公告 + 排行榜预览 + 快捷入口）
    │   ├── Landing.vue       # 公开落地页：特性介绍 + 统计数字动画
    │   ├── AuthPage.vue      # 登录/注册页面
    │   ├── Dashboard.vue     # 仪表盘页面（卡片 + 筛选 + 趋势图 + 分布图 双列网格布局）
    │   ├── RecordList.vue    # 记录列表页面
    │   ├── AddEditRecord.vue # 新增/编辑记录页面
    │   └── Leaderboard.vue   # AI 排行榜页面（综合得分排名 + 6 轴评分分解 + 散点图）
    └── styles/global.css     # 全局样式（Apple 设计系统 CSS 变量 + Element Plus 全局覆写）
```

### 图表详解

**每日趋势图（DailyTrendChart）**
- 三种可视化类型可切换：面积图（默认）/ 折线图 / 柱状图，通过卡片头部分段控件切换
- 面积图：ECharts smooth line（`smooth: 0.4`）+ stacked area，两条堆叠面积系列 + LinearGradient 渐变填充
- 折线图：独立线条，带圆点标记，清晰区分 Input/Output 趋势
- 柱状图：分组柱状，直观对比每日 Input/Output 用量
- **无限级缩放**：`dataZoom` inside（鼠标滚轮）+ slider（底部滑动条），支持无极缩放与平移
- 毛玻璃 tooltip（`backdrop-filter: blur(20px)`）
- xAxis 日期类别 / yAxis 自动缩写（1.2M, 500K）

**模型用量分布图（ModelBreakdownChart）**
- 两种可视化类型可切换：水平堆叠柱状图（默认）/ 环形饼图，通过卡片头部分段控件切换
- 水平柱状图：`yAxis: { type: 'category' }`，按总量降序排列，两条堆叠 bar 系列
- 环形饼图：内径 52% / 外径 78%，按模型总量占比展示，供应商配色 + 图例
- 模型超过 10 个时自动启用 **无限级缩放**（inside + slider），支持无极缩放滚动浏览
- 供应商配色：由 `models.json` 统一管理，覆盖 18 个供应商，未知供应商自动生成 MD5 取色
- **毛玻璃 tooltip**：自定义 HTML formatter，展示模型名、供应商、Input/Output/Total 三栏数据及百分比
- `barWidth: 16` / 非对称 `borderRadius`

### 排行榜详解（Leaderboard）

**排行榜页面**
- 顶部统计卡片：模型总数、平均综合得分、平均速度、平均输入价格（数字滚动动画）
- 筛选栏：搜索 + 供应商筛选 + 排序方式（综合得分 / 6 个轴得分 / 速度 / 价格 / 上下文 / 各基准测试 / 模型名）+ 升降序切换
- 表格列：排名（金/银/铜色）、模型（ProviderIcon + 名称）、供应商（品牌色标签）、综合得分（百分比 + 进度条）、速度、输入/输出价格、上下文窗口
- 得分别表头悬停显示 LLM Stats Score v1.0 6 轴加权方法论文档
- 行展开：6 轴得分分解卡片（推理 25% / 编程 25% / 知识 15% / 工具使用与智能体 20% / 长上下文 10% / 视觉 5%），含各轴基准测试明细
- **Quality vs Speed 散点图**：X 轴综合得分 / Y 轴速度，气泡大小 = 上下文窗口，供应商配色，毛玻璃 tooltip
- 同步按钮：一键从 llm-stats.com 拉取最新排行榜数据

**首页排行榜预览（LeaderboardPreview）**
- Top 5 模型卡片列表，金/银/铜排名徽章（渐变色）
- 每张卡片展示：排名、ProviderIcon、模型名（供应商色点）、综合得分、速度、价格
- 悬浮水平位移动画效果
- "View Full Leaderboard" 链接跳转完整排行榜页

**数据刮削（scrape_llm_stats.py）**
- 主数据源：`https://llm-stats.com/stats/v1/models` API
- 回退方案：HTML 页面解析（`__NEXT_DATA__` / `__INITIAL_STATE__`）
- 最终回退：40 条内置种子数据（主流模型完整覆盖）
- 支持从 API 响应中提取 6 轴分项得分和所有基准测试
- 自动分配 `rank_overall`（按综合得分降序，NULL 排最后）
- 启动时空库自动种子（非阻塞子进程）

### 路由

| 路径 | 组件 | 说明 | 需认证 |
|------|------|------|--------|
| `/` | HomeRouter.vue | 智能首页：未登录显示 Landing，已登录显示 Home | 否 |
| `/auth` | AuthPage.vue | 登录/注册页面 | 否 |
| `/dashboard` | Dashboard.vue | 仪表盘：统计卡片 + 筛选 + 趋势图 + 分布图 | 是 |
| `/records` | RecordList.vue | 记录列表：筛选栏 + 表格 + 分页 | 是 |
| `/records/add` | AddEditRecord.vue | 添加记录表单 | 是 |
| `/records/:id/edit` | AddEditRecord.vue | 编辑记录表单（回填数据） | 是 |
| `/leaderboard` | Leaderboard.vue | AI 排行榜：综合得分排名 + 6 轴分解 + 散点图 | 是 |

### 多语言支持

| 语言 | 标识 |
|------|------|
| English（默认） | en |
| 中文 | zh-CN |
| 日本語 | ja |
| 한국어 | ko |
| Русский | ru |
| Français | fr |
| Español | es |

语言选择保存到 `localStorage`，切换时所有 UI 文字、Element Plus 组件和图表标签同步更新。

## 关键设计决策

1. **ECharts 替代 uPlot**：uPlot 缺乏样条插值、堆叠柱状、富 HTML tooltip 和动画过渡。ECharts 树摇后仅载入所需模块，bundle 影响可控。散点图额外按需载入 ScatterChart。
2. **自定义 count-up，无额外依赖**：`useCountUp` composable 约 40 行 `requestAnimationFrame` + `easeOutCubic`，无需引入 countup.js 或 @vueuse/motion。
3. **自定义导航替代 el-menu**：Element Plus 菜单默认样式与 Apple 美学冲突，改用 `<router-link>` 实现简洁导航。
4. **数据库自动建表 + 自动迁移**：使用 `Base.metadata.create_all()` 启动时创建新表，`run_migrations()` 通过 `ALTER TABLE` 为已有表安全添加缺失列，无需 Alembic 迁移。
5. **total_tokens 存储为列**：写入时计算 `input + output`，简化聚合查询。
6. **供应商/模型集中注册**：`models.json` 为单一数据源，后端 API 下发，前端 Pinia Store 缓存。`allow-create` 仍保留支持自定义输入。前端刷新按钮一键调用 `POST /api/models/sync` 后端运行 `sync_models.py` 从 OpenRouter + LiteLLM 拉取最新模型列表。
7. **单 Pinia Store**：`tokenRecords` 和 `leaderboard` 分别作为 Token 数据和排行榜数据的单一数据源。
8. **Vite 代理**：开发时 `/api` 代理到后端，避免 CORS 问题。
9. **自建 i18n**：基于 Pinia Store + 翻译文件，无需额外依赖。排行榜 6 轴评分标注已纳入全部 7 种语言。
10. **`from __future__ import annotations`**：避免 Pydantic 模型字段名与类型名冲突（如 `date` 字段与 `datetime.date` 类型）。
11. **登录记忆**：登录成功后自动保存邮箱和混淆密码到 `localStorage`。72 小时内再次登录时，点击邮箱输入框自动提示并补全密码；超过 72 小时仅提示邮箱，需手动输入密码。
12. **交互式模型同步**：添加记录页面顶部显示当前供应商/模型数量及更新时间，点击刷新按钮即可从 OpenRouter + LiteLLM 拉取最新模型列表，同步完成后自动重载注册表。
13. **智能首页路由**：`/` 根据登录状态智能切换——未登录显示 Landing 产品介绍页，已登录显示 Home 主页（统计概览 + 流动公告 + 排行榜预览 + 快捷入口）。登录后默认跳转 `/` 而非直接进入仪表盘。
14. **流动公告卡片轮播**：Home 页使用 CSS `@keyframes translateX` + 重复列表技法实现无缝水平滚动。卡片展示最近 Token 记录（供应商色点 + 模型名 + Token 数 + 日期），悬浮暂停，边缘渐变遮罩。
15. **iOS 26 液态玻璃导航**：自行设计 `LiquidNav` 组件——透明玻璃背景仅由镜面高光边缘（`inset 0 0.5px`）+ 浮动阴影定义形态。液态光斑通过 `requestAnimationFrame` + lerp 缓动跟随鼠标自由滑动，光斑经过文字时逐字折射变色（CSS transition 400ms 平滑过渡）。不依赖任何第三方动画库。
16. **LLM Stats Score v1.0 评分体系**：综合得分优先使用 llm-stats.com API 返回的官方值，无法获取时回退到本地 6 轴加权计算。爬虫支持 API JSON → HTML 解析 → 内置种子数据三级回退。
17. **HMAC 签名 CAPTCHA**：滑动验证码基于 HMAC-SHA256 时间戳签名，5 分钟有效期，由后端生成令牌并验证。

## 启动方式

```bash
cd backend
python -m venv venv && source venv/Scripts/activate && pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

cd ../frontend
npm install && npm run dev
```

或直接运行根目录 `start.bat`。
