import uuid
from datetime import datetime

from fastapi import FastAPI, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth_service.jwt import get_current_affiliate_id
from app.core_service.services import CoreService
from app.core_service.utils import GroupEnum
from app.database import get_async_session

app = FastAPI()

@app.get("/core/leads")
async def get_leads(
        date_from: datetime = Query(..., description="Start date (YYYY-MM-DDTHH:MM:SS)"),
        date_to: datetime = Query(..., description="End date (YYYY-MM-DDTHH:MM:SS)"),
        group: GroupEnum = Query(..., description="Grouping criteria"),
        affiliate_id: uuid.UUID = Depends(get_current_affiliate_id),
        session: AsyncSession = Depends(get_async_session)
):
    """Extracting grouped leads"""
    return await CoreService.get_lead_statistics(
        date_from,
        date_to,
        group.value,
        affiliate_id,
        session
    )