from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.home_state import HomeState

HOME_STATE_ID = 1


class HomeStateRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self) -> HomeState:
        result = await self.db.execute(select(HomeState).where(HomeState.id == HOME_STATE_ID))
        row = result.scalar_one_or_none()
        if row is None:
            row = HomeState(id=HOME_STATE_ID, scenario="sleep", auto_mode=True)
            self.db.add(row)
            await self.db.flush()
            await self.db.refresh(row)
        return row

    async def set_scenario(self, scenario: str) -> HomeState:
        row = await self.get()
        row.scenario = scenario
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def set_auto_mode(self, auto: bool) -> HomeState:
        row = await self.get()
        row.auto_mode = auto
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def update(self, *, scenario: str | None = None, auto_mode: bool | None = None) -> HomeState:
        row = await self.get()
        if scenario is not None:
            row.scenario = scenario
        if auto_mode is not None:
            row.auto_mode = auto_mode
        await self.db.flush()
        await self.db.refresh(row)
        return row
