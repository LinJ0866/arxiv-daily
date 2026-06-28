"""
FastAPI 应用入口
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.database import init_db, get_db
from app.models.user import User
from app.api.auth import get_current_user

# 创建调度器
scheduler = AsyncIOScheduler()


async def run_daily_pipeline():
    """每日定时任务：爬取文章 + 计算 Embedding + 计算推荐"""
    import asyncio
    from datetime import date, datetime

    print(f"[{datetime.now()}] Starting daily pipeline...")

    try:
        # 在线程池中运行同步的 pipeline 脚本
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _run_pipeline_sync)
        print(f"[{datetime.now()}] Daily pipeline completed: {result}")
    except Exception as e:
        print(f"[{datetime.now()}] Daily pipeline failed: {e}")


def _run_pipeline_sync():
    """同步运行 pipeline（在线程池中执行）"""
    import sys
    import os
    import json
    from datetime import date, datetime

    # 添加项目根目录到路径
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from app.database import SessionLocal
    from app.models.article import Article, ArticleEmbedding, ArticleAI
    from app.models.pipeline_log import PipelineLog
    from app.services.embedding_service import get_embeddings

    db = SessionLocal()
    stats = {"crawled": 0, "saved": 0, "embedded": 0, "recommended": 0}

    # 创建日志记录
    log = PipelineLog(
        run_date=date.today(),
        started_at=datetime.utcnow(),
        status="running"
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    try:
        # Step 1: 爬取论文
        import arxiv
        client = arxiv.Client()
        all_articles = []
        seen_ids = set()

        for category in settings.categories_list:
            search = arxiv.Search(
                query=f"cat:{category}",
                max_results=100,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            for paper in client.results(search):
                paper_id = paper.entry_id.split('/')[-1]
                if paper_id not in seen_ids:
                    seen_ids.add(paper_id)
                    all_articles.append({
                        'id': paper_id,
                        'title': paper.title,
                        'authors': [str(a) for a in paper.authors],
                        'categories': list(paper.categories),
                        'summary': paper.summary,
                        'pdf': paper.pdf_url,
                        'abs': paper.entry_id,
                        'comment': paper.comment or '',
                    })

        stats["crawled"] = len(all_articles)

        # Step 2: 存入数据库（去重）
        for article_data in all_articles:
            existing = db.query(Article).filter(Article.id == article_data['id']).first()
            if existing:
                continue
            article = Article(
                id=article_data['id'],
                title=article_data.get('title', ''),
                authors=article_data.get('authors', []),
                categories=article_data.get('categories', []),
                summary=article_data.get('summary'),
                pdf_url=article_data.get('pdf'),
                abs_url=article_data.get('abs'),
                comment=article_data.get('comment'),
                crawled_at=date.today()
            )
            db.add(article)
            stats["saved"] += 1
        db.commit()

        # Step 3: 计算 Embedding
        articles_without_emb = db.query(Article).filter(
            Article.crawled_at == date.today(),
            ~Article.id.in_(db.query(ArticleEmbedding.article_id))
        ).all()

        if articles_without_emb:
            texts = [a.summary or a.title for a in articles_without_emb]
            embeddings = get_embeddings(texts)
            for article, embedding in zip(articles_without_emb, embeddings):
                db_embedding = ArticleEmbedding(
                    article_id=article.id,
                    embedding=embedding.tolist(),
                    model_name=settings.embedding_model
                )
                db.add(db_embedding)
            db.commit()
            stats["embedded"] = len(articles_without_emb)

        # Step 4: 计算推荐（所有用户）
        from app.services.recommendation_service import compute_all_users_recommendations
        stats["recommended"] = compute_all_users_recommendations(db)

        # 更新日志为成功
        log.finished_at = datetime.utcnow()
        log.status = "success"
        log.crawled_count = stats["crawled"]
        log.saved_count = stats["saved"]
        log.embedded_count = stats["embedded"]
        log.recommended_count = stats["recommended"]
        db.commit()

    except Exception as e:
        # 更新日志为失败
        log.finished_at = datetime.utcnow()
        log.status = "failed"
        log.error_message = str(e)
        db.commit()
        print(f"Pipeline error: {e}")
        raise
    finally:
        db.close()

    return stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库并注册定时任务
    """
    # 启动时
    print("Starting arXiv Daily AI Enhanced API...")
    print(f"Database: {settings.database_url.split('@')[-1] if '@' in settings.database_url else 'configured'}")
    print(f"LLM: {'enabled' if settings.llm_enabled else 'disabled'}")
    print(f"Embedding: {settings.embedding_model}")

    # 注册每日定时任务（UTC 01:30，北京时间 09:30）
    scheduler.add_job(
        run_daily_pipeline,
        CronTrigger(hour=1, minute=30),
        id="daily_pipeline",
        name="Daily arXiv Pipeline",
        replace_existing=True
    )
    scheduler.start()
    print("Scheduler started: daily pipeline at 01:30 UTC")

    yield

    # 关闭时
    scheduler.shutdown()
    print("Scheduler stopped")
    print("Shutting down...")


# 创建 FastAPI 应用
app = FastAPI(
    title="arXiv Daily AI Enhanced",
    description="arXiv 论文每日推荐系统 API",
    version="2.0.0",
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# 注册路由
# ============================================

from app.api.auth import router as auth_router
from app.api.articles import router as articles_router
from app.api.likes import router as likes_router
from app.api.recommendations import router as recommendations_router
from app.api.preferences import router as preferences_router
from app.api.zotero import router as zotero_router

app.include_router(auth_router)
app.include_router(articles_router)
app.include_router(likes_router)
app.include_router(recommendations_router)
app.include_router(preferences_router)
app.include_router(zotero_router)


# ============================================
# 根路由
# ============================================

@app.get("/")
async def root():
    """API 根路径"""
    return {
        "name": "arXiv Daily AI Enhanced",
        "version": "2.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}


@app.get("/api/scheduler/status")
async def scheduler_status():
    """查看定时任务状态"""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else None,
        })
    return {"jobs": jobs}


@app.post("/api/scheduler/run-now")
async def run_pipeline_now(
    current_user: User = Depends(get_current_user)
):
    """手动触发 pipeline（仅 admin 可用）"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can trigger pipeline"
        )
    import asyncio
    asyncio.create_task(run_daily_pipeline())
    return {"status": "triggered", "message": "Pipeline started in background"}


@app.get("/api/scheduler/history")
async def get_pipeline_history(
    limit: int = 10,
    db = Depends(get_db)
):
    """获取 Pipeline 运行历史"""
    from app.models.pipeline_log import PipelineLog

    logs = db.query(PipelineLog).order_by(
        PipelineLog.started_at.desc()
    ).limit(limit).all()

    return {
        "history": [
            {
                "id": log.id,
                "run_date": log.run_date.isoformat(),
                "started_at": log.started_at.isoformat(),
                "finished_at": log.finished_at.isoformat() if log.finished_at else None,
                "status": log.status,
                "crawled_count": log.crawled_count,
                "saved_count": log.saved_count,
                "embedded_count": log.embedded_count,
                "recommended_count": log.recommended_count,
                "error_message": log.error_message,
            }
            for log in logs
        ]
    }


@app.post("/api/system/rebuild-embeddings")
async def rebuild_embeddings(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """重建所有 embedding（仅 admin 可用）"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can rebuild embeddings"
        )

    import asyncio
    asyncio.create_task(_rebuild_embeddings_async())

    return {"status": "started", "message": "Embedding rebuild started in background"}


async def _rebuild_embeddings_async():
    """异步重建所有 embedding"""
    from app.database import SessionLocal
    from app.models.article import Article, ArticleEmbedding
    from app.models.user import UserInterest
    from app.services.embedding_service import get_embeddings

    db = SessionLocal()
    try:
        print("Starting embedding rebuild...")

        # Step 1: 重建文章 embedding
        articles = db.query(Article).all()
        print(f"Rebuilding embeddings for {len(articles)} articles...")

        # 删除旧 embedding
        db.query(ArticleEmbedding).delete()
        db.commit()

        # 批量计算新 embedding
        batch_size = 20  # DashScope API 限制
        for i in range(0, len(articles), batch_size):
            batch = articles[i:i + batch_size]
            texts = [a.summary or a.title for a in batch]
            embeddings = get_embeddings(texts)

            for article, embedding in zip(batch, embeddings):
                db_embedding = ArticleEmbedding(
                    article_id=article.id,
                    embedding=embedding.tolist(),
                    model_name=settings.embedding_model
                )
                db.add(db_embedding)

            db.commit()
            print(f"  Processed {min(i + batch_size, len(articles))}/{len(articles)} articles")

        print(f"Article embeddings rebuilt: {len(articles)}")

        # Step 2: 重建用户兴趣向量
        users = db.query(User).all()
        print(f"Rebuilding user interests for {len(users)} users...")

        # 删除旧兴趣向量
        db.query(UserInterest).delete()
        db.commit()

        from app.models.recommendation import UserRecommendation
        from app.services.embedding_service import compute_time_decay_weights
        import numpy as np

        rebuilt_users = 0
        for user in users:
            # 获取用户喜欢的论文
            liked_records = db.query(
                UserRecommendation.article_id,
                UserRecommendation.liked_at
            ).filter(
                UserRecommendation.user_id == user.id,
                UserRecommendation.is_liked == True
            ).order_by(UserRecommendation.liked_at.desc()).all()

            if not liked_records:
                continue

            # 获取这些论文的 embedding
            article_ids = [r.article_id for r in liked_records]
            embeddings = db.query(ArticleEmbedding).filter(
                ArticleEmbedding.article_id.in_(article_ids)
            ).all()
            embedding_map = {e.article_id: np.array(e.embedding) for e in embeddings}

            # 构造 embedding 矩阵
            valid_embeddings = []
            for record in liked_records:
                if record.article_id in embedding_map:
                    valid_embeddings.append(embedding_map[record.article_id])

            if not valid_embeddings:
                continue

            # 计算加权平均
            embeddings_matrix = np.array(valid_embeddings)
            weights = compute_time_decay_weights(len(valid_embeddings))
            user_interest = np.average(embeddings_matrix, axis=0, weights=weights)

            # 保存
            interest = UserInterest(
                user_id=user.id,
                embedding=user_interest.tolist(),
                like_count=len(valid_embeddings)
            )
            db.add(interest)
            rebuilt_users += 1

        db.commit()
        print(f"User interests rebuilt: {rebuilt_users}")
        print("Embedding rebuild completed!")

    except Exception as e:
        print(f"Embedding rebuild failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


# ============================================
# 开发环境初始化
# ============================================

@app.post("/init-db")
async def initialize_database():
    """
    初始化数据库（仅开发环境使用）
    生产环境应使用 Alembic 迁移
    """
    try:
        init_db()
        return {"status": "success", "message": "Database initialized"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================
# 启动入口
# ============================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,  # 开发环境启用热重载
    )
