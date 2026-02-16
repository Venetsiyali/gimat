"""
GIMAT - Neo4j Graph Database Configuration
Hydrological Ontology Management
"""

from neo4j import AsyncGraphDatabase
from config import settings
from typing import Dict, List, Optional
import asyncio


class Neo4jDatabase:
    """Neo4j database connection and query management"""
    
    def __init__(self):
        self.driver = None
    
    async def connect(self):
        """Initialize Neo4j connection"""
        self.driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
        print(f"✓ Connected to Neo4j at {settings.neo4j_uri}")
    
    async def close(self):
        """Close Neo4j connection"""
        if self.driver:
            await self.driver.close()
    
    async def execute_query(self, query: str, parameters: Dict = None):
        """Execute a Cypher query"""
        async with self.driver.session() as session:
            result = await session.run(query, parameters or {})
            return await result.data()
    
    async def execute_write(self, query: str, parameters: Dict = None):
        """Execute a write query"""
        async with self.driver.session() as session:
            result = await session.run(query, parameters or {})
            await session.close()
            return result
    
    # ==========================================
    # Node Creation Methods
    # ==========================================
    
    async def create_river(self, name: str, basin: str, length_km: float = None, 
                          properties: Dict = None) -> Dict:
        """Create a River node"""
        query = """
        CREATE (r:River {
            name: $name,
            basin: $basin,
            length_km: $length_km,
            properties: $properties
        })
        RETURN r
        """
        return await self.execute_write(query, {
            "name": name,
            "basin": basin,
            "length_km": length_km,
            "properties": properties or {}
        })
    
    async def create_river_reach(self, reach_id: str, river_name: str, 
                                 upstream_km: float, downstream_km: float,
                                 properties: Dict = None) -> Dict:
        """Create a RiverReach node (segment of river)"""
        query = """
        CREATE (rr:RiverReach {
            reach_id: $reach_id,
            river_name: $river_name,
            upstream_km: $upstream_km,
            downstream_km: $downstream_km,
            length_km: $length_km,
            properties: $properties
        })
        RETURN rr
        """
        return await self.execute_write(query, {
            "reach_id": reach_id,
            "river_name": river_name,
            "upstream_km": upstream_km,
            "downstream_km": downstream_km,
            "length_km": abs(downstream_km - upstream_km),
            "properties": properties or {}
        })
    
    async def create_hydropost(self, station_id: str, name: str, river_name: str,
                              latitude: float, longitude: float, 
                              river_km: float = None,
                              properties: Dict = None) -> Dict:
        """Create a Hydropost (monitoring station) node"""
        query = """
        CREATE (h:Hydropost {
            station_id: $station_id,
            name: $name,
            river_name: $river_name,
            latitude: $latitude,
            longitude: $longitude,
            river_km: $river_km,
            properties: $properties
        })
        RETURN h
        """
        return await self.execute_write(query, {
            "station_id": station_id,
            "name": name,
            "river_name": river_name,
            "latitude": latitude,
            "longitude": longitude,
            "river_km": river_km,
            "properties": properties or {}
        })
    
    async def create_reservoir(self, reservoir_id: str, name: str, river_name: str,
                              capacity_m3: float = None, latitude: float = None,
                              longitude: float = None, properties: Dict = None) -> Dict:
        """Create a Reservoir node"""
        query = """
        CREATE (res:Reservoir {
            reservoir_id: $reservoir_id,
            name: $name,
            river_name: $river_name,
            capacity_m3: $capacity_m3,
            latitude: $latitude,
            longitude: $longitude,
            properties: $properties
        })
        RETURN res
        """
        return await self.execute_write(query, {
            "reservoir_id": reservoir_id,
            "name": name,
            "river_name": river_name,
            "capacity_m3": capacity_m3,
            "latitude": latitude,
            "longitude": longitude,
            "properties": properties or {}
        })
    
    async def create_meteo_station(self, station_id: str, name: str,
                                  latitude: float, longitude: float,
                                  elevation_m: float = None,
                                  properties: Dict = None) -> Dict:
        """Create a MeteoStation node"""
        query = """
        CREATE (m:MeteoStation {
            station_id: $station_id,
            name: $name,
            latitude: $latitude,
            longitude: $longitude,
            elevation_m: $elevation_m,
            properties: $properties
        })
        RETURN m
        """
        return await self.execute_write(query, {
            "station_id": station_id,
            "name": name,
            "latitude": latitude,
            "longitude": longitude,
            "elevation_m": elevation_m,
            "properties": properties or {}
        })
    
    # ==========================================
    # Relationship Creation Methods
    # ==========================================
    
    async def create_flows_to(self, upstream_reach_id: str, downstream_reach_id: str):
        """Create FLOWS_TO relationship between river reaches"""
        query = """
        MATCH (up:RiverReach {reach_id: $upstream_id})
        MATCH (down:RiverReach {reach_id: $downstream_id})
        CREATE (up)-[:FLOWS_TO]->(down)
        """
        return await self.execute_write(query, {
            "upstream_id": upstream_reach_id,
            "downstream_id": downstream_reach_id
        })
    
    async def create_monitors(self, station_id: str, reach_id: str):
        """Create MONITORS relationship (Hydropost monitors RiverReach)"""
        query = """
        MATCH (h:Hydropost {station_id: $station_id})
        MATCH (rr:RiverReach {reach_id: $reach_id})
        CREATE (h)-[:MONITORS]->(rr)
        """
        return await self.execute_write(query, {
            "station_id": station_id,
            "reach_id": reach_id
        })
    
    async def create_located_on(self, reservoir_id: str, river_name: str):
        """Create LOCATED_ON relationship (Reservoir on River)"""
        query = """
        MATCH (res:Reservoir {reservoir_id: $reservoir_id})
        MATCH (r:River {name: $river_name})
        CREATE (res)-[:LOCATED_ON]->(r)
        """
        return await self.execute_write(query, {
            "reservoir_id": reservoir_id,
            "river_name": river_name
        })
    
    async def create_influences(self, reservoir_id: str, station_id: str, 
                               influence_distance_km: float = None):
        """Create INFLUENCES relationship (Reservoir influences Hydropost)"""
        query = """
        MATCH (res:Reservoir {reservoir_id: $reservoir_id})
        MATCH (h:Hydropost {station_id: $station_id})
        CREATE (res)-[:INFLUENCES {distance_km: $distance}]->(h)
        """
        return await self.execute_write(query, {
            "reservoir_id": reservoir_id,
            "station_id": station_id,
            "distance": influence_distance_km
        })
    
    # ==========================================
    # Query Methods
    # ==========================================
    
    async def get_upstream_stations(self, station_id: str, max_hops: int = 10) -> List[Dict]:
        """Get all upstream hydroposts"""
        query = """
        MATCH path = (h:Hydropost {station_id: $station_id})-[:MONITORS]->
                     (rr:RiverReach)-[:FLOWS_TO*1..{$max_hops}]->(upstream_rr:RiverReach)
                     <-[:MONITORS]-(upstream_h:Hydropost)
        RETURN DISTINCT upstream_h.station_id as station_id, 
               upstream_h.name as name,
               length(path) as distance_hops
        ORDER BY distance_hops
        """
        return await self.execute_query(query, {
            "station_id": station_id,
            "max_hops": max_hops
        })
    
    async def get_downstream_stations(self, station_id: str, max_hops: int = 10) -> List[Dict]:
        """Get all downstream hydroposts"""
        query = """
        MATCH path = (h:Hydropost {station_id: $station_id})-[:MONITORS]->
                     (rr:RiverReach)<-[:FLOWS_TO*1..{$max_hops}]-(downstream_rr:RiverReach)
                     <-[:MONITORS]-(downstream_h:Hydropost)
        RETURN DISTINCT downstream_h.station_id as station_id, 
               downstream_h.name as name,
               length(path) as distance_hops
        ORDER BY distance_hops
        """
        return await self.execute_query(query, {
            "station_id": station_id,
            "max_hops": max_hops
        })
    
    async def get_influencing_reservoirs(self, station_id: str) -> List[Dict]:
        """Get reservoirs that influence a hydropost"""
        query = """
        MATCH (res:Reservoir)-[inf:INFLUENCES]->(h:Hydropost {station_id: $station_id})
        RETURN res.reservoir_id as reservoir_id,
               res.name as name,
               res.capacity_m3 as capacity,
               inf.distance_km as distance_km
        ORDER BY distance_km
        """
        return await self.execute_query(query, {"station_id": station_id})
    
    async def get_river_network(self, river_name: str = None) -> Dict:
        """Get entire river network topology"""
        if river_name:
            query = """
            MATCH (rr:RiverReach {river_name: $river_name})
            OPTIONAL MATCH (rr)-[f:FLOWS_TO]->(downstream)
            OPTIONAL MATCH (h:Hydropost)-[:MONITORS]->(rr)
            RETURN rr, f, downstream, collect(h) as hydroposts
            """
            params = {"river_name": river_name}
        else:
            query = """
            MATCH (rr:RiverReach)
            OPTIONAL MATCH (rr)-[f:FLOWS_TO]->(downstream)
            OPTIONAL MATCH (h:Hydropost)-[:MONITORS]->(rr)
            RETURN rr, f, downstream, collect(h) as hydroposts
            """
            params = {}
        
        return await self.execute_query(query, params)


# Global Neo4j instance
neo4j_db = Neo4jDatabase()


# ==========================================
# Dependency for FastAPI
# ==========================================

async def get_neo4j():
    """Dependency for getting Neo4j database"""
    return neo4j_db
