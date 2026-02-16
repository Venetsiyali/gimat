"""
GIMAT - Ontology Endpoints
Neo4j graph database queries for river network topology
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Optional
from database.neo4j_db import get_neo4j, Neo4jDatabase
from models.schemas import (
    RiverCreateRequest, HydropostCreateRequest,
    ReservoirCreateRequest, NetworkResponse
)

router = APIRouter()


# ==========================================
# Node Creation Endpoints
# ==========================================

@router.post("/rivers", status_code=201)
async def create_river(
    river: RiverCreateRequest,
    neo4j: Neo4jDatabase = Depends(get_neo4j)
):
    """Create a new river in the ontology"""
    
    await neo4j.create_river(
        name=river.name,
        basin=river.basin,
        length_km=river.length_km,
        properties=river.properties or {}
    )
    
    return {
        "message": f"River '{river.name}' created successfully",
        "river_name": river.name
    }


@router.post("/hydroposts", status_code=201)
async def create_hydropost(
    hydropost: HydropostCreateRequest,
    neo4j: Neo4jDatabase = Depends(get_neo4j)
):
    """Create a new hydropost (monitoring station)"""
    
    await neo4j.create_hydropost(
        station_id=hydropost.station_id,
        name=hydropost.name,
        river_name=hydropost.river_name,
        latitude=hydropost.latitude,
        longitude=hydropost.longitude,
        river_km=hydropost.river_km,
        properties=hydropost.properties or {}
    )
    
    return {
        "message": f"Hydropost '{hydropost.name}' created successfully",
        "station_id": hydropost.station_id
    }


@router.post("/reservoirs", status_code=201)
async def create_reservoir(
    reservoir: ReservoirCreateRequest,
    neo4j: Neo4jDatabase = Depends(get_neo4j)
):
    """Create a new reservoir"""
    
    await neo4j.create_reservoir(
        reservoir_id=reservoir.reservoir_id,
        name=reservoir.name,
        river_name=reservoir.river_name,
        capacity_m3=reservoir.capacity_m3,
        latitude=reservoir.latitude,
        longitude=reservoir.longitude,
        properties=reservoir.properties or {}
    )
    
    return {
        "message": f"Reservoir '{reservoir.name}' created successfully",
        "reservoir_id": reservoir.reservoir_id
    }


# ==========================================
# Network Query Endpoints
# ==========================================

@router.get("/network/{river_name}", response_model=NetworkResponse)
async def get_river_network(
    river_name: str,
    neo4j: Neo4jDatabase = Depends(get_neo4j)
):
    """
    Get complete river network topology
    
    Returns nodes (reaches, hydroposts, reservoirs) and relationships
    """
    
    network_data = await neo4j.get_river_network(river_name)
    
    # Process and format network data
    nodes = []
    edges = []
    
    for record in network_data:
        reach = record.get('rr')
        flow_rel = record.get('f')
        downstream = record.get('downstream')
        hydroposts = record.get('hydroposts', [])
        
        if reach:
            nodes.append({
                "id": reach['reach_id'],
                "type": "river_reach",
                "properties": dict(reach)
            })
        
        if flow_rel and downstream:
            edges.append({
                "from": reach['reach_id'],
                "to": downstream['reach_id'],
                "type": "FLOWS_TO"
            })
        
        for hp in hydroposts:
            if hp:
                nodes.append({
                    "id": hp['station_id'],
                    "type": "hydropost",
                    "properties": dict(hp)
                })
                edges.append({
                    "from": hp['station_id'],
                    "to": reach['reach_id'],
                    "type": "MONITORS"
                })
    
    return {
        "river_name": river_name,
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges)
    }


@router.get("/hydroposts/{station_id}/upstream")
async def get_upstream_stations(
    station_id: str,
    max_hops: int = 10,
    neo4j: Neo4jDatabase = Depends(get_neo4j)
):
    """Get all upstream monitoring stations"""
    
    upstream = await neo4j.get_upstream_stations(station_id, max_hops)
    
    if not upstream:
        return {
            "station_id": station_id,
            "upstream_stations": [],
            "count": 0,
            "message": "No upstream stations found"
        }
    
    return {
        "station_id": station_id,
        "upstream_stations": upstream,
        "count": len(upstream)
    }


@router.get("/hydroposts/{station_id}/downstream")
async def get_downstream_stations(
    station_id: str,
    max_hops: int = 10,
    neo4j: Neo4jDatabase = Depends(get_neo4j)
):
    """Get all downstream monitoring stations"""
    
    downstream = await neo4j.get_downstream_stations(station_id, max_hops)
    
    if not downstream:
        return {
            "station_id": station_id,
            "downstream_stations": [],
            "count": 0,
            "message": "No downstream stations found"
        }
    
    return {
        "station_id": station_id,
        "downstream_stations": downstream,
        "count": len(downstream)
    }


@router.get("/hydroposts/{station_id}/influences")
async def get_influencing_reservoirs(
    station_id: str,
    neo4j: Neo4jDatabase = Depends(get_neo4j)
):
    """Get reservoirs that influence this hydropost"""
    
    reservoirs = await neo4j.get_influencing_reservoirs(station_id)
    
    return {
        "station_id": station_id,
        "influencing_reservoirs": reservoirs,
        "count": len(reservoirs)
    }


# ==========================================
# Relationship Endpoints
# ==========================================

@router.post("/relationships/flows-to")
async def create_flows_to_relationship(
    upstream_reach_id: str,
    downstream_reach_id: str,
    neo4j: Neo4jDatabase = Depends(get_neo4j)
):
    """Create FLOWS_TO relationship between river reaches"""
    
    await neo4j.create_flows_to(upstream_reach_id, downstream_reach_id)
    
    return {
        "message": f"Created FLOWS_TO relationship",
        "from": upstream_reach_id,
        "to": downstream_reach_id
    }


@router.post("/relationships/monitors")
async def create_monitors_relationship(
    station_id: str,
    reach_id: str,
    neo4j: Neo4jDatabase = Depends(get_neo4j)
):
    """Create MONITORS relationship (Hydropost monitors RiverReach)"""
    
    await neo4j.create_monitors(station_id, reach_id)
    
    return {
        "message": "Created MONITORS relationship",
        "hydropost": station_id,
        "reach": reach_id
    }


@router.post("/relationships/influences")
async def create_influences_relationship(
    reservoir_id: str,
    station_id: str,
    distance_km: Optional[float] = None,
    neo4j: Neo4jDatabase = Depends(get_neo4j)
):
    """Create INFLUENCES relationship (Reservoir influences Hydropost)"""
    
    await neo4j.create_influences(reservoir_id, station_id, distance_km)
    
    return {
        "message": "Created INFLUENCES relationship",
        "reservoir": reservoir_id,
        "hydropost": station_id,
        "distance_km": distance_km
    }


# ==========================================
# Utility Endpoints
# ==========================================

@router.get("/basins")
async def get_basins(neo4j: Neo4jDatabase = Depends(get_neo4j)):
    """Get list of all river basins in the system"""
    
    query = """
    MATCH (r:River)
    RETURN DISTINCT r.basin as basin, r.name as river_name, r.length_km as length_km
    ORDER BY r.basin
    """
    
    result = await neo4j.execute_query(query)
    
    # Group by basin
    basins = {}
    for record in result:
        basin_name = record['basin']
        if basin_name not in basins:
            basins[basin_name] = {
                "basin_name": basin_name,
                "rivers": []
            }
        basins[basin_name]["rivers"].append({
            "river_name": record['river_name'],
            "length_km": record['length_km']
        })
    
    return {
        "basins": list(basins.values()),
        "total_basins": len(basins)
    }


@router.get("/statistics")
async def get_ontology_statistics(neo4j: Neo4jDatabase = Depends(get_neo4j)):
    """Get statistics about the ontology graph"""
    
    stats_query = """
    MATCH (r:River) WITH count(r) as river_count
    MATCH (rr:RiverReach) WITH river_count, count(rr) as reach_count
    MATCH (h:Hydropost) WITH river_count, reach_count, count(h) as hydropost_count
    MATCH (res:Reservoir) WITH river_count, reach_count, hydropost_count, count(res) as reservoir_count
    MATCH ()-[rel]->() WITH river_count, reach_count, hydropost_count, reservoir_count, count(rel) as relationship_count
    RETURN river_count, reach_count, hydropost_count, reservoir_count, relationship_count
    """
    
    result = await neo4j.execute_query(stats_query)
    
    if result:
        stats = result[0]
        return {
            "nodes": {
                "rivers": stats.get('river_count', 0),
                "river_reaches": stats.get('reach_count', 0),
                "hydroposts": stats.get('hydropost_count', 0),
                "reservoirs": stats.get('reservoir_count', 0),
                "total": (stats.get('river_count', 0) + 
                         stats.get('reach_count', 0) + 
                         stats.get('hydropost_count', 0) + 
                         stats.get('reservoir_count', 0))
            },
            "relationships": {
                "total": stats.get('relationship_count', 0)
            }
        }
    
    return {"error": "Could not retrieve statistics"}
