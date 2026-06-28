"""
文章相关 Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class AIData(BaseModel):
    """AI 增强数据"""
    tldr: Optional[str] = None
    motivation: Optional[str] = None
    method: Optional[str] = None
    result: Optional[str] = None
    conclusion: Optional[str] = None
    code_url: Optional[str] = None
    code_stars: Optional[int] = None


class ArticleBase(BaseModel):
    """文章基础信息"""
    id: str
    title: str
    authors: List[str] = []
    categories: List[str] = []


class ArticleResponse(ArticleBase):
    """文章详情响应"""
    summary: Optional[str] = None
    pdf_url: Optional[str] = None
    abs_url: Optional[str] = None
    comment: Optional[str] = None
    crawled_at: date
    ai: Optional[AIData] = None
    is_liked: bool = False

    class Config:
        from_attributes = True


class ArticleListItem(ArticleBase):
    """文章列表项"""
    summary: Optional[str] = None
    crawled_at: date
    ai: Optional[AIData] = None
    is_liked: bool = False


class ArticleListResponse(BaseModel):
    """文章列表响应"""
    articles: List[ArticleListItem]
    total: int
    page: int
    page_size: int
