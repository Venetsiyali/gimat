"""
GIMAT - Data Seeding Script
Populates PostgreSQL and Neo4j with real Uzbekistan hydrological stations and mock time-series data.
Stations: Chorvoq, G'azalkent, Chinoz, Ravatxo'ja, Navoiy, Bekobod, Termiz.
"""

import asyncio
import random
import sys
import os
from datetime import datetime, timedelta
import numpy as np

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.timescale import init_db, AsyncSessionLocal, Observation
from database.neo4j_db import neo4j_db

# Real Station Data
STATIONS = [
    {
        "id": "chorvoq",
        "name": "Chorvoq suv ombori",
        "river": "Chirchiq",
        "lat": 41.6268,
        "lon": 70.0276,
        "baseline_wl": 880.0,  # meters asl
        "baseline_Q": 250.0    # m3/s
    },
    {
        "id": "gazalkent",
        "name": "G'azalkent gidroposti",
        "river": "Chirchiq",
        "lat": 41.5627,
        "lon": 69.7712,
        "baseline_wl": 750.0,
        "baseline_Q": 240.0
    },
    {
        "id": "chinoz",
        "name": "Chinoz gidroposti",
        "river": "Sirdaryo",
        "lat": 40.9419,
        "lon": 68.7521,
        "baseline_wl": 260.0,
        "baseline_Q": 450.0
    },
    {
        "id": "ravatxoja",
        "name": "Ravatxo'ja gidrouzeli",
        "river": "Zarafshon",
        "lat": 39.5224,
        "lon": 67.2415,
        "baseline_wl": 640.0,
        "baseline_Q": 180.0
    },
    {
        "id": "navoiy",
        "name": "Navoiy gidroposti",
        "river": "Zarafshon",
        "lat": 40.0984,
        "lon": 65.3712,
        "baseline_wl": 340.0,
        "baseline_Q": 120.0
    },
    {
        "id": "bekobod",
        "name": "Bekobod gidroposti",
        "river": "Sirdaryo",
        "lat": 40.2136,
        "lon": 69.2618,
        "baseline_wl": 310.0,
        "baseline_Q": 550.0
    },
    {
        "id": "termiz",
        "name": "Termiz gidroposti",
        "river": "Amudaryo",
        "lat": 37.2241,
        "lon": 67.2764,
        "baseline_wl": 305.0,
        "baseline_Q": 1800.0
    }
]

async def seed_postgres():
    """Seed PostgreSQL with stations and 30 days of mock data"""
    print("⏳ Seeding PostgreSQL...")
    
    # Initialize DB (create tables)
    await init_db()
    
    async with AsyncSessionLocal() as session:
        observations = []
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        # Generate hourly data for 30 days
        for station in STATIONS:
            print(f"   Generating data for {station['name']}...")
            current = start_date
            while current <= end_date:
                # Add some random variation (seasonal + noise)
                day_factor = np.sin((current.timetuple().tm_yday / 365.0) * 2 * np.pi)
                hour_factor = np.sin((current.hour / 24.0) * 2 * np.pi)
                
                # Water Level (H)
                noise_h = np.random.normal(0, 0.05)
                wl = station['baseline_wl'] + (day_factor * 2.0) + (hour_factor * 0.1) + noise_h
                
                # Discharge (Q)
                noise_q = np.random.normal(0, 5.0)
                q = station['baseline_Q'] + (day_factor * 50.0) + (hour_factor * 10.0) + noise_q
                
                # Temperature (T)
                temp_noise = np.random.normal(0, 0.5)
                temp = 15.0 + (day_factor * 10.0) + (hour_factor * 2.0) + temp_noise
                
                obs = Observation(
                    timestamp=current,
                    station_id=station['id'],
                    station_name=station['name'],
                    river_name=station['river'],
                    latitude=station['lat'],
                    longitude=station['lon'],
                    water_level=round(wl, 2),
                    discharge=round(max(0, q), 1), # Ensure Q >= 0
                    temperature=round(max(0, temp), 1),
                    data_source="mock_seed_v1",
                    quality_flag="simulated"
                )
                observations.append(obs)
                
                current += timedelta(hours=1)
                
            # Batch insert every station to avoid memory issues
            session.add_all(observations)
            await session.commit()
            observations = []
            
    print("✓ PostgreSQL seeding complete!")

async def seed_neo4j():
    """Seed Neo4j with Hydropost nodes and relationships"""
    print("⏳ Seeding Neo4j...")
    
    try:
        await neo4j_db.connect()
        
        # Clear existing relevant data (optional, be careful in prod!)
        # await neo4j_db.execute_write("MATCH (h:Hydropost) DETACH DELETE h")
        
        # Create Hydropost Nodes
        for s in STATIONS:
            await neo4j_db.create_hydropost(
                station_id=s['id'],
                name=s['name'],
                river_name=s['river'],
                latitude=s['lat'],
                longitude=s['lon']
            )
            print(f"   Created node: {s['name']}")
            
        # Create Relationships (Topology)
        # Chirchiq: Chorvoq -> G'azalkent -> (flows into Sirdaryo)
        await neo4j_db.execute_write("""
            MATCH (up:Hydropost {station_id: 'chorvoq'})
            MATCH (down:Hydropost {station_id: 'gazalkent'})
            MERGE (up)-[:FLOWS_TO]->(down)
        """)
        
        # Sirdaryo: Bekobod -> Chinoz
        await neo4j_db.execute_write("""
            MATCH (up:Hydropost {station_id: 'bekobod'})
            MATCH (down:Hydropost {station_id: 'chinoz'})
            MERGE (up)-[:FLOWS_TO]->(down)
        """)
        
        # Zarafshon: Ravatxo'ja -> Navoiy
        await neo4j_db.execute_write("""
            MATCH (up:Hydropost {station_id: 'ravatxoja'})
            MATCH (down:Hydropost {station_id: 'navoiy'})
            MERGE (up)-[:FLOWS_TO]->(down)
        """)
        
        print("✓ Neo4j seeding complete!")
        
    except Exception as e:
        print(f"❌ Neo4j error: {e}")
    finally:
        await neo4j_db.close()

async def main():
    await seed_postgres()
    await seed_neo4j()

if __name__ == "__main__":
    asyncio.run(main())
