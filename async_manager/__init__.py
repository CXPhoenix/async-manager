"""
Async Manager
=============

一個輕量級的 anyio 包裝器，用於將同步函式無縫整合到非同步工作流中。

主要功能：
- `to_async`: 將同步函式轉換為 Awaitable。
- `CapacityLimiter`: 支援精細的並發控制。
- `AsyncManager`: 管理多個 Limiter。

使用範例:
    >>> from async_manager import to_async
    >>> @to_async
    >>> def sync_job():
    >>>     pass
"""
from .manager import AsyncManager
from ._facilitation import to_async, regist_limiter, unregist_limiter, create_limiter

__all__ = [
    AsyncManager,
    to_async,
    regist_limiter,
    unregist_limiter,
    create_limiter,
]
