"""
Zotero 导入 API
"""

import os
import tempfile
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.article import Article, ArticleEmbedding
from app.api.auth import get_current_user
from app.services.embedding_service import get_embeddings
from app.services.zotero_parser import parse_zotero_rdf, import_articles, mark_as_liked, fetch_arxiv_metadata

router = APIRouter(prefix="/api/zotero", tags=["Zotero"])


@router.post("/import")
async def import_zotero_rdf_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    从 Zotero RDF 文件导入文献

    - 解析 RDF 文件
    - 通过 arXiv API 补齐 categories
    - 导入文章到数据库
    - 自动标记为喜欢
    - 计算 embedding
    """
    # 检查文件类型
    if not file.filename.endswith('.rdf'):
        raise HTTPException(status_code=400, detail="Only .rdf files are supported")

    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.rdf') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # 解析 RDF
        articles = parse_zotero_rdf(tmp_path)
        if not articles:
            raise HTTPException(status_code=400, detail="No articles found in RDF file")

        # 通过 arXiv API 补齐 categories
        arxiv_ids = [a['id'] for a in articles]
        metadata = fetch_arxiv_metadata(arxiv_ids)
        for article in articles:
            if article['id'] in metadata:
                article['categories'] = metadata[article['id']].get('categories', [])
                article['comment'] = metadata[article['id']].get('comment', '')

        # 导入文章
        new_count, existing_count = import_articles(articles, db)

        # 标记为喜欢
        article_ids = [a['id'] for a in articles]
        liked_count = mark_as_liked(article_ids, current_user.id, db)

        # 计算 embedding
        emb_count = compute_embeddings(article_ids, db)

        return {
            "status": "success",
            "total": len(articles),
            "new_articles": new_count,
            "existing_articles": existing_count,
            "liked": liked_count,
            "embeddings_computed": emb_count,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 清理临时文件
        os.unlink(tmp_path)


def compute_embeddings(article_ids: list[str], db: Session) -> int:
    """计算 embedding"""
    import os

    # 获取没有 embedding 的文章
    articles = db.query(Article).filter(
        Article.id.in_(article_ids),
        ~Article.id.in_(db.query(ArticleEmbedding.article_id))
    ).all()

    if not articles:
        return 0

    # 批量计算 embedding
    texts = [a.summary or a.title for a in articles]
    embeddings = get_embeddings(texts)

    # 保存到数据库
    embedding_model = os.getenv('EMBEDDING_MODEL', 'unknown')
    for article, embedding in zip(articles, embeddings):
        db_embedding = ArticleEmbedding(
            article_id=article.id,
            embedding=embedding,
            model_name=embedding_model
        )
        db.add(db_embedding)

    db.commit()
    return len(articles)
