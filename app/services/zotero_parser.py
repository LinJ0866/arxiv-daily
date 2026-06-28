"""
Zotero RDF 解析服务
"""

import re
from datetime import datetime, date
from xml.etree import ElementTree as ET


def parse_zotero_rdf(file_path: str) -> list[dict]:
    """
    解析 Zotero RDF 文件

    返回文章列表（仅基础信息，categories 通过 arXiv API 补齐）
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    # 定义命名空间
    namespaces = {
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'z': 'http://www.zotero.org/namespaces/export#',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'foaf': 'http://xmlns.com/foaf/0.1/',
        'bib': 'http://purl.org/net/biblio#',
        'dcterms': 'http://purl.org/dc/terms/',
        'prism': 'http://prismstandard.org/namespaces/1.2/basic/',
    }

    articles = []

    # 查找所有论文条目
    for desc in root.findall('.//rdf:Description', namespaces):
        # 检查是否是论文类型
        item_type = desc.find('z:itemType', namespaces)
        if item_type is None or item_type.text not in ['preprint', 'conferencePaper', 'journalArticle']:
            continue

        # 提取 arXiv ID
        arxiv_id = None
        for identifier in desc.findall('.//dc:identifier', namespaces):
            uri = identifier.find('.//rdf:value', namespaces)
            if uri is not None and uri.text:
                match = re.search(r'arxiv\.org/abs/(\d+\.\d+)', uri.text)
                if match:
                    arxiv_id = match.group(1)
                    break

        if not arxiv_id:
            # 尝试从 DOI 提取
            for identifier in desc.findall('.//dc:identifier', namespaces):
                if identifier.text:
                    match = re.search(r'arXiv\.(\d+\.\d+)', identifier.text)
                    if match:
                        arxiv_id = match.group(1)
                        break

        if not arxiv_id:
            continue

        # 提取标题
        title_elem = desc.find('dc:title', namespaces)
        title = title_elem.text if title_elem is not None else ''

        # 提取摘要
        abstract_elem = desc.find('dcterms:abstract', namespaces)
        abstract = abstract_elem.text if abstract_elem is not None else ''

        # 提取作者
        authors = []
        for person in desc.findall('.//foaf:Person', namespaces):
            surname = person.find('foaf:surname', namespaces)
            given_name = person.find('foaf:givenName', namespaces)
            if surname is not None and given_name is not None:
                authors.append(f"{given_name.text} {surname.text}")

        # 提取日期（使用 dc:date）
        date_elem = desc.find('dc:date', namespaces)
        pub_date = None
        if date_elem is not None and date_elem.text:
            try:
                # 解析日期格式：2025-02-19
                pub_date = datetime.strptime(date_elem.text, '%Y-%m-%d').date()
            except ValueError:
                try:
                    # 尝试其他格式
                    pub_date = datetime.strptime(date_elem.text, '%Y-%m-%d %H:%M:%S').date()
                except ValueError:
                    pub_date = date.today()
        else:
            pub_date = date.today()

        # PDF 和摘要链接
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
        abs_url = f"https://arxiv.org/abs/{arxiv_id}"

        articles.append({
            'id': arxiv_id,
            'title': title,
            'authors': authors,
            'summary': abstract,
            'pdf_url': pdf_url,
            'abs_url': abs_url,
            'crawled_at': pub_date,  # 使用 dc:date
            'categories': [],  # 稍后通过 arXiv API 补齐
        })

    return articles


def fetch_arxiv_metadata(arxiv_ids: list[str]) -> dict:
    """
    通过 arXiv API 获取文章元数据（categories 等）
    """
    import arxiv

    metadata = {}
    client = arxiv.Client()

    # 分批查询（每批最多 100 个）
    batch_size = 100
    for i in range(0, len(arxiv_ids), batch_size):
        batch = arxiv_ids[i:i + batch_size]
        search = arxiv.Search(id_list=batch)

        for paper in client.results(search):
            paper_id = paper.entry_id.split('/')[-1]
            # 移除版本号（如 v1, v2）
            paper_id = re.sub(r'v\d+$', '', paper_id)
            metadata[paper_id] = {
                'categories': list(paper.categories),
                'comment': paper.comment or '',
            }

    return metadata


def import_articles(articles: list[dict], db) -> tuple[int, int]:
    """
    导入文章到数据库

    返回：(新增数量, 已存在数量)
    """
    from app.models.article import Article

    new_count = 0
    existing_count = 0

    for article_data in articles:
        # 检查是否已存在
        existing = db.query(Article).filter(Article.id == article_data['id']).first()
        if existing:
            existing_count += 1
            continue

        article = Article(
            id=article_data['id'],
            title=article_data['title'],
            authors=article_data['authors'],
            categories=article_data.get('categories', []),
            summary=article_data['summary'],
            pdf_url=article_data['pdf_url'],
            abs_url=article_data['abs_url'],
            comment=article_data.get('comment', ''),
            crawled_at=article_data['crawled_at'],
        )
        db.add(article)
        new_count += 1

    db.commit()
    return new_count, existing_count


def mark_as_liked(article_ids: list[str], user_id: int, db) -> int:
    """
    将文章标记为喜欢

    返回：标记喜欢的数量
    """
    from app.models.recommendation import UserRecommendation

    liked_count = 0
    for article_id in article_ids:
        # 检查是否已有记录
        existing = db.query(UserRecommendation).filter(
            UserRecommendation.user_id == user_id,
            UserRecommendation.article_id == article_id
        ).first()

        if existing:
            if not existing.is_liked:
                existing.is_liked = True
                existing.liked_at = datetime.utcnow()
                liked_count += 1
        else:
            recommendation = UserRecommendation(
                user_id=user_id,
                article_id=article_id,
                recommended_at=date.today(),
                source='zotero',
                is_liked=True,
                liked_at=datetime.utcnow()
            )
            db.add(recommendation)
            liked_count += 1

    db.commit()
    return liked_count
