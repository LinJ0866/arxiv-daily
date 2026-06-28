"""
Embedding 服务 - 计算文本向量和相似度
"""

import numpy as np
from openai import OpenAI
from typing import List

from app.config import settings

# 创建 OpenAI 客户端
client = OpenAI(
    api_key=settings.embedding_api_key,
    base_url=settings.embedding_api_base
)


def get_embeddings(texts: List[str], batch_size: int = 20) -> np.ndarray:
    """
    批量获取文本的 embedding 向量

    使用 OpenAI 兼容 API，支持任何兼容接口的提供商

    Args:
        texts: 文本列表
        batch_size: 批处理大小（默认 64）

    Returns:
        numpy 数组，形状为 (len(texts), embedding_dim)
    """
    if not texts:
        return np.array([])

    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.embeddings.create(
            input=batch,
            model=settings.embedding_model
        )
        all_embeddings.extend([r.embedding for r in response.data])

    return np.array(all_embeddings)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    计算余弦相似度（L2 归一化后点积）

    Args:
        a: 向量矩阵 a，形状为 (n, d)
        b: 向量矩阵 b，形状为 (m, d)

    Returns:
        相似度矩阵，形状为 (n, m)
    """
    # L2 归一化
    a_normalized = a / np.linalg.norm(a, axis=1, keepdims=True)
    b_normalized = b / np.linalg.norm(b, axis=1, keepdims=True)

    # 点积计算余弦相似度
    return np.dot(a_normalized, b_normalized.T)


def compute_time_decay_weights(n: int) -> np.ndarray:
    """
    计算时间衰减权重（参考 zotero-arxiv-daily）

    使用对数衰减函数: w[i] = 1 / (1 + log10(i + 1))
    然后归一化使得权重之和为 1

    Args:
        n: 权重数量

    Returns:
        归一化后的权重数组
    """
    if n == 0:
        return np.array([])

    weights = 1 / (1 + np.log10(np.arange(n) + 1))
    return weights / weights.sum()
