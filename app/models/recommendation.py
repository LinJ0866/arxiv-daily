"""
推荐相关数据库模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class UserRecommendation(Base):
    """
    用户推荐记录表

    统一存储系统推荐和用户手动喜欢的记录
    - source='system': 系统每日推荐
    - source='manual': 用户手动喜欢（可能来自推荐列表，也可能是浏览所有文章时喜欢）
    """
    __tablename__ = "user_recommendations"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, comment="用户 ID")
    article_id = Column(String(20), ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True, comment="文章 ID")
    recommended_at = Column(Date, primary_key=True, comment="推荐/喜欢日期")

    # 来源
    source = Column(String(20), nullable=False, comment="来源: system | manual")

    # 系统推荐得分（source='manual' 时为 NULL）
    vector_score = Column(Float, comment="向量相似度得分")
    keyword_score = Column(Float, comment="关键词匹配得分")
    author_matched = Column(Boolean, comment="作者是否匹配")
    final_score = Column(Float, comment="综合得分")

    # 用户交互状态
    is_liked = Column(Boolean, default=False, comment="是否喜欢")
    liked_at = Column(DateTime, comment="喜欢时间")

    # 关系
    user = relationship("User", back_populates="recommendations")
    article = relationship("Article", back_populates="recommendations")

    def __repr__(self):
        return (
            f"<UserRecommendation(user_id={self.user_id}, article_id='{self.article_id}', "
            f"source='{self.source}', is_liked={self.is_liked})>"
        )
