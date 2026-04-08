from pydantic import BaseModel, Field
from typing import Dict, Optional

class ResourceState(BaseModel):
    boats: int = 0
    ambulances: int = 0
    food_kits: int = 0

class Observation(BaseModel):
    task_id: str = Field(description="The current active task (triage_basic, resource_allocation, signal_vs_noise)")
    step: int = Field(description="Current step in the episode")
    intelligence_report: str = Field(description="Text briefing of the current situation")
    telemetry_data: Dict[str, str] = Field(description="Raw sensor data from regions")
    available_resources: ResourceState = Field(description="Resources currently available for deployment")
    last_action_feedback: Optional[str] = Field(None, description="Feedback from the previous step")

class Action(BaseModel):
    threat_level: str = Field("low", description="Classified threat level: 'low', 'medium', 'high'")
    deploy_region: Optional[str] = Field(None, description="Name of the region to send resources")
    resource_allocation: Dict[str, int] = Field(default_factory=dict, description="Resources to deploy, e.g. {'boats': 2}")
    reasoning: str = Field(..., description="Brief logical justification for this action")