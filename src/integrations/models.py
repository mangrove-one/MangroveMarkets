"""Pydantic models for external integrations."""
from src.shared.types import MangroveBaseModel


class AkashDeployment(MangroveBaseModel):
    deployment_id: str
    status: str
    provider: str = ""
    cost_per_block_akt: float = 0.0


class BittensorResponse(MangroveBaseModel):
    subnet_id: int
    response: str
    miner_uid: int = 0
    response_time_ms: float = 0.0
