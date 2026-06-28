"""
数据库连接配置
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # 连接前检查是否有效
    pool_size=10,         # 连接池大小
    max_overflow=20,      # 最大溢出连接数
    echo=False            # 是否打印 SQL（调试时设为 True）
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建模型基类
Base = declarative_base()


def get_db():
    """
    获取数据库会话（用于 FastAPI 依赖注入）
    使用 yield 确保会话在请求结束后正确关闭
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库（创建所有表）
    仅用于开发环境，生产环境应使用 Alembic 迁移
    """
    from app.models import article, user, recommendation  # noqa: F401
    Base.metadata.create_all(bind=engine)
