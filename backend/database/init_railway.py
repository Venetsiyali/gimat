"""
Railway-optimized Database Initialization
Auto-detects Railway environment and initializes databases
"""

import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from neo4j import AsyncGraphDatabase


async def init_timescale():
    """Initialize TimescaleDB with Railway DATABASE_URL"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("[WARN] DATABASE_URL not set, skipping TimescaleDB init")
        return
    
    # Convert to asyncpg
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql+asyncpg://', 1)
    
    print("[INIT] Initializing TimescaleDB...")
    
    engine = create_async_engine(database_url, echo=False)
    
    async with engine.begin() as conn:
        # Enable TimescaleDB extension
        await conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
        print("[INIT] ✓ TimescaleDB extension enabled")
        
        # Create hypertables if not exist
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS observations (
                id SERIAL,
                station_id VARCHAR(50) NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                discharge FLOAT,
                water_level FLOAT,
                temperature FLOAT,
                PRIMARY KEY (id, timestamp)
            );
        """)
        
        await conn.execute("""
            SELECT create_hypertable('observations', 'timestamp', 
                if_not_exists => TRUE,
                chunk_time_interval => INTERVAL '1 day'
            );
        """)
        print("[INIT] ✓ Hypertable 'observations' created")
        
        # Create indexes
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_observations_station_time 
            ON observations (station_id, timestamp DESC);
        """)
        
        # Enable compression
        await conn.execute("""
            ALTER TABLE observations SET (
                timescaledb.compress,
                timescaledb.compress_segmentby = 'station_id'
            );
        """)
        
        await conn.execute("""
            SELECT add_compression_policy('observations', INTERVAL '7 days', if_not_exists => TRUE);
        """)
        print("[INIT] ✓ Compression enabled")
        
        # Create predictions table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id SERIAL,
                station_id VARCHAR(50) NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                model_name VARCHAR(100),
                predicted_value FLOAT,
                confidence FLOAT,
                PRIMARY KEY (id, timestamp)
            );
        """)
        
        await conn.execute("""
            SELECT create_hypertable('predictions', 'timestamp', 
                if_not_exists => TRUE,
                chunk_time_interval => INTERVAL '1 day'
            );
        """)
        print("[INIT] ✓ Predictions hypertable created")
    
    await engine.dispose()
    print("[INIT] ✓ TimescaleDB initialization complete")


async def init_neo4j():
    """Initialize Neo4j with Railway NEO4J_URI"""
    
    neo4j_uri = os.getenv('NEO4J_URI')
    neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
    neo4j_password = os.getenv('NEO4J_PASSWORD')
    
    if not neo4j_uri or not neo4j_password:
        print("[WARN] Neo4j credentials not set, skipping Neo4j init")
        return
    
    print("[INIT] Initializing Neo4j...")
    
    driver = AsyncGraphDatabase.driver(
        neo4j_uri,
        auth=(neo4j_user, neo4j_password)
    )
    
    async with driver.session() as session:
        # Create constraints
        await session.run("""
            CREATE CONSTRAINT station_id_unique IF NOT EXISTS
            FOR (s:Station) REQUIRE s.station_id IS UNIQUE
        """)
        
        await session.run("""
            CREATE CONSTRAINT river_name_unique IF NOT EXISTS
            FOR (r:River) REQUIRE r.name IS UNIQUE
        """)
        
        print("[INIT] ✓ Neo4j constraints created")
        
        # Create indexes
        await session.run("""
            CREATE INDEX station_name_idx IF NOT EXISTS
            FOR (s:Station) ON (s.name)
        """)
        
        await session.run("""
            CREATE INDEX river_name_idx IF NOT EXISTS
            FOR (r:River) ON (r.name)
        """)
        
        print("[INIT] ✓ Neo4j indexes created")
        
        # Create sample nodes (Chirchiq basin)
        await session.run("""
            MERGE (r:River {name: 'Chirchiq'})
            SET r.basin = 'Syrdaryo', r.length_km = 155
            
            MERGE (s1:Station {station_id: 'HP_CHIRCHIQ_001'})
            SET s1.name = 'Gazalkent', s1.latitude = 41.56, s1.longitude = 70.12
            
            MERGE (s2:Station {station_id: 'HP_CHIRCHIQ_002'})
            SET s2.name = 'Tashkent', s2.latitude = 41.31, s2.longitude = 69.27
            
            MERGE (s1)-[:LOCATED_ON]->(r)
            MERGE (s2)-[:LOCATED_ON]->(r)
            MERGE (s1)-[:UPSTREAM_OF {distance_km: 45}]->(s2)
        """)
        
        print("[INIT] ✓ Sample Chirchiq basin data created")
    
    await driver.close()
    print("[INIT] ✓ Neo4j initialization complete")


async def init_all_databases():
    """Initialize all databases"""
    print("=" * 50)
    print("Database Initialization Started")
    print("=" * 50)
    
    try:
        await init_timescale()
    except Exception as e:
        print(f"[ERROR] TimescaleDB init failed: {e}")
    
    try:
        await init_neo4j()
    except Exception as e:
        print(f"[ERROR] Neo4j init failed: {e}")
    
    print("=" * 50)
    print("Database Initialization Complete")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(init_all_databases())
