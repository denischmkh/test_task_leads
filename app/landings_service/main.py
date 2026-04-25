import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from app.auth_service.jwt import get_current_affiliate_id
from app.broker import redis_broker
from app.database import async_session_maker
from app.landings_service.schema import LeadCreate
from app.landings_service.services import LandingsService
from app.models import Affiliate, Offer


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_session_maker() as session:
        affiliate_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        offer_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

        affiliate_exists = await session.get(Affiliate, affiliate_id)
        offer_exists = await session.get(Offer, offer_id)

        if not affiliate_exists:
            session.add(Affiliate(id=affiliate_id, name="Test Shop"))
            print(f"DEBUG: Affiliate {affiliate_id} created.")

        if not offer_exists:
            session.add(Offer(id=offer_id, name="Test Offer"))
            print(f"DEBUG: Offer {offer_id} created.")

        if not affiliate_exists or not offer_exists:
            await session.commit()
        else:
            print("DEBUG: All test records already exist.")

    yield

app = FastAPI(lifespan=lifespan)


@app.post('/landings/lead')
async def create_lead(
        lead: LeadCreate,
        affiliate_id: uuid.UUID = Depends(get_current_affiliate_id)
):
    """Creating new lead"""
    return await LandingsService.create_new_lead(
        lead=lead,
        affiliate_id=affiliate_id,
        broker=redis_broker
    )

