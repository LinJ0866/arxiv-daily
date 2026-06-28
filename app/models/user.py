"""
用户相关数据库模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="用户 ID")
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    is_admin = Column(Boolean, default=False, comment="是否为管理员")

    # 推荐权重配置
    weight_vector = Column(Float, default=0.7, comment="向量相似度权重")
    weight_keyword = Column(Float, default=0.3, comment="关键词匹配权重")
    author_bonus = Column(Float, default=0.5, comment="作者匹配加分")

    created_at = Column(DateTime, default=datetime.utcnow, comment="注册时间")

    # 关系
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    interest = relationship("UserInterest", back_populates="user", uselist=False, cascade="all, delete-orphan")
    recommendations = relationship("UserRecommendation", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class UserPreference(Base):
    """用户偏好设置"""
    __tablename__ = "user_preferences"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, comment="用户 ID")
    keywords = Column(JSON, default=[], comment="偏好关键词列表")
    authors = Column(JSON, default=[], comment="偏好作者列表")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    user = relationship("User", back_populates="preferences")

    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id}, keywords={self.keywords})>"


class UserInterest(Base):
    """用户兴趣向量（预计算）"""
    __tablename__ = "user_interests"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, comment="用户 ID")
    embedding = Column(JSON, nullable=False, comment="用户兴趣向量（JSON 数组）")
    like_count = Column(Integer, default=0, comment="计算时基于的喜欢论文数量")
    updated_at = Column(DateTime, default=datetime.utcnow, comment="更新时间")

    # 关系
    user = relationship("User", back_populates="interest")

    def __repr__(self):
        return f"<UserInterest(user_id={self.user_id}, like_count={self.like_count})>"
