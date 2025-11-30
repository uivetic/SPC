"""Redis cache service for Google Sheets data"""
import json
from typing import Optional, Any
from app.config import settings
import asyncio

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None


class CacheService:
    """Service for caching Google Sheets data using Redis"""
    
    def __init__(self):
        self._redis_client: Optional[redis.Redis] = None
        self._enabled = REDIS_AVAILABLE and settings.REDIS_URL is not None
    
    async def _get_client(self) -> Optional[redis.Redis]:
        """Get or initialize Redis client"""
        if not self._enabled:
            return None
        
        if self._redis_client is None and settings.REDIS_URL:
            try:
                self._redis_client = await redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True
                )
            except Exception as e:
                print(f"Redis connection failed: {e}")
                self._enabled = False
                return None
        
        return self._redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self._enabled:
            return None
        
        client = await self._get_client()
        if not client:
            return None
        
        try:
            value = await client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        if not self._enabled:
            return False
        
        client = await self._get_client()
        if not client:
            return False
        
        try:
            ttl = ttl or settings.CACHE_TTL_SECONDS
            await client.setex(
                key,
                ttl,
                json.dumps(value)
            )
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self._enabled:
            return False
        
        client = await self._get_client()
        if not client:
            return False
        
        try:
            await client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern"""
        if not self._enabled:
            return 0
        
        client = await self._get_client()
        if not client:
            return 0
        
        try:
            keys = await client.keys(pattern)
            if keys:
                return await client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache invalidate error: {e}")
            return 0
    
    async def close(self):
        """Close Redis connection"""
        if self._redis_client:
            await self._redis_client.close()
            self._redis_client = None


# Global cache service instance
cache_service = CacheService()

