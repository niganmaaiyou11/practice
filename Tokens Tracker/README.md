# Tokens Tracker

一个个人 AI Token 用量追踪平台，支持多供应商用量记录、自动邮件导入、AI 模型排行榜、AI 周报等功能。

## ✨ 功能特性

### 📊 Token 用量追踪
- 手动记录每日各 AI 供应商的 Token 使用量（输入/输出/总计）
- 支持 OpenAI、Anthropic、Google、DeepSeek、xAI、Mistral、Moonshot、智谱、阿里、字节、MiniMax、阶跃星辰、百川等 13+ 供应商
- 按日期、供应商、模型筛选和排序

### 📈 数据分析仪表盘
- 4 个 KPI 摘要卡片（带动画数字滚动）
- 每日趋势图（面积图/折线图/柱状图，支持无限缩放）
- 模型用量分布图（水平柱状图/环形饼图）
- 供应商用量分布图
- 基于 models.json 定价数据的费用计算

### 📧 邮件自动导入
- Gmail OAuth2 连接（弹窗授权流程）
- IMAP 连接支持任意邮箱（QQ、163、126、Outlook 等）
- 13+ AI 供应商的账单/用量邮件自动解析
- 后台定时同步（每 15 分钟）
- 同步预览/试运行模式

### 🏆 AI 模型排行榜
- 数据来源于 llm-stats.com
- 6 维评分体系：推理 25%、编码 25%、知识 15%、工具使用 20%、长上下文 10%、视觉 5%
- 质量 vs 速度散点图
- 模态筛选（文本/图像/视频/TTS/STT）
- 中国模型筛选、开源/闭源筛选

### 📰 AI 周报
- 聚合 12 个 RSS 源（OpenAI、Google AI、Hugging Face、GitHub、The Verge 等）
- 自动分类（模型/行业/开源/工具/中国）
- 影响力评估（高/中/关注）
- 关键实体提取、自动生成摘要和要点

### 🔔 通知系统
- 应用内通知中心
- 未读计数角标
- 周报更新自动推送

### 🌍 国际化
- 支持 7 种语言：English、中文、日本語、한국어、Русский、Français、Español

### 🎨 UI 设计
- Apple 风格设计系统
- iOS 26 液态玻璃导航栏
- 毛玻璃（Glassmorphism）效果
- 深色模式支持
- 页面过渡动画

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Vue 3 + TypeScript + Vite + Pinia + Vue Router + Element Plus + ECharts |
| **后端** | Python + FastAPI + SQLAlchemy + Pydantic + Uvicorn |
| **数据库** | SQLite（自动创建，自动迁移） |
| **认证** | JWT（PyJWT）+ bcrypt + HMAC-SHA256 验证码 |
| **加密** | Fernet（OAuth Token / IMAP 密码加密存储） |
| **定时任务** | APScheduler（邮件同步 + 周报刷新） |
| **外部 API** | Gmail OAuth2、OpenRouter、LiteLLM、llm-stats.com |

## 🚀 快速开始

### 前置要求
- Python >= 3.10
- Node.js（含 npm）

**Windows：** 双击 `start.bat`

**macOS / Linux：**
```bash
chmod +x start.sh
./start.sh
```

启动后访问本地服务即可。

## ⚙️ 配置

### 环境变量（`backend/.env`）

```env
# JWT 签名密钥（生产环境请修改）
JWT_SECRET_KEY=your-secret-key

# Fernet 加密密钥（首次运行自动生成）
FERNET_KEY=your-fernet-key
```

### 可选：Gmail OAuth 邮件同步

```env
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/email/oauth-callback
```

> 不配置 Gmail OAuth 也可以使用 IMAP 方式连接任意邮箱。

## 📁 项目结构

```
Tokens Tracker/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── database.py          # 数据库引擎 & 会话
│   │   ├── models.py            # ORM 模型（8 张表）
│   │   ├── schemas.py           # Pydantic 请求/响应模型
│   │   ├── crud.py              # CRUD & 聚合查询
│   │   ├── auth.py              # JWT 认证 & 验证码
│   │   ├── email_*.py           # 邮件同步模块
│   │   ├── weekly_news.py       # AI 周报
│   │   └── routers/             # API 路由
│   ├── data/
│   │   └── models.json          # 供应商/模型注册表
│   └── scripts/                 # 数据同步脚本
├── frontend/
│   └── src/
│       ├── pages/               # 页面组件
│       ├── components/          # 通用组件
│       ├── stores/              # Pinia 状态管理
│       ├── api/                 # API 请求封装
│       ├── locales/             # 国际化翻译
│       └── composables/         # 组合式函数
├── start.bat                    # Windows 一键启动
└── start.sh                     # macOS/Linux 一键启动
```

## 📄 License

本项目仅供个人学习使用。
