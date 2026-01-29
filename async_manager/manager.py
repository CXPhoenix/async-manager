import anyio
from typing import Callable, Awaitable, overload
from functools import partial, wraps
from contextlib import contextmanager

class AsyncManager:
    """
    非同步管理器 (Async Manager) 用於管理並發限制 (Concurrency Limits) 與同步函式轉換。
    
    這個類別維護了一組命名的 `CapacityLimiter`，並提供裝飾器將同步函式轉換為
    在 Thread Pool 中運行的非同步函式 (Awaitable)。
    """
    def __init__(self):
        """
        初始化 AsyncManager。
        建立一個空的 limiter 儲存庫。
        """
        self._limiter: dict[str, anyio.CapacityLimiter] = {}
    
    def regist_limiter(self, name: str, limiter: anyio.CapacityLimiter):
        """
        註冊一個命名的 CapacityLimiter。

        Args:
            name: Limiter 的名稱 (ID)。
            limiter: anyio.CapacityLimiter 實例。
        """
        self._limiter[name] = limiter
    
    def unregist_limiter(self, name: str):
        """
        取消註冊 (移除) 指定名稱的 CapacityLimiter。

        Args:
            name: 要移除的 Limiter 名稱。
        """
        self._limiter.pop(name, None)
    
    def get_limiter(self, name: str) -> anyio.CapacityLimiter | None:
        """
        取得指定名稱的 CapacityLimiter。

        Args:
            name: Limiter 名稱。

        Returns:
            CapacityLimiter | None: 如果找到則回傳實例，否則回傳 None。
        """
        return self._limiter.get(name, None)
    
    @contextmanager
    def create_limiter(self, name: str, max_worker: int):
        """
        建立並管理一個 Limiter 生命週期的 Context Manager。
        
        當進入 context 時註冊 limiter，離開時自動取消註冊。
        
        Args:
            name: Limiter 名稱。
            max_worker: 最大並發工作數。
        
        Yields:
             anyio.CapacityLimiter: 建立的 limiter 實例。
        
        Example:
            >>> manager = AsyncManager()
            >>> with manager.create_limiter("docker", 10):
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
            >>> @to_async
            >>> def sync_func():
            >>>     pass
            
            >>> # 方式二：傳遞 CapacityLimiter 物件（簡單場景）
            >>> limiter = CapacityLimiter(5)
            >>> @to_async(limiter=limiter)
            >>> def sync_func():
            >>>     pass
            
            >>> # 方式三：使用 limiter name（已有 limiter 環境，建議另外管理 name limiter，要提前註冊）
            >>> @to_async(limiter="docker")
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
