"""
文章相关数据库模型
"""

from sqlalchemy import Column, String, Text, DateTime, Date, JSON, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class Article(Base):
    """文章主表"""
    __tablename__ = "articles"

    id = Column(String(20), primary_key=True, comment="arXiv ID, e.g. 2401.12345")
    title = Column(Text, nullable=False, comment="论文标题")
    authors = Column(JSON, default=[], comment="作者列表")
    categories = Column(JSON, default=[], comment="分类列表")
    summary = Column(Text, comment="原始摘要")
    pdf_url = Column(Text, comment="PDF 链接")
    abs_url = Column(Text, comment="摘要页面链接")
    comment = Column(Text, comment="arXiv 评论")
    crawled_at = Column(Date, nullable=False, comment="爬取日期")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    embedding = relationship("ArticleEmbedding", back_populates="article", uselist=False, cascade="all, delete-orphan")
    ai_data = relationship("ArticleAI", back_populates="article", uselist=False, cascade="all, delete-orphan")
    recommendations = relationship("UserRecommendation", back_populates="article", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Article(id='{self.id}', title='{self.title[:50]}...')>"


class ArticleEmbedding(Base):
    """文章 Embedding 向量"""
    __tablename__ = "article_embeddings"

    article_id = Column(String(20), ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True)
    embedding = Column(JSON, nullable=False, comment="Embedding 向量（JSON 数组）")
    model_name = Column(String(100), comment="使用的 Embedding 模型名称")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    article = relationship("Article", back_populates="embedding")

    def __repr__(self):
        return f"<ArticleEmbedding(article_id='{self.article_id}', model='{self.model_name}')>"


class ArticleAI(Base):
    """文章 AI 增强数据"""
    __tablename__ = "article_ai"

    article_id = Column(String(20), ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True)
    language = Column(String(10), default="en", comment="AI 输出语言")
    tldr = Column(Text, comment="TL;DR 摘要")
    motivation = Column(Text, comment="研究动机")
    method = Column(Text, comment="研究方法")
    result = Column(Text, comment="研究结果")
    conclusion = Column(Text, comment="研究结论")
    code_url = Column(Text, comment="代码仓库链接")
    code_stars = Column(Integer, comment="代码仓库 star 数")
    code_last_update = Column(Date, comment="代码仓库最后更新日期")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    article = relationship("Article", back_populates="ai_data")

    def __repr__(self):
        return f"<ArticleAI(article_id='{self.article_id}', language='{self.language}')>"
