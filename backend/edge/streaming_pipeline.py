"""
Streaming Data Pipeline with Message Queue
"""

import asyncio
from typing import Dict, Callable, Optional
import json


class StreamingPipeline:
    """
    Async streaming pipeline for real-time data
    Supports Kafka, RabbitMQ, or Redis Streams
    """
    
    def __init__(self, backend: str = "redis", connection_params: Optional[Dict] = None):
        """
        Initialize streaming pipeline
        
        Args:
            backend: 'kafka', 'rabbitmq', or 'redis'
            connection_params: Connection parameters
        """
        self.backend = backend
        self.connection_params = connection_params or {}
        self.handlers = {}
        
        if backend == "redis":
            try:
                import redis.asyncio as aioredis
                self.client = None  # Initialize on connect
            except ImportError:
                print("redis package not installed, using mock")
                self.client = None
        
        elif backend == "kafka":
            # aiokafka integration
            print("Kafka backend: aiokafka integration placeholder")
            self.client = None
        
        else:
            print(f"Backend {backend} not fully implemented, using mock")
            self.client = None
    
    async def connect(self):
        """Connect to message queue"""
        if self.backend == "redis" and self.client is None:
            try:
                import redis.asyncio as aioredis
                self.client = await aioredis.from_url(
                    self.connection_params.get('url', 'redis://localhost'),
                    encoding="utf-8",
                    decode_responses=True
                )
                print("Connected to Redis")
            except Exception as e:
                print(f"Redis connection failed: {e}")
    
    async def publish(self, topic: str, message: Dict):
        """
        Publish message to topic
        
        Args:
            topic: Topic/channel name
            message: Message dict
        """
        if self.client:
            await self.client.publish(topic, json.dumps(message))
        else:
            # Mock
            print(f"[PUBLISH] {topic}: {message}")
    
    async def subscribe(self, topic: str, handler: Callable):
        """
        Subscribe to topic with handler
        
        Args:
            topic: Topic name
            handler: Async function to handle messages
        """
        self.handlers[topic] = handler
        
        if self.client:
            pubsub = self.client.pubsub()
            await pubsub.subscribe(topic)
            
            print(f"Subscribed to {topic}")
            
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    data = json.loads(message['data'])
                    await handler(data)
        else:
            print(f"[SUBSCRIBE] {topic} with handler {handler.__name__}")
    
    async def stream_observations(self, processor_func: Callable):
        """
        Stream observations in real-time
        
        Args:
            processor_func: Function to process each observation
        """
        async def handle_observation(data: Dict):
            processed = await processor_func(data)
            # Forward to next stage
            await self.publish('processed_observations', processed)
        
        await self.subscribe('raw_observations', handle_observation)
    
    async def close(self):
        """Close connection"""
        if self.client:
            await self.client.close()


# ==========================================
# Edge to Cloud Gateway
# ==========================================

class EdgeCloudGateway:
    """
    Gateway between edge devices and cloud backend
    """
    
    def __init__(self, pipeline: StreamingPipeline):
        self.pipeline = pipeline
    
    async def forward_from_edge(self, edge_data: Dict):
        """
        Receive data from edge and forward to cloud
        
        Args:
            edge_data: Data from edge device
        """
        # Validate
        if not self._validate_edge_data(edge_data):
            print(f"Invalid edge data: {edge_data}")
            return
        
        # Forward to cloud processing
        await self.pipeline.publish('edge_observations', edge_data)
    
    def _validate_edge_data(self, data: Dict) -> bool:
        """Validate edge data format"""
        required_fields = ['station_id', 'timestamp', 'value']
        return all(field in data for field in required_fields)
    
    async def sync_configuration(self, edge_device_id: str) -> Dict:
        """
        Sync configuration to edge device
        
        Args:
            edge_device_id: Edge device identifier
        
        Returns:
            Configuration dict
        """
        # Placeholder - would fetch from database
        config = {
            'device_id': edge_device_id,
            'sampling_interval': 300,  # 5 minutes
            'wavelet': 'db4',
            'buffer_size': 50
        }
        
        return config
