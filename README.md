# 🚀 Daily arXiv AI Enhanced

> [English](README_en.md) | 中文

每日自动爬取 arXiv 论文，AI 摘要增强，个性化推荐系统

## ✨ 功能特性

### 核心功能
- 📥 **自动爬取**：定时爬取 arXiv 最新论文
- 🤖 **AI 摘要**：自动生成 TL;DR、动机、方法、结果、结论（可选）
- ⭐ **个性化推荐**：基于喜欢列表 + 关键词 + 作者的智能推荐
- ❤️ **喜欢收藏**：收藏喜欢的论文，支持 Zotero 导入
- 👥 **多用户**：支持多用户，独立偏好和喜欢列表

### 推荐算法
- **向量相似度**：基于 Embedding 的语义匹配（权重可配置）
- **关键词匹配**：匹配用户设置的偏好关键词
- **作者匹配**：匹配用户关注的作者
- **时间衰减**：最近喜欢的论文权重更高

## 📦 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | FastAPI + SQLAlchemy + PostgreSQL |
| 前端 | Vue 3 + Vite + Pinia |
| Embedding | OpenAI 兼容 API（如阿里云 DashScope） |
| LLM | OpenAI 兼容 API（可选） |
| 部署 | Docker Compose |

## 🚀 快速开始

### 1. 环境准备

```bash
git clone https://github.com/your-username/daily-arXiv-ai-enhanced.git
cd daily-arXiv-ai-enhanced
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
# 数据库
DATABASE_URL=postgresql://arxiv:password@db:5432/arxiv_daily

# 应用
SECRET_KEY=your-secret-key-change-this

# Embedding（必填）
EMBEDDING_API_KEY=your-api-key
EMBEDDING_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
EMBEDDING_MODEL=text-embedding-v4

# LLM（可选）
LLM_API_KEY=
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL=deepseek-chat

# 爬虫配置
ARXIV_CATEGORIES=cs.CV,cs.CL,cs.AI
```

### 3. 启动服务

```bash
docker-compose up -d
docker-compose exec api python scripts/init_db.py --with-test-data
```

### 4. 访问应用

- **前端**：http://localhost
- **API 文档**：http://localhost:8000/docs

### 5. 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| test | test123 | 普通用户 |

## 📖 使用教程

### 用户功能

#### 注册/登录
1. 访问首页，点击右上角"注册"
2. 填写用户名和密码完成注册
3. 使用注册的账号登录

#### 浏览论文
- 首页显示最新论文列表
- 支持按分类筛选（cs.CV、cs.AI 等）
- 支持按日期筛选
- 支持搜索（标题、摘要、作者）

#### 喜欢论文
- 点击论文卡片上的 ❤️ 按钮收藏
- 在"我的喜欢"页面查看所有收藏

#### 导入 Zotero 文献
1. 从 Zotero 导出 RDF 文件
2. 进入"我的喜欢"页面
3. 点击"导入 Zotero"按钮
4. 选择导出的 RDF 文件

#### 设置偏好
1. 进入"设置"页面
2. 添加偏好关键词（如 transformer、diffusion）
3. 添加关注的作者
4. 调整推荐权重

#### 个性化推荐
- 登录后首页显示"猜你喜欢"板块
- 推荐基于喜欢列表 + 关键词 + 作者
- 可在设置页点击"刷新推荐"

### 管理员功能

#### 系统管理
- 进入"系统"页面查看定时任务状态
- 查看运行历史记录
- 手动触发爬取
- 重建 Embedding

#### 设置管理员
```bash
docker-compose exec api python scripts/init_db.py --set-admin username
```

## ⚙️ 配置说明

### 环境变量

| 变量 | 必填 | 说明 | 默认值 |
|------|------|------|--------|
| `DATABASE_URL` | ✅ | PostgreSQL 连接字符串 | - |
| `SECRET_KEY` | ✅ | JWT 密钥 | - |
| `EMBEDDING_API_KEY` | ✅ | Embedding API 密钥 | - |
| `EMBEDDING_API_BASE` | ✅ | Embedding API 地址 | `https://api.openai.com/v1` |
| `EMBEDDING_MODEL` | ✅ | Embedding 模型名称 | `text-embedding-v3-small` |
| `LLM_API_KEY` | ❌ | LLM API 密钥 | - |
| `LLM_MODEL` | ❌ | LLM 模型名称 | `deepseek-chat` |
| `ARXIV_CATEGORIES` | ❌ | 爬取分类 | `cs.CV,cs.CL,cs.AI` |

### 推荐权重

每个用户可独立配置：

| 权重 | 说明 | 默认值 |
|------|------|--------|
| `weight_vector` | 向量相似度权重 | 0.7 |
| `weight_keyword` | 关键词匹配权重 | 0.3 |
| `author_bonus` | 作者匹配加分 | 0.5 |

## 🚢 CI/CD 配置

项目使用 GitHub Actions 自动构建和部署。

### 后端（Docker 镜像）

自动构建 Docker 镜像并推送到阿里云 ACR。

**配置 Secrets：**

| Secret | 说明 |
|--------|------|
| `ACR_USERNAME` | 阿里云 ACR 用户名 |
| `ACR_PASSWORD` | 阿里云 ACR 密码 |

**镜像地址：**
```
registry.cn-hangzhou.aliyuncs.com/arxiv-daily/arxiv-daily:latest
```

### 前端（GitHub Pages / 七牛云）

默认部署到 GitHub Pages，可选部署到七牛云。

**配置 Secrets：**

| Secret | 必填 | 说明 |
|--------|------|------|
| `API_BASE_URL` | ❌ | 后端 API 地址（留空使用相对路径） |
| `QINIU_ENABLED` | ❌ | 设为 `true` 启用七牛云部署 |
| `QINIU_ACCESS_KEY` | ❌ | 七牛云 Access Key |
| `QINIU_SECRET_KEY` | ❌ | 七牛云 Secret Key |
| `QINIU_BUCKET` | ❌ | 七牛云 Bucket |
| `QINIU_DOMAIN` | ❌ | 七牛云 CDN 域名 |

#### 启用七牛云部署

1. 在 GitHub 仓库 Settings > Secrets and variables > Actions
2. 添加以下 Secrets：
   - `QINIU_ENABLED`: `true`
   - `QINIU_ACCESS_KEY`: 你的七牛云 Access Key
   - `QINIU_SECRET_KEY`: 你的七牛云 Secret Key
   - `QINIU_BUCKET`: 你的 Bucket 名称
   - `QINIU_DOMAIN`: 你的 CDN 域名（如 `https://cdn.example.com`）
3. 推送代码后，前端会同时部署到 GitHub Pages 和七牛云

#### 配置自定义域名（GitHub Pages）

1. 在 GitHub 仓库 Settings > Pages
2. 在 Custom domain 输入你的域名
3. 配置 DNS CNAME 记录指向 `your-username.github.io`

## 🔧 开发

### 本地开发

```bash
# 启动数据库
docker-compose up -d db

# 安装后端依赖
pip install -r requirements.txt

# 初始化数据库
python scripts/init_db.py --with-test-data

# 启动后端
uvicorn app.main:app --reload --port 8000

# 启动前端
cd frontend
npm install
npm run dev
```

### 项目结构

```
.
├── app/                    # FastAPI 后端
│   ├── api/                # API 路由
│   ├── models/             # 数据库模型
│   ├── schemas/            # Pydantic Schemas
│   ├── services/           # 业务逻辑
│   └── main.py             # 入口
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── api/            # API 封装
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   ├── stores/         # 状态管理
│   │   └── router/         # 路由
│   └── package.json
├── scripts/                # 脚本工具
├── migrations/             # 数据库迁移
├── docker-compose.yml      # Docker 配置
└── requirements.txt        # Python 依赖
```

## 📄 许可证

Apache-2.0

## 🙏 致谢

- [arXiv](https://arxiv.org/) - 论文数据源
- [FastAPI](https://fastapi.tiangolo.com/) - Web 框架
- [Vue.js](https://vuejs.org/) - 前端框架
- [pgvector](https://github.com/pgvector/pgvector) - PostgreSQL 向量扩展
