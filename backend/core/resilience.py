"""
GAAIUS Resilience & Integration Patterns
Circuit breakers, retry logic, timeouts, graceful degradation
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Callable, Any, TypeVar, Dict
from enum import Enum
import time

import aiohttp

from backend.core.exceptions import (
    RequestTimeoutError, RateLimitError, ExternalServiceError, ErrorCode
)
from backend.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

T = TypeVar('T')


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failure mode - rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker pattern for external service calls
    Prevents cascading failures by stopping requests to failing services
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout_seconds: int = 60,
        expected_exception: type = Exception
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker '{self.name}' entering HALF_OPEN state")
            else:
                raise ExternalServiceError(
                    message=f"Circuit breaker '{self.name}' is OPEN",
                    service_name=self.name
                )
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.success_count = 0
            logger.info(f"Circuit breaker '{self.name}' recovered - state CLOSED")
        self.success_count += 1
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(f"Circuit breaker '{self.name}' OPEN after {self.failure_count} failures")
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery"""
        if not self.last_failure_time:
            return False
        
        elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout_seconds


class RetryPolicy:
    """
    Retry policy with exponential backoff
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 1.5,
        initial_delay_ms: int = 100,
        max_delay_ms: int = 10000
    ):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.initial_delay_ms = initial_delay_ms
        self.max_delay_ms = max_delay_ms
    
    async def execute(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with retry logic
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If all retries exhausted
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt >= self.max_retries:
                    logger.error(f"All retries exhausted: {str(e)}")
                    raise
                
                delay_ms = min(
                    self.initial_delay_ms * (self.backoff_factor ** attempt),
                    self.max_delay_ms
                )
                
                logger.warning(
                    f"Retry attempt {attempt + 1}/{self.max_retries} "
                    f"after {delay_ms}ms - {str(e)}"
                )
                
                await asyncio.sleep(delay_ms / 1000)
        
        raise last_exception


class ResilientHTTPClient:
    """
    HTTP client with built-in resilience patterns
    Includes timeouts, retries, circuit breaker, rate limiting
    """
    
    def __init__(
        self,
        name: str,
        timeout_seconds: int = 30,
        max_retries: int = 3,
        rate_limit_per_minute: int = 60
    ):
        self.name = name
        self.timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Resilience patterns
        self.circuit_breaker = CircuitBreaker(
            name=name,
            failure_threshold=5,
            recovery_timeout_seconds=60
        )
        self.retry_policy = RetryPolicy(max_retries=max_retries)
        
        # Rate limiting
        self.rate_limit_per_minute = rate_limit_per_minute
        self.request_times: Dict[str, list] = {}
    
    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get(
        self,
        url: str,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        GET request with resilience
        
        Args:
            url: Request URL
            headers: Request headers
            **kwargs: Additional aiohttp arguments
            
        Returns:
            JSON response
            
        Raises:
            RequestTimeoutError: If request times out
            RateLimitError: If rate limit exceeded
        """
        return await self._request("GET", url, headers=headers, **kwargs)
    
    async def post(
        self,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        POST request with resilience
        
        Args:
            url: Request URL
            data: Form data
            json: JSON data
            headers: Request headers
            **kwargs: Additional aiohttp arguments
            
        Returns:
            JSON response
        """
        return await self._request(
            "POST",
            url,
            data=data,
            json=json,
            headers=headers,
            **kwargs
        )
    
    async def _request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute HTTP request with all resilience patterns
        
        Args:
            method: HTTP method
            url: Request URL
            **kwargs: aiohttp arguments
            
        Returns:
            JSON response
        """
        # Check rate limit
        self._check_rate_limit()
        
        async def _do_request():
            if not self.session:
                raise ExternalServiceError(
                    message="HTTP client not initialized",
                    service_name=self.name
                )
            
            try:
                async with self.session.request(method, url, **kwargs) as resp:
                    # Check for rate limit response
                    if resp.status == 429:
                        retry_after = int(resp.headers.get('Retry-After', 60))
                        raise RateLimitError(
                            message=f"{self.name} rate limit exceeded",
                            retry_after_seconds=retry_after
                        )
                    
                    resp.raise_for_status()
                    
                    if resp.content_type == 'application/json':
                        return await resp.json()
                    else:
                        return {"text": await resp.text()}
                        
            except asyncio.TimeoutError as e:
                raise RequestTimeoutError(
                    message=f"Request to {self.name} timed out",
                    timeout_seconds=self.timeout.total,
                    cause=e
                )
        
        # Execute with circuit breaker and retries
        return await self.circuit_breaker.call(
            lambda: self.retry_policy.execute(_do_request)
        )
    
    def _check_rate_limit(self):
        """Check if rate limit is exceeded"""
        identifier = self.name
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        if identifier not in self.request_times:
            self.request_times[identifier] = []
        
        self.request_times[identifier] = [
            t for t in self.request_times[identifier]
            if t > minute_ago
        ]
        
        # Check limit
        if len(self.request_times[identifier]) >= self.rate_limit_per_minute:
            raise RateLimitError(
                message=f"Rate limit exceeded for {self.name}",
                retry_after_seconds=60
            )
        
        self.request_times[identifier].append(now)


class HealthCheck:
    """Health check manager for services"""
    
    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.last_results: Dict[str, bool] = {}
    
    def register(self, service_name: str, check_func: Callable):
        """Register a health check"""
        self.checks[service_name] = check_func
    
    async def check_all(self) -> Dict[str, bool]:
        """Run all health checks"""
        results = {}
        for service_name, check_func in self.checks.items():
            try:
                results[service_name] = await asyncio.wait_for(check_func(), timeout=5)
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {e}")
                results[service_name] = False
        
        self.last_results = results
        return results
    
    async def check_service(self, service_name: str) -> bool:
        """Check single service"""
        if service_name not in self.checks:
            raise ValueError(f"Service {service_name} not registered")
        
        try:
            result = await asyncio.wait_for(
                self.checks[service_name](),
                timeout=5
            )
            self.last_results[service_name] = result
            return result
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            self.last_results[service_name] = False
            return False
    
    def is_healthy(self) -> bool:
        """Check if all registered services are healthy"""
        return all(self.last_results.values()) if self.last_results else False
