"""
推荐 API
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.database import get_db
from app.models.user import User
from app.models.article import Article, ArticleAI
from app.models.recommendation import UserRecommendation
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/recommendations", tags=["推荐"])


@router.get("")
def get_recommendations(
    target_date: Optional[date] = Query(None, description="目标日期，默认今天"),
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户推荐列表

    - **target_date**: 目标日期（默认今天）
    - **limit**: 返回数量（默认 50）
    - 按综合得分降序排列
    """
    if target_date is None:
        target_date = date.today()

    # 使用 JOIN 查询获取推荐记录和文章信息
    results = db.query(
        UserRecommendation,
        Article,
        ArticleAI
    ).join(
        Article, UserRecommendation.article_id == Article.id
    ).outerjoin(
        ArticleAI, Article.id == ArticleAI.article_id
    ).filter(
        UserRecommendation.user_id == current_user.id,
        UserRecommendation.recommended_at == target_date
    ).order_by(
        UserRecommendation.final_score.desc().nullslast()
    ).limit(limit).all()

    # 获取总数
    total = db.query(UserRecommendation).filter(
        UserRecommendation.user_id == current_user.id,
        UserRecommendation.recommended_at == target_date
    ).count()

    return {
        "recommendations": [
            {
                "article_id": reco.article_id,
                "id": article.id,
                "title": article.title,
                "authors": article.authors or [],
                "categories": article.categories or [],
                "summary": article.summary,
                "abs_url": article.abs_url,
                "pdf_url": article.pdf_url,
                "crawled_at": article.crawled_at.isoformat() if article.crawled_at else None,
                "ai": {
                    "tldr": ai.tldr if ai else None,
                } if ai else None,
                "source": reco.source,
                "final_score": reco.final_score,
                "is_liked": reco.is_liked,
            }
            for reco, article, ai in results
        ],
        "date": target_date,
        "total": total,
    }


@router.post("/recompute")
def recompute_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    手动触发重新计算今日推荐

    - 重新计算用户兴趣向量
    - 计算今日新文章的推荐得分
    - 增量写入推荐记录（保留旧记录）
    """
    from app.services.recommendation_service import compute_user_recommendations

    new_count = compute_user_recommendations(current_user.id, db)

    return {
        "status": "success",
        "new_recommendations": new_count,
    }
