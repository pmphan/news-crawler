from sqlalchemy.ext.asyncio import AsyncSession

from .postgres_service import BasePostgresService
from schema.postgres import Articles

class ArticleService(BasePostgresService[Articles]):
    model = Articles