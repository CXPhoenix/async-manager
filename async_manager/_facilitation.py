from .manager import AsyncManager

module_manager = AsyncManager()
to_async = module_manager.to_async
regist_limiter = module_manager.regist_limiter
unregist_limiter = module_manager.unregist_limiter
create_limiter = module_manager.create_limiter