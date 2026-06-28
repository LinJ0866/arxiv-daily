"""
Pydantic Schemas 包
"""

from app.schemas.user import (
    UserCreate,
    UserResponse,
    Token,
    TokenData,
    PreferenceUpdate,
    PreferenceResponse,
    WeightUpdate,
    WeightResponse,
)
from app.schemas.article import (
    AIData,
    ArticleBase,
    ArticleResponse,
    ArticleListItem,
    ArticleListResponse,
)
from app.schemas.recommendation import (
    RecommendationItem,
    RecommendationListResponse,
    RecomputeResponse,
    LikeItem,
    LikeListResponse,
    LikeResponse,
)

__all__ = [
    # User
    "UserCreate",
    "UserResponse",
    "Token",
    "TokenData",
    "PreferenceUpdate",
    "PreferenceResponse",
    "WeightUpdate",
    "WeightResponse",
    # Article
    "AIData",
    "ArticleBase",
    "ArticleResponse",
    "ArticleListItem",
    "ArticleListResponse",
    # Recommendation
    "RecommendationItem",
    "RecommendationListResponse",
    "RecomputeResponse",
    "LikeItem",
    "LikeListResponse",
    "LikeResponse",
]
