import uuid

from fastapi import HTTPException

from app.broker import RedisBroker
from app.landings_service.schema import LeadCreate


class LandingsService:
    @staticmethod
    async def create_new_lead(
            lead: LeadCreate,
            affiliate_id: uuid.UUID,
            broker: RedisBroker,
    ):
        """Creating new lead"""
        if lead.affiliate_id != affiliate_id:
            raise HTTPException(status_code=403, detail="ID mismatch")

        key = broker.create_redis_key(lead)
        if await broker.is_duplicate(key):
            raise HTTPException(status_code=409, detail="Duplicate lead within 10 min")

        await broker.add_to_queue(lead)

        return {"status": "ok"}