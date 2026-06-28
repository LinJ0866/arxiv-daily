"""
推荐相关 Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class RecommendationItem(BaseModel):
    """推荐项"""
    article_id: str
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    summary: Optional[str] = None
    categories: Optional[List[str]] = None
    ai: Optional[dict] = None
    source: str
    final_score: Optional[float] = None
    is_liked: bool = False


class RecommendationListResponse(BaseModel):
    """推荐列表响应"""
    recommendations: List[RecommendationItem]
    date: date
    total: int


class RecomputeResponse(BaseModel):
    """重新计算推荐响应"""
    status: str
    new_recommendations: int


class LikeItem(BaseModel):
    """喜欢项"""
    article_id: str
    liked_at: Optional[datetime] = None
    source: str


class LikeListResponse(BaseModel):
    """喜欢列表响应"""
    likes: List[LikeItem]


class LikeResponse(BaseModel):
    """喜欢/取消喜欢响应"""
    status: str
    article_id: str
