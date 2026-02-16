"""
DSS API Endpoints - What-if Simulator
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict

router = APIRouter()


class Scenario(BaseModel):
    reservoir_id: str
    release_rate: float
    duration_hours: int = 24
    downstream_stations: List[str]


class SimulationResult(BaseModel):
    scenario: Dict
    predictions: List[Dict]
    duration_hours: int
    risk_level: str


@router.post("/simulate", response_model=SimulationResult)
async def simulate_scenario(scenario: Scenario):
    """
    Simulate reservoir release scenario
    
    Args:
        scenario: Scenario parameters
    
    Returns:
        Simulation results
    """
    from dss.simulator import WhatIfSimulator
    from models.gnn_model import TemporalGNN
    
    # Load GNN model (placeholder)
    gnn_model = None  # Would load trained model
    
    simulator = WhatIfSimulator(gnn_model)
    
    result = simulator.simulate_scenario(
        scenario=scenario.dict(),
        downstream_stations=scenario.downstream_stations,
        duration_hours=scenario.duration_hours
    )
    
    return SimulationResult(**result)


@router.post("/compare")
async def compare_scenarios(scenarios: List[Scenario]):
    """
    Compare multiple scenarios
    
    Args:
        scenarios: List of scenarios
    
    Returns:
        Comparison results
    """
    from dss.simulator import WhatIfSimulator
    
    gnn_model = None
    simulator = WhatIfSimulator(gnn_model)
    
    scenario_dicts = [s.dict() for s in scenarios]
    
    comparison = simulator.compare_scenarios(scenario_dicts)
    
    return comparison
