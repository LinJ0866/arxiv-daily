"""
API 路由包
"""

from app.api.auth import router as auth_router
from app.api.articles import router as articles_router
from app.api.likes import router as likes_router
from app.api.recommendations import router as recommendations_router
from app.api.preferences import router as preferences_router

__all__ = [
    "auth_router",
    "articles_router",
    "likes_router",
    "recommendations_router",
    "preferences_router",
]
