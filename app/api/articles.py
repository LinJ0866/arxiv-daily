"""
文章 API
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, String
from typing import Optional
from datetime import date

from app.database import get_db
from app.models.article import Article, ArticleAI
from app.models.user import User
from app.models.recommendation import UserRecommendation
from app.api.auth import get_current_user, get_optional_user
from app.schemas.article import ArticleResponse, ArticleListResponse, AIData

router = APIRouter(prefix="/api/articles", tags=["文章"])


@router.get("/dates")
def get_available_dates(
    db: Session = Depends(get_db)
):
    """
    获取所有可用的日期列表

    按日期倒序排列，用于前端日期选择器
    """
    dates = db.query(
        Article.crawled_at,
        func.count(Article.id).label('count')
    ).group_by(
        Article.crawled_at
    ).order_by(
        Article.crawled_at.desc()
    ).all()

    return {
        "dates": [
            {"date": d.isoformat(), "count": c}
            for d, c in dates
        ]
    }


@router.get("", response_model=ArticleListResponse)
def list_articles(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="分类过滤"),
    date_from: Optional[date] = Query(None, description="开始日期"),
    date_to: Optional[date] = Query(None, description="结束日期"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    获取文章列表

    - 支持分页、分类过滤、日期范围过滤、关键词搜索
    - 登录用户返回喜欢状态
    """
    query = db.query(Article)

    # 分类过滤（PostgreSQL JSON 数组包含查询）
    if category:
        # 将 JSON 数组转为文本，然后检查是否包含指定分类
        query = query.filter(
            func.cast(Article.categories, String).like(f'%"{category}"%')
        )

    # 日期范围过滤
    if date_from:
        query = query.filter(Article.crawled_at >= date_from)
    if date_to:
        query = query.filter(Article.crawled_at <= date_to)

    # 关键词搜索
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Article.title.ilike(search_term)) |
            (Article.summary.ilike(search_term))
        )

    # 统计总数
    total = query.count()

    # 分页查询
    articles = query.order_by(Article.crawled_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 获取用户的喜欢状态
    liked_article_ids = set()
    if current_user:
        liked = db.query(UserRecommendation.article_id).filter(
            UserRecommendation.user_id == current_user.id,
            UserRecommendation.is_liked == True
        ).all()
        liked_article_ids = {r[0] for r in liked}

    # 构造响应
    article_list = []
    for article in articles:
        ai_data = db.query(ArticleAI).filter(ArticleAI.article_id == article.id).first()

        article_list.append({
            "id": article.id,
            "title": article.title,
            "authors": article.authors or [],
            "categories": article.categories or [],
            "summary": article.summary,
            "abs_url": article.abs_url,
            "pdf_url": article.pdf_url,
            "crawled_at": article.crawled_at.isoformat() if article.crawled_at else None,
            "ai": {
                "tldr": ai_data.tldr,
                "motivation": ai_data.motivation,
                "method": ai_data.method,
                "result": ai_data.result,
                "conclusion": ai_data.conclusion,
            } if ai_data else None,
            "is_liked": article.id in liked_article_ids,
        })

    return {
        "articles": article_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(
    article_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    获取文章详情

    - **article_id**: arXiv ID（如 2401.12345）
    - 登录用户返回喜欢状态
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    ai_data = db.query(ArticleAI).filter(ArticleAI.article_id == article_id).first()

    # 获取喜欢状态
    is_liked = False
    if current_user:
        like = db.query(UserRecommendation).filter(
            UserRecommendation.user_id == current_user.id,
            UserRecommendation.article_id == article_id,
            UserRecommendation.is_liked == True
        ).first()
        is_liked = like is not None

    return {
        "id": article.id,
        "title": article.title,
        "authors": article.authors or [],
        "categories": article.categories or [],
        "summary": article.summary,
        "pdf_url": article.pdf_url,
        "abs_url": article.abs_url,
        "comment": article.comment,
        "crawled_at": article.crawled_at,
        "ai": {
            "tldr": ai_data.tldr,
            "motivation": ai_data.motivation,
            "method": ai_data.method,
            "result": ai_data.result,
            "conclusion": ai_data.conclusion,
            "code_url": ai_data.code_url,
            "code_stars": ai_data.code_stars,
        } if ai_data else None,
        "is_liked": is_liked,
    }
