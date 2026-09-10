"""Process due Quality KPI digest subscriptions once.

Run from backend/: python scripts/dispatch_quality_digests.py
"""

import asyncio

from app.db.session import AsyncSessionLocal
from app.services.quality_digest_service import dispatch_due_digests


async def main() -> None:
    async with AsyncSessionLocal() as db:
        delivered = await dispatch_due_digests(db)
    print(f"Delivered {delivered} quality digest(s).")


if __name__ == "__main__":
    asyncio.run(main())
