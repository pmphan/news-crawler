from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .postgres_service import BasePostgresService
from database.schema.article import VnExpress

class VnExpressDBService(BasePostgresService[VnExpress]):
    model = VnExpress