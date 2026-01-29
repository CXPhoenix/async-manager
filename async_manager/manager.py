import anyio
from typing import Callable, Awaitable, overload
from functools import partial, wraps
from contextlib import contextmanager

class AsyncManager:
    def __init__(self):
        self._limiter: dict[str, anyio.CapacityLimiter] = {}
    
    def regist_limiter(self, name: str, limiter: anyio.CapacityLimiter):
        self._limiter[name] = limiter
    
    def unregist_limiter(self, name: str):
        self._limiter.pop(name, None)
    
    def get_limiter(self, name: str) -> anyio.CapacityLimiter | None:
        return self._limiter.get(name, None)
    
    @contextmanager
    def create_limiter(self, name: str, max_worker: int):
        """
        Context manager 用於自動管理 limiter 生命週期
        
        Example:
            >>> manager = AsyncManager()
            >>> with manager.managed_limiter("docker", 10):
            >>>     # limiter 在這裡可用
            >>>     pass
        """
        limiter = anyio.CapacityLimiter(max_worker)
        self.regist_limiter(name, limiter)
        try:
            yield limiter
        finally:
            self.unregist_limiter(name)

    @overload
    def to_async[T, **P](self, func: Callable[P, T]) -> Callable[P, Awaitable[T]]:...

    @overload
    def to_async[T, **P](self, func: None = None, *, limiter: str) -> Callable[Callable[P, T], Callable[P, Awaitable[T]]]:...

    @overload
    def to_async[T, **P](self, func: None = None, *, limiter: anyio.CapacityLimiter) -> Callable[Callable[P, T], Callable[P, Awaitable[T]]]:...

    def to_async[T, **P](self, func: Callable[P, T] | None = None, *, limiter: str | anyio.CapacityLimiter | None = None):
        """
        將同步函式轉換為非同步函式
        
        Args:
            func: 要轉換的同步函式
            limiter: 可以是：
                    - None: 使用預設執行緒池（推薦）
                    - CapacityLimiter 物件: 直接使用該 limiter（推薦用於簡單場景）
                    - str: limiter 名稱（推薦用於 FastAPI，需先註冊）
        
        Examples:
            >>> # 方式一：無參數（最簡單）
            >>> @asynchronization
            >>> def sync_func():
            >>>     pass
            
            >>> # 方式二：傳遞 CapacityLimiter 物件（簡單場景）
            >>> limiter = CapacityLimiter(5)
            >>> @asynchronization(limiter=limiter)
            >>> def sync_func():
            >>>     pass
            
            >>> # 方式三：使用 limiter name（已有 limiter 環境，建議另外管理 name limiter，要提前註冊）
            >>> @asynchronization(limiter="docker")
            >>> def sync_func():
            >>>     pass
        """
        def decorator(f: Callable[P, T]) -> Callable[P, Awaitable[T]]:
            @wraps(f)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                actual_limiter: anyio.CapacityLimiter | None = None

                match limiter:
                    case str():
                        actual_limiter = self.get_limiter(limiter)
                        if actual_limiter is None:
                            raise RuntimeError(
                                f"Limiter {limiter} 尚未註冊！"
                            )
                    case anyio.CapacityLimiter():
                        actual_limiter = limiter
                    
                    case _:
                        actual_limiter = None
                
                return await anyio.to_thread.run_sync(
                    partial(f, *args, **kwargs),
                    limiter = actual_limiter,
                )
            
            return wrapper
        
        if func is not None:
            return decorator(func)
        return decorator


if __name__ == "__main__":
    import asyncio
    import time

    async_manager = AsyncManager()
    
    @async_manager.to_async
    def hello(wait: int | float = 1) -> None:
        time.sleep(wait)
        print(f"After {wait} sleep..., Hello World!")

    async def main():
        await asyncio.gather(
            hello(2),
            hello(0.8),
            hello(1)
        )

    asyncio.run(main())
