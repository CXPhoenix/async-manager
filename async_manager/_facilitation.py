"""
此模組提供了全域預設的 AsyncManager 實例及其便捷函式 (Facilitation Functions)。

使用這些函式可以直接操作一個全域共用的 AsyncManager，而無需自行實例化。
"""
from .manager import AsyncManager

module_manager = AsyncManager()
to_async = module_manager.to_async
regist_limiter = module_manager.regist_limiter
unregist_limiter = module_manager.unregist_limiter
create_limiter = module_manager.create_limiter