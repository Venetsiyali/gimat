"""
Railway-compatible Database Configuration
Auto-connects to Railway-provisioned databases
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from neo4j import AsyncGraphDatabase
import redis.asyncio as aioredis
from typing import Optional


class DatabaseManager:
    """
    Unified database manager for Railway deployment
    Supports both Railway-provided and custom database URLs
    """
    
    def __init__(self):
        self.timescale_engine = None
        self.neo4j_driver = None
        self.redis_client = None
    
    async def connect_timescale(self):
        """Connect to TimescaleDB (PostgreSQL)"""
        # Railway provides DATABASE_URL
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            # Fallback to manual configuration
            host = os.getenv('TIMESCALE_HOST', 'localhost')
            port = os.getenv('TIMESCALE_PORT', '5432')
            db = os.getenv('TIMESCALE_DB', 'gimat')
            user = os.getenv('TIMESCALE_USER', 'gimat_user')
            password = os.getenv('TIMESCALE_PASSWORD', 'gimat_password')
            
            database_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
        else:
            # Railway gives postgres://, convert to asyncpg
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql+asyncpg://', 1)
        
        print(f"[DB] Connecting to TimescaleDB...")
        
        self.timescale_engine = create_async_engine(
            database_url,
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True
        )
        
        print("[DB] ✓ TimescaleDB connected")
        
        return self.timescale_engine
    
    async def connect_neo4j(self):
        """Connect to Neo4j"""
        # Railway Neo4j or custom
        neo4j_uri = os.getenv('NEO4J_URI')
        
        if not neo4j_uri:
            neo4j_uri = f"bolt://{os.getenv('NEO4J_HOST', 'localhost')}:7687"
        
        neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
        neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')
        
        print(f"[DB] Connecting to Neo4j at {neo4j_uri}...")
        
        self.neo4j_driver = AsyncGraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password),
            max_connection_pool_size=50
        )
        
        # Verify connection
        async with self.neo4j_driver.session() as session:
            result = await session.run("RETURN 1")
            await result.consume()
        
        print("[DB] ✓ Neo4j connected")
        
        return self.neo4j_driver
    
    async def connect_redis(self):
        """Connect to Redis"""
        # Railway provides REDIS_URL
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        
        print(f"[DB] Connecting to Redis...")
        
        self.redis_client = await aioredis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50
        )
        
        # Verify connection
        await self.redis_client.ping()
        
        print("[DB] ✓ Redis connected")
        
        return self.redis_client
    
    async def connect_all(self):
        """Connect to all databases"""
        await self.connect_timescale()
        await self.connect_neo4j()
        await self.connect_redis()
        
        print("[DB] ✓ All databases connected successfully")
    
    async def disconnect_all(self):
        """Disconnect from all databases"""
        if self.timescale_engine:
            await self.timescale_engine.dispose()
            print("[DB] TimescaleDB disconnected")
        
        if self.neo4j_driver:
            await self.neo4j_driver.close()
            print("[DB] Neo4j disconnected")
        
        if self.redis_client:
            await self.redis_client.close()
            print("[DB] Redis disconnected")
    
    def get_async_session(self):
        """Get async SQLAlchemy session factory"""
        if not self.timescale_engine:
            raise RuntimeError("TimescaleDB not connected")
        
        return sessionmaker(
            self.timescale_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )


# Global instance
db_manager = DatabaseManager()


# Dependency for FastAPI
async def get_db():
    """FastAPI dependency for database session"""
    async_session = db_manager.get_async_session()
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_neo4j():
    """FastAPI dependency for Neo4j session"""
    if not db_manager.neo4j_driver:
        raise RuntimeError("Neo4j not connected")
    
    async with db_manager.neo4j_driver.session() as session:
        yield session


async def get_redis():
    """FastAPI dependency for Redis client"""
    if not db_manager.redis_client:
        raise RuntimeError("Redis not connected")
    
    return db_manager.redis_client
