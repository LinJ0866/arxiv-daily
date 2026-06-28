"""
Pipeline 运行日志模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Date, Text
from app.database import Base
from datetime import datetime


class PipelineLog(Base):
    """Pipeline 运行日志"""
    __tablename__ = "pipeline_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_date = Column(Date, nullable=False, comment="运行日期")
    started_at = Column(DateTime, nullable=False, comment="开始时间")
    finished_at = Column(DateTime, comment="结束时间")
    status = Column(String(20), nullable=False, comment="状态: running/success/failed")

    # 统计数据
    crawled_count = Column(Integer, default=0, comment="爬取文章数")
    saved_count = Column(Integer, default=0, comment="新增文章数")
    embedded_count = Column(Integer, default=0, comment="计算 Embedding 数")
    recommended_count = Column(Integer, default=0, comment="生成推荐数")

    # 错误信息
    error_message = Column(Text, comment="错误信息")

    def __repr__(self):
        return f"<PipelineLog(id={self.id}, date={self.run_date}, status={self.status})>"
