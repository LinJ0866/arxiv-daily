"""
用户相关 Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============================================
# 认证相关
# ============================================

class UserCreate(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    is_admin: bool = False
    weight_vector: float
    weight_keyword: float
    author_bonus: float
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT Token 响应"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token 解析数据"""
    user_id: Optional[int] = None


# ============================================
# 偏好设置相关
# ============================================

class PreferenceUpdate(BaseModel):
    """更新偏好设置请求"""
    keywords: List[str] = Field(default=[], description="偏好关键词列表")
    authors: List[str] = Field(default=[], description="偏好作者列表")


class PreferenceResponse(BaseModel):
    """偏好设置响应"""
    keywords: List[str]
    authors: List[str]


class WeightUpdate(BaseModel):
    """更新推荐权重请求"""
    weight_vector: Optional[float] = Field(None, ge=0, le=1, description="向量相似度权重")
    weight_keyword: Optional[float] = Field(None, ge=0, le=1, description="关键词匹配权重")
    author_bonus: Optional[float] = Field(None, ge=0, le=2, description="作者匹配加分")


class WeightResponse(BaseModel):
    """推荐权重响应"""
    weight_vector: float
    weight_keyword: float
    author_bonus: float
