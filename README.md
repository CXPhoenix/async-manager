<div align="center">
  <h1 style="margin-top: 10px;">Async Manager</h1>

  <h2>讓同步函式在非同步環境中優雅運行的最佳助手</h2>

  <p>
    <a href="#features">功能特色</a>
    ◆ <a href="#quick-start">快速開始</a>
    ◆ <a href="#installation">安裝指南</a>
    ◆ <a href="docs/api.md">API 文件</a>
  </p>
</div>

## 簡介 🎯

**Async Manager** 是一個專為 Python 非同步應用程式（如 FastAPI）設計的輕量級套件。它封裝了 `anyio` 的底層細節，提供簡單易用的裝飾器 (Decorator)，讓你能夠輕鬆地將同步函式 (Synchronous Functions) 整合進非同步 (Asynchronous) 流程中，而不會阻塞 Event Loop。

特別適用於：
- 在 `FastAPI` 中執行耗時的 CPU 密集型運算。
- 在 `AnyIO` 環境中呼叫傳統的同步 IO 函式庫（如 `requests`, `pandas`, `SQLAlchemy` Core）。
- 需要精細控制執行緒池 (Thread Pool) 並發數量 (Capacity Limiter) 的場景。

## 功能特色 ✨

- **🚀 簡單易用**：只要加上 `@to_async` 裝飾器，立刻讓同步函式變成 Awaitable。
- **🛡️ 資源控管**：支援 `CapacityLimiter`，防止過多並發耗盡系統資源。
- **📦 生命週期管理**：提供 Context Manager (`create_limiter`) 自動註冊與清理 Limiter，避免記憶體洩漏。
- **🔧 靈活整合**：可直接使用名稱字串 (String) 參照 Limiter，方便與依賴注入 (Dependency Injection) 系統整合。

## 安裝指南 📦

使用 `pip` 或 `uv` 安裝：

```bash
uv add async-manager
# 或
pip install async-manager
```

## 快速開始 ⚡

### 基礎範例

最簡單的用法，直接將同步函式轉為非同步：

```python
import time
import asyncio
from async_manager import to_async

# 原始的同步函式 (會阻塞)
@to_async
def slow_task(duration: float):
    print(f"Starting task for {duration}s")
    time.sleep(duration)
    return "Done"

async def main():
    # 現在它是 awaitable 的了！且在獨立 Thread 中執行
    await slow_task(1.0)

if __name__ == "__main__":
    asyncio.run(main())
```

### 使用 Capacity Limiter

限制同時執行的任務數量，保護你的資源：

```python
from async_manager import AsyncManager

manager = AsyncManager()

# 使用 Context Manager 建立一個名為 "db_pool" 的 limiter，限制最大 5 個並發
with manager.create_limiter("db_pool", max_worker=5):
    
    # 指定使用這個 limiter
    @manager.to_async(limiter="db_pool")
    def heavy_db_query():
        # ... database operations ...
        pass

    # 在這個區塊內呼叫 heavy_db_query 都會受到並發限制
```

## 文件索引 📚

- **[API 參考文件](docs/api.md)**：詳細的類別與函式說明。
- **[使用指南](docs/usage.md)**：進階範例、FastAPI 整合教學與最佳實踐。

## 授權 📄

本專案採用 **Educational Community License v2.0 (ECL-2.0)** 授權 - 詳情請參閱 [LICENSE](LICENSE) 檔案。
