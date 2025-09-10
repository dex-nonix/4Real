from typing import Dict, Any

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from nonix_plugin.base import BasePlugin
from .models import Base

_async_session_local = None


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def set_async_session_local(value):
    global _async_session_local
    _async_session_local = value


def AsyncSessionLocal() -> async_sessionmaker:
    return _async_session_local()


class NxWebDbPlugin(BasePlugin):
    engine = None

    def _configure(self, config: Dict[str, Any]):
        pass

    async def _startup(self, config: Dict[str, Any]):
        global _async_session_local
        options = config.get("options", {})

        self.engine = engine = create_async_engine(config["url"], **options)
        set_async_session_local(async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False))

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def _shutdown(self, config: Dict[str, Any]):
        if self.engine:
            await self.engine.dispose()
