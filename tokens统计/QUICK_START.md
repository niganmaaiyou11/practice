# AI Token 用量统计 - 启动教程

## 前置条件

- **Python** >= 3.10
- **Node.js**（含 npm）

## 最快启动（一键脚本）

### Windows 用户

双击项目根目录的 `start.bat`

### macOS / Linux 用户

```bash
chmod +x start.sh
./start.sh
```

脚本会自动安装依赖、创建虚拟环境、启动前后端。

---

## 手动启动（分步）

### 第一步：安装依赖

```bash
# 后端
cd backend
python -m pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 第二步：启动后端

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

> 启动成功后访问 http://localhost:8000/docs 可查看 API 文档

### 第三步：启动前端

另开一个终端：

```bash
cd frontend
npm run dev
```

### 第四步：打开应用

浏览器访问：**http://localhost:5173**

---

## 更新模型列表

供应商和模型数据来自 OpenRouter + LiteLLM 社区接口，运行以下命令即可拉取最新模型：

```bash
cd backend
python scripts/sync_models.py
```

> 更新后后端会自动重载（需以 `--reload` 方式启动），刷新浏览器即可看到最新模型。

---

## 发给别人使用

将整个 `git/` 文件夹打包（zip）发给对方，对方解压后：

1. 确保已安装 Python 和 Node.js
2. Windows 双击 `start.bat`，macOS/Linux 运行 `./start.sh`
3. 浏览器打开 `http://localhost:5173`

> 对方的数据会保存在他自己的 `backend/token_tracker.db` 中，不会与你冲突。

---

## 常见问题

### 端口被占用

```bash
# Windows - 查看端口占用
netstat -ano | findstr "8000"
# 杀掉进程（替换 PID）
taskkill /F /PID <进程ID>

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

### 数据库重置

删除 `backend/token_tracker.db` 后重新启动即可。

---

## 项目目录

```
git/
├── start.bat            # Windows 一键启动
├── start.sh             # macOS/Linux 一键启动
├── backend/             # Python 后端
│   ├── scripts/         # sync_models.py 模型同步脚本
│   └── data/            # models.json 供应商/模型注册表
├── frontend/            # Vue 前端
├── PROJECT_SUMMARY.md   # 项目详细总结
├── QUICK_START.md       # 本文件
└── .gitignore
```
