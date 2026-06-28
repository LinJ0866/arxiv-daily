"""
喜欢 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.database import get_db
from app.models.user import User
from app.models.article import Article, ArticleAI
from app.models.recommendation import UserRecommendation
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/likes", tags=["喜欢"])


@router.post("/{article_id}")
def like_article(
    article_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    喜欢文章

    - **article_id**: arXiv ID
    - 如果文章已有推荐记录，更新 is_liked 状态
    - 如果文章没有推荐记录，创建新的手动喜欢记录
    """
    # 检查文章是否存在
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # 检查是否已有推荐记录
    existing = db.query(UserRecommendation).filter(
        UserRecommendation.user_id == current_user.id,
        UserRecommendation.article_id == article_id
    ).first()

    if existing:
        # 更新现有记录
        existing.is_liked = True
        existing.liked_at = datetime.utcnow()
    else:
        # 创建新记录（手动喜欢非推荐文章）
        recommendation = UserRecommendation(
            user_id=current_user.id,
            article_id=article_id,
            recommended_at=date.today(),
            source='manual',
            is_liked=True,
            liked_at=datetime.utcnow()
        )
        db.add(recommendation)

    db.commit()

    return {"status": "success", "article_id": article_id}


@router.delete("/{article_id}")
def unlike_article(
    article_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    取消喜欢文章

    - **article_id**: arXiv ID
    """
    recommendation = db.query(UserRecommendation).filter(
        UserRecommendation.user_id == current_user.id,
        UserRecommendation.article_id == article_id,
        UserRecommendation.is_liked == True
    ).first()

    if not recommendation:
        raise HTTPException(status_code=404, detail="Like not found")

    recommendation.is_liked = False
    recommendation.liked_at = None
    db.commit()

    return {"status": "success", "article_id": article_id}


@router.get("")
def list_likes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户喜欢列表（包含文章详细信息）

    按喜欢时间倒序排列
    """
    # JOIN 文章表获取详细信息
    likes = db.query(
        UserRecommendation,
        Article,
        ArticleAI
    ).join(
        Article, UserRecommendation.article_id == Article.id
    ).outerjoin(
        ArticleAI, Article.id == ArticleAI.article_id
    ).filter(
        UserRecommendation.user_id == current_user.id,
        UserRecommendation.is_liked == True
    ).order_by(UserRecommendation.liked_at.desc()).all()

    return {
        "likes": [
            {
                "id": article.id,
                "article_id": article.id,
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
                "is_liked": True,
                "liked_at": like.liked_at.isoformat() if like.liked_at else None,
                "source": like.source,
            }
            for like, article, ai in likes
        ]
    }
