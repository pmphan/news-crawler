from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .postgres_service import BasePostgresService
from database.schema.article import VnExpress, TuoiTre

class VnExpressDBService(BasePostgresService[VnExpress]):
    model = VnExpress

class TuoiTreDbService(BasePostgresService[TuoiTre]):
    model = TuoiTre

# Mapping spider name to DB service to use.
crawler_db_mapping = {
    "vnexpress": VnExpressDBService,
    "tuoitre": TuoiTreDbService
}