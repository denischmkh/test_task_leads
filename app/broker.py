import asyncio
import json
import sys
from os.path import abspath, dirname, join
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

BASE_DIR = dirname(abspath(__file__))

sys.path.append(str(join(BASE_DIR, '..')))

from redis.asyncio import Redis

from app.config import settings
from app.database import async_session_maker
from app.landings_service.schema import LeadCreate
from app.models import Lead


class RedisBroker:
    """Redis Broker"""
    def __init__(self):
        self.redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )

    def create_redis_key(self, lead_schema: LeadCreate):
        return f"dedup:{lead_schema.name}:{lead_schema.phone}:{lead_schema.offer_id}:{lead_schema.affiliate_id}"

    async def is_duplicate(self, key: str) -> bool:
        res = await self.redis.set(key, "1", ex=600, nx=True)
        return not res

    async def add_to_queue(self, lead_schema: LeadCreate):
        await self.redis.lpush("lead_queue", lead_schema.model_dump_json())

    async def delete_from_queue(self, key):
        await self.redis.lrem("lead_queue", 0, key)

    async def process_queue(self, session: Optional[AsyncSession] = None):
        print("Worker started. Waiting for leads...")
        while True:
            try:
                data = await self.redis.brpop("lead_queue", timeout=1)
                if data:
                    _, raw_lead = data
                    lead_dict = json.loads(raw_lead)
                    new_lead = Lead(**lead_dict)
                    if session:
                        session.add(new_lead)
                        await session.commit()
                    else:
                        async with async_session_maker() as new_session:
                            new_session.add(new_lead)
                            await new_session.commit()
                            print(f"Lead saved via new session: {new_lead.name}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Worker Error: {e}")

redis_broker = RedisBroker()

if __name__ == '__main__':
    asyncio.run(redis_broker.process_queue())