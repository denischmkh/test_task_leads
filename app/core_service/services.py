import uuid
from collections import defaultdict
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Lead


class CoreService:
    @staticmethod
    async def get_lead_statistics(
            date_from: datetime,
            date_to: datetime,
            group: str,
            affiliate_id: uuid.UUID,
            session: AsyncSession,
    ):
        query = (
            select(Lead)
            .where(Lead.affiliate_id == affiliate_id)
            .where(Lead.created_at >= date_from)
            .where(Lead.created_at <= date_to)
            .order_by(Lead.created_at.desc())
        )

        result = await session.execute(query)
        leads = result.scalars().all()

        grouped_data = defaultdict(list)

        for lead in leads:
            if group == "date":
                key = lead.created_at.date().isoformat()
            else:
                key = str(lead.offer_id)

            grouped_data[key].append({
                "id": str(lead.id),
                "name": lead.name,
                "phone": lead.phone,
                "country": lead.country,
                "created_at": lead.created_at.isoformat(),
                "offer_id": str(lead.offer_id)
            })

        response = []
        for key, items in grouped_data.items():
            response.append({
                "group_key": key,
                "count": len(items),
                "leads": items
            })

        return {
            "affiliate_id": affiliate_id,
            "total_count": len(leads),
            "data": response
        }