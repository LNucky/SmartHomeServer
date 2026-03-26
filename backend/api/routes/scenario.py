from fastapi import APIRouter, HTTPException

from api.deps import DbSession
from api.schemas import ScenarioResponse, ScenarioUpdateRequest
from db.repositories.device_repo import DeviceRepository
from db.repositories.home_state_repo import HomeStateRepository
from db.repositories.sensor_repo import SensorRepository
from services.scenario_engine import SCENARIOS, compute_device_states

router = APIRouter(prefix="/scenario", tags=["scenario"])


async def apply_rgb_from_scenario(db) -> None:
    """RGB (комн. 1): только при сценарии sunny; не управляется через POST /devices/rgb."""
    h_repo = HomeStateRepository(db)
    d_repo = DeviceRepository(db)
    home = await h_repo.get()
    await d_repo.set_state("rgb", 1, home.scenario == "sunny")


async def recompute_devices_if_auto(db) -> None:
    h_repo = HomeStateRepository(db)
    s_repo = SensorRepository(db)
    d_repo = DeviceRepository(db)
    home = await h_repo.get()
    if not home.auto_mode:
        return
    snap = await s_repo.get_snapshot_dict()
    states = compute_device_states(home.scenario, snap)
    await d_repo.apply_computed_states(states)


@router.get("", response_model=ScenarioResponse)
async def get_scenario(db: DbSession):
    h = await HomeStateRepository(db).get()
    await db.commit()
    return ScenarioResponse(scenario=h.scenario, auto_mode=h.auto_mode)


@router.put("", response_model=ScenarioResponse)
async def put_scenario(body: ScenarioUpdateRequest, db: DbSession):
    if body.scenario is None and body.auto_mode is None:
        raise HTTPException(400, "Укажите scenario и/или auto_mode")

    h_repo = HomeStateRepository(db)
    if body.scenario is not None:
        if body.scenario not in SCENARIOS:
            raise HTTPException(400, f"scenario ∈ {sorted(SCENARIOS)}")
    h = await h_repo.update(scenario=body.scenario, auto_mode=body.auto_mode)
    await apply_rgb_from_scenario(db)
    await recompute_devices_if_auto(db)
    await db.commit()
    h = await h_repo.get()
    return ScenarioResponse(scenario=h.scenario, auto_mode=h.auto_mode)
