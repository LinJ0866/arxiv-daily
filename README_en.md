# 🚀 Daily arXiv AI Enhanced

> English | [中文](README.md)

Daily automated crawling of arXiv papers with AI-powered summaries and personalized recommendations.

## ✨ Features

### Core Features
- 📥 **Auto Crawling**: Scheduled crawling of latest arXiv papers
- 🤖 **AI Summaries**: Auto-generated TL;DR, motivation, method, results, conclusions (optional)
- ⭐ **Personalized Recommendations**: Smart recommendations based on likes, keywords, and authors
- ❤️ **Like & Collect**: Save favorite papers, support Zotero import
- 👥 **Multi-user**: Support multiple users with independent preferences and likes

### Recommendation Algorithm
- **Vector Similarity**: Embedding-based semantic matching (configurable weight)
- **Keyword Matching**: Match user's preferred keywords
- **Author Matching**: Match user's followed authors
- **Time Decay**: Recently liked papers have higher weight

## 📦 Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + SQLAlchemy + PostgreSQL |
| Frontend | Vue 3 + Vite + Pinia |
| Embedding | OpenAI-compatible API (e.g., DashScope) |
| LLM | OpenAI-compatible API (optional) |
| Deployment | Docker Compose |

## 🚀 Quick Start

### 1. Prerequisites

```bash
git clone https://github.com/your-username/daily-arXiv-ai-enhanced.git
cd daily-arXiv-ai-enhanced
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` file:

```bash
# Database
DATABASE_URL=postgresql://arxiv:password@db:5432/arxiv_daily

# Application
SECRET_KEY=your-secret-key-change-this

# Embedding (required)
EMBEDDING_API_KEY=your-api-key
EMBEDDING_API_BASE=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-v3-small

# LLM (optional)
LLM_API_KEY=
LLM_MODEL=deepseek-chat

# Crawler
ARXIV_CATEGORIES=cs.CV,cs.CL,cs.AI
```

### 3. Start Services

```bash
docker-compose up -d
docker-compose exec api python scripts/init_db.py --with-test-data
```

### 4. Access

- **Frontend**: http://localhost
- **API Docs**: http://localhost:8000/docs

### 5. Default Accounts

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |
| test | test123 | User |

## 📖 User Guide

### Registration / Login
1. Visit homepage, click "Register" in top right
2. Fill in username and password
3. Login with your credentials

### Browse Papers
- Homepage displays latest papers
- Filter by category (cs.CV, cs.AI, etc.)
- Filter by date
- Search by title, abstract, or author

### Like Papers
- Click ❤️ button on paper cards
- View all likes in "My Likes" page

### Import from Zotero
1. Export RDF file from Zotero
2. Go to "My Likes" page
3. Click "Import Zotero" button
4. Select the exported RDF file

### Set Preferences
1. Go to "Settings" page
2. Add preferred keywords (e.g., transformer, diffusion)
3. Add followed authors
4. Adjust recommendation weights

### Personalized Recommendations
- "Recommended for You" section appears after login
- Based on likes + keywords + authors
- Click "Refresh" in settings to update

### Admin Features
- View system status in "System" page
- View run history
- Manually trigger crawling
- Rebuild embeddings

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `DATABASE_URL` | ✅ | PostgreSQL connection string | - |
| `SECRET_KEY` | ✅ | JWT secret key | - |
| `EMBEDDING_API_KEY` | ✅ | Embedding API key | - |
| `EMBEDDING_API_BASE` | ✅ | Embedding API base URL | `https://api.openai.com/v1` |
| `EMBEDDING_MODEL` | ✅ | Embedding model name | `text-embedding-v3-small` |
| `LLM_API_KEY` | ❌ | LLM API key | - |
| `LLM_MODEL` | ❌ | LLM model name | `deepseek-chat` |
| `ARXIV_CATEGORIES` | ❌ | Categories to crawl | `cs.CV,cs.CL,cs.AI` |

### Recommendation Weights

Each user can configure independently:

| Weight | Description | Default |
|--------|-------------|---------|
| `weight_vector` | Vector similarity weight | 0.7 |
| `weight_keyword` | Keyword matching weight | 0.3 |
| `author_bonus` | Author match bonus | 0.5 |

## 🚢 CI/CD Configuration

The project uses GitHub Actions for automated build and deployment.

### Backend (Docker Image)

Automatically builds Docker image and pushes to Alibaba Cloud ACR.

**Configure Secrets:**

| Secret | Description |
|--------|-------------|
| `ACR_USERNAME` | Alibaba Cloud ACR username |
| `ACR_PASSWORD` | Alibaba Cloud ACR password |

**Image URL:**
```
registry.cn-hangzhou.aliyuncs.com/arxiv-daily/arxiv-daily:latest
```

### Frontend (GitHub Pages / Qiniu Cloud)

By default, deploys to GitHub Pages. Optionally deploy to Qiniu Cloud CDN.

**Configure Secrets:**

| Secret | Required | Description |
|--------|----------|-------------|
| `API_BASE_URL` | ❌ | Backend API URL (empty for relative path) |
| `QINIU_ENABLED` | ❌ | Set to `true` to enable Qiniu deployment |
| `QINIU_ACCESS_KEY` | ❌ | Qiniu Access Key |
| `QINIU_SECRET_KEY` | ❌ | Qiniu Secret Key |
| `QINIU_BUCKET` | ❌ | Qiniu Bucket name |
| `QINIU_DOMAIN` | ❌ | Qiniu CDN domain (e.g., `https://cdn.example.com`) |

#### Enable Qiniu Cloud Deployment

1. Go to GitHub repo Settings > Secrets and variables > Actions
2. Add the following Secrets:
   - `QINIU_ENABLED`: `true`
   - `QINIU_ACCESS_KEY`: Your Qiniu Access Key
   - `QINIU_SECRET_KEY`: Your Qiniu Secret Key
   - `QINIU_BUCKET`: Your Bucket name
   - `QINIU_DOMAIN`: Your CDN domain
3. After pushing code, frontend will deploy to both GitHub Pages and Qiniu Cloud

#### Custom Domain (GitHub Pages)

1. Go to GitHub repo Settings > Pages
2. Enter your domain in Custom domain
3. Configure DNS CNAME record pointing to `your-username.github.io`

## 🔧 Development

### Local Development

```bash
# Start database
docker-compose up -d db

# Install backend dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py --with-test-data

# Start backend
uvicorn app.main:app --reload --port 8000

# Start frontend
cd frontend
npm install
npm run dev
```

### Project Structure

```
.
├── app/                    # FastAPI backend
│   ├── api/                # API routes
│   ├── models/             # Database models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   └── main.py             # Entry point
├── frontend/               # Vue 3 frontend
│   ├── src/
│   │   ├── api/            # API client
│   │   ├── components/     # Components
│   │   ├── views/          # Pages
│   │   ├── stores/         # State management
│   │   └── router/         # Router
│   └── package.json
├── scripts/                # Utility scripts
├── migrations/             # Database migrations
├── docker-compose.yml      # Docker config
└── requirements.txt        # Python dependencies
```

## 📝 API Documentation

After starting the backend, visit http://localhost:8000/docs for complete API documentation.

### Main APIs

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | User login |
| GET | `/api/articles` | List articles |
| GET | `/api/articles/{id}` | Get article detail |
| POST | `/api/likes/{id}` | Like article |
| DELETE | `/api/likes/{id}` | Unlike article |
| GET | `/api/likes` | Get likes list |
| GET | `/api/recommendations` | Get recommendations |
| POST | `/api/recommendations/recompute` | Refresh recommendations |
| POST | `/api/zotero/import` | Import from Zotero |
| POST | `/api/system/rebuild-embeddings` | Rebuild embeddings |

## 📄 License

Apache-2.0

## 🙏 Acknowledgments

- [arXiv](https://arxiv.org/) - Paper data source
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Vue.js](https://vuejs.org/) - Frontend framework
- [pgvector](https://github.com/pgvector/pgvector) - PostgreSQL vector extension
