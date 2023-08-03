from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .postgres_service import BasePostgresService
from database.schema.article import Articles

class ArticleService(BasePostgresService[Articles]):
    model = Articles

    @classmethod
    async def get_all_article_ranked(cls, db: AsyncSession):
        query = select(cls.model).order_by(cls.model.score.desc())
        result = await db.execute(query)
        return result.scalars().all()