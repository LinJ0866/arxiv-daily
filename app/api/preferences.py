"""
偏好设置 API
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserPreference
from app.api.auth import get_current_user
from app.schemas.user import PreferenceUpdate, PreferenceResponse, WeightUpdate, WeightResponse

router = APIRouter(prefix="/api/preferences", tags=["偏好设置"])


@router.get("", response_model=PreferenceResponse)
def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户偏好设置

    返回用户配置的偏好关键词和作者列表
    """
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        # 如果没有偏好记录，创建空记录
        pref = UserPreference(user_id=current_user.id, keywords=[], authors=[])
        db.add(pref)
        db.commit()
        db.refresh(pref)

    return {
        "keywords": pref.keywords or [],
        "authors": pref.authors or [],
    }


@router.put("", response_model=PreferenceResponse)
def update_preferences(
    data: PreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户偏好设置

    - **keywords**: 偏好关键词列表
    - **authors**: 偏好作者列表
    """
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        pref = UserPreference(user_id=current_user.id)
        db.add(pref)

    pref.keywords = data.keywords
    pref.authors = data.authors
    db.commit()
    db.refresh(pref)

    return {
        "keywords": pref.keywords,
        "authors": pref.authors,
    }


@router.get("/weights", response_model=WeightResponse)
def get_weights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户推荐权重配置

    返回向量相似度权重、关键词匹配权重、作者匹配加分
    """
    return {
        "weight_vector": current_user.weight_vector,
        "weight_keyword": current_user.weight_keyword,
        "author_bonus": current_user.author_bonus,
    }


@router.put("/weights", response_model=WeightResponse)
def update_weights(
    data: WeightUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户推荐权重配置

    - **weight_vector**: 向量相似度权重（0-1）
    - **weight_keyword**: 关键词匹配权重（0-1）
    - **author_bonus**: 作者匹配加分（0-2）
    """
    if data.weight_vector is not None:
        current_user.weight_vector = data.weight_vector
    if data.weight_keyword is not None:
        current_user.weight_keyword = data.weight_keyword
    if data.author_bonus is not None:
        current_user.author_bonus = data.author_bonus

    db.commit()
    db.refresh(current_user)

    return {
        "weight_vector": current_user.weight_vector,
        "weight_keyword": current_user.weight_keyword,
        "author_bonus": current_user.author_bonus,
    }
