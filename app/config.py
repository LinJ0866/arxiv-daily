"""
配置管理 - 从环境变量或 .env 文件加载配置
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # 数据库
    database_url: str = "postgresql://user:password@localhost:5432/arxiv_daily"

    # 应用
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    secret_key: str = "your-secret-key-change-this"
    access_token_expire_days: int = 7

    # LLM（可选，不配置则跳过 AI 增强）
    llm_api_key: Optional[str] = None
    llm_api_base: str = "https://api.openai.com/v1"
    llm_model: str = "deepseek-chat"
    language: str = "Chinese"

    # Embedding（必填，用于推荐算法）
    embedding_api_key: str = ""
    embedding_api_base: str = "https://api.openai.com/v1"
    embedding_model: str = "text-embedding-3-small"

    # 爬虫配置
    arxiv_categories: str = "cs.CV,cs.CL,cs.AI"

    # GitHub API（可选，用于获取代码仓库信息）
    github_token: Optional[str] = None

    @property
    def categories_list(self) -> list[str]:
        """将逗号分隔的分类字符串转换为列表"""
        return [c.strip() for c in self.arxiv_categories.split(",") if c.strip()]

    @property
    def llm_enabled(self) -> bool:
        """检查 LLM 是否已配置"""
        return self.llm_api_key is not None and len(self.llm_api_key) > 0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
settings = Settings()
