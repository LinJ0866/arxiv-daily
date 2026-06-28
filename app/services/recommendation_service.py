"""
推荐服务 - 计算用户推荐
"""

import numpy as np
from datetime import date, datetime
from sqlalchemy.orm import Session

from app.models.user import User, UserPreference, UserInterest
from app.models.article import Article, ArticleEmbedding
from app.models.recommendation import UserRecommendation
from app.services.embedding_service import get_embeddings, cosine_similarity, compute_time_decay_weights


def compute_user_interest(user_id: int, db: Session) -> np.ndarray | None:
    """
    基于用户喜欢列表计算兴趣向量

    使用时间衰减加权平均：
    - 最近喜欢的论文权重更高
    - 使用对数衰减函数: w[i] = 1 / (1 + log10(i + 1))
    """
    # 获取用户所有喜欢的论文（按喜欢时间倒序）
    liked_records = db.query(
        UserRecommendation.article_id,
        UserRecommendation.liked_at
    ).filter(
        UserRecommendation.user_id == user_id,
        UserRecommendation.is_liked == True
    ).order_by(UserRecommendation.liked_at.desc()).all()

    if not liked_records:
        return None

    # 获取这些论文的 embedding
    article_ids = [r.article_id for r in liked_records]
    embeddings = db.query(ArticleEmbedding).filter(
        ArticleEmbedding.article_id.in_(article_ids)
    ).all()

    embedding_map = {e.article_id: np.array(e.embedding) for e in embeddings}

    # 构造 embedding 矩阵（按喜欢时间排序）
    valid_embeddings = []
    for record in liked_records:
        if record.article_id in embedding_map:
            valid_embeddings.append(embedding_map[record.article_id])

    if not valid_embeddings:
        return None

    embeddings_matrix = np.array(valid_embeddings)

    # 计算时间衰减权重
    weights = compute_time_decay_weights(len(valid_embeddings))

    # 加权平均
    user_interest = np.average(embeddings_matrix, axis=0, weights=weights)

    # 保存到数据库
    interest = db.query(UserInterest).filter(UserInterest.user_id == user_id).first()
    if interest:
        interest.embedding = user_interest.tolist()
        interest.like_count = len(valid_embeddings)
        interest.updated_at = datetime.utcnow()
    else:
        interest = UserInterest(
            user_id=user_id,
            embedding=user_interest.tolist(),
            like_count=len(valid_embeddings)
        )
        db.add(interest)

    db.commit()
    return user_interest


def compute_user_recommendations(user_id: int, db: Session) -> int:
    """
    为用户计算今日推荐

    算法：
    1. 获取用户兴趣向量（基于喜欢列表 + 时间衰减）
    2. 获取今日新文章
    3. 排除已有推荐/喜欢记录的文章
    4. 计算综合得分 = 向量相似度 * w_vector + 关键词匹配 * w_keyword + 作者匹配 * bonus
    5. 增量写入推荐记录

    返回：新增推荐数量
    """
    # 获取用户兴趣向量
    interest = db.query(UserInterest).filter(UserInterest.user_id == user_id).first()
    if interest:
        user_interest = np.array(interest.embedding)
    else:
        # 尝试计算兴趣向量
        user_interest = compute_user_interest(user_id, db)
        if user_interest is None:
            return 0  # 没有喜欢记录，无法推荐

    # 获取用户偏好
    pref = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    keywords = pref.keywords if pref else []
    authors = pref.authors if pref else []

    # 获取用户权重配置
    user = db.query(User).filter(User.id == user_id).first()

    # 获取今日新文章
    today = date.today()
    today_articles = db.query(Article).filter(Article.crawled_at == today).all()

    if not today_articles:
        return 0

    # 获取已有推荐/喜欢记录
    existing_article_ids = set(
        r[0] for r in db.query(UserRecommendation.article_id).filter(
            UserRecommendation.user_id == user_id
        ).all()
    )

    # 筛选新文章
    new_articles = [a for a in today_articles if a.id not in existing_article_ids]

    if not new_articles:
        return 0

    # 获取新文章的 embedding
    article_embeddings = db.query(ArticleEmbedding).filter(
        ArticleEmbedding.article_id.in_([a.id for a in new_articles])
    ).all()
    embedding_map = {e.article_id: np.array(e.embedding) for e in article_embeddings}

    # 计算推荐
    new_recommendations = []
    for article in new_articles:
        if article.id not in embedding_map:
            continue

        # 向量相似度
        article_emb = embedding_map[article.id]
        vector_score = float(cosine_similarity(
            user_interest.reshape(1, -1),
            article_emb.reshape(1, -1)
        )[0][0])

        # 关键词匹配
        keyword_score = 0
        if keywords:
            text = ((article.title or "") + " " + (article.summary or "")).lower()
            keyword_score = sum(1 for kw in keywords if kw.lower() in text)

        # 作者匹配
        author_matched = False
        if authors and article.authors:
            article_authors_lower = [a.lower() for a in article.authors]
            author_matched = any(
                author.lower() in article_authors_lower
                for author in authors
            )

        # 综合得分
        final_score = (
            user.weight_vector * vector_score +
            user.weight_keyword * keyword_score +
            (user.author_bonus if author_matched else 0)
        )

        new_recommendations.append(UserRecommendation(
            user_id=user_id,
            article_id=article.id,
            recommended_at=today,
            source='system',
            vector_score=vector_score,
            keyword_score=keyword_score,
            author_matched=author_matched,
            final_score=final_score,
            is_liked=False
        ))

    # 批量插入
    if new_recommendations:
        db.bulk_save_objects(new_recommendations)
        db.commit()

    return len(new_recommendations)


def compute_all_users_recommendations(db: Session) -> int:
    """
    为所有活跃用户计算推荐（每日定时任务调用）

    只为有喜欢记录的用户计算推荐

    返回：总新增推荐数量
    """
    # 只查询有喜欢记录的用户
    users_with_likes = db.query(User).join(
        UserRecommendation, User.id == UserRecommendation.user_id
    ).filter(
        UserRecommendation.is_liked == True
    ).distinct().all()

    if not users_with_likes:
        print("  No users with likes, skipping recommendations")
        return 0

    total_new = 0
    for user in users_with_likes:
        new_count = compute_user_recommendations(user.id, db)
        total_new += new_count
        print(f"  User {user.username}: {new_count} new recommendations")

    return total_new
