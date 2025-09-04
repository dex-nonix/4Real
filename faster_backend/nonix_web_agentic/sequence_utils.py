from __future__ import annotations

from sqlalchemy import select

from nonix_web_db import AsyncSessionLocal
from .models.message_sequence import MessageSequence



async def next_seq(history_id: int) -> int:
    async with AsyncSessionLocal() as db_session:
        async with db_session.begin():
            result = await db_session.execute(
                select(MessageSequence).where(MessageSequence.history_id == history_id).with_for_update()
            )
            ms = result.scalar_one_or_none()
            if ms is None:
                ms = MessageSequence(history_id=history_id, next_seq=1)
                db_session.add(ms)
                await db_session.flush()
                value = 1
                ms.next_seq = 2
            else:
                value = ms.next_seq or 1
                ms.next_seq = value + 1
        await db_session.commit()
        return value