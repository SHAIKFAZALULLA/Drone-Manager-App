from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal

class DroneIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    manufacturer: str = Field(min_length=2, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    serial_number: str = Field(min_length=2, max_length=100)
    drone_type: str = Field(min_length=2, max_length=100)
    max_flight_time: Optional[float] = Field(default=None, gt=0)
    max_payload: Optional[float] = Field(default=None, ge=0)
    purchase_date: Optional[str] = None
    status: Literal["AVAILABLE","IN_MISSION","MAINTENANCE","INACTIVE","RETIRED"] = "AVAILABLE"

class BatteryIn(BaseModel):
    drone_id: str = Field(min_length=1)
    serial_number: str = Field(min_length=2)
    battery_percentage: float = Field(ge=0, le=100)
    voltage: Optional[float] = Field(default=None, gt=0)
    temperature: Optional[float] = None
    charge_cycles: int = Field(default=0, ge=0)
    health_percentage: float = Field(default=100, ge=0, le=100)
    last_charged: Optional[str] = None

class MissionIn(BaseModel):
    name: str = Field(min_length=2)
    drone_id: str = Field(min_length=1)
    scheduled_start: str
    scheduled_end: str
    destination: Optional[str] = None
    notes: Optional[str] = None
    status: Literal["SCHEDULED","IN_PROGRESS","COMPLETED","CANCELLED"] = "SCHEDULED"

class FlightIn(BaseModel):
    drone_id: str = Field(min_length=1)
    mission_id: Optional[str] = None
    actual_start: str
    actual_end: str
    start_battery_percentage: float = Field(ge=0, le=100)
    end_battery_percentage: float = Field(ge=0, le=100)
    distance_km: float = Field(default=0, ge=0)
    notes: Optional[str] = None
    status: Literal["COMPLETED","ABORTED","FAILED"] = "COMPLETED"

class MaintenanceIn(BaseModel):
    drone_id: str = Field(min_length=1)
    title: str = Field(min_length=2)
    maintenance_type: Literal["ROUTINE","INSPECTION","REPAIR","BATTERY_REPLACEMENT","SOFTWARE_UPDATE","CALIBRATION","EMERGENCY"] = "ROUTINE"
    scheduled_date: str
    priority: Literal["LOW","MEDIUM","HIGH","CRITICAL"] = "MEDIUM"
    notes: Optional[str] = None
    status: Literal["SCHEDULED","IN_PROGRESS","COMPLETED","CANCELLED","OVERDUE"] = "SCHEDULED"
