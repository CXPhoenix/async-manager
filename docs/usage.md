# 使用指南 (Usage Guide) 📖

本指南提供 `async_manager` 的常見使用情境與最佳實踐。

## 基礎入門

### 為什麼需要 Async Manager？

在 Python 的非同步程式設計（如 FastAPI, AnyIO）中，直接呼叫同步的 IO 密集型函式（如 `requests`, `pandas` 處理）會阻塞 Event Loop，導致效能低落。

`async_manager` 封裝了 `anyio.to_thread.run_sync`，讓你透過簡單的裝飾器 `@to_async` 將同步函式轉換為非同步函式，並丟入 Thread Pool 執行。

### 基本範例

```python
import time
import asyncio
from async_manager import to_async

# 1. 將同步函式轉為非同步
@to_async
def blocking_task(name: str, seconds: float):
    print(f"[{name}] Task started...")
    time.sleep(seconds)  # 模擬阻塞操作
    print(f"[{name}] Task finished!")
    return f"Result for {name}"

async def main():
    # 2. 像呼叫一般 async 函式一樣呼叫它
    print("Main start")
    
    # 平行執行
    results = await asyncio.gather(
        blocking_task("Task A", 2.0),
        blocking_task("Task B", 1.0)
    )
    
    print(results)

if __name__ == "__main__":
    asyncio.run(main())
```

## 進階使用

### 限制並發數量 (Rate Limiting)

當你需要限制同時執行的任務數量（例如：避免資料庫連線過多，或是避免打爆外部 API），可以使用 `CapacityLimiter`。

#### 方法一：使用 Context Manager (推薦)

```python
from async_manager import AsyncManager, to_async

manager = AsyncManager()

# 定義需要限制的任務
@manager.to_async(limiter="external_api")
def call_api(url):
    # ... call api ...
    pass

async def main():
    # 建立一個最多允許 5 個並發的 limiter
    with manager.create_limiter("external_api", max_worker=5):
        # 這裡發出的請求最多只有 5 個會同時執行
        tasks = [call_api(f"https://api.example.com/{i}") for i in range(20)]
        await asyncio.gather(*tasks)
```

#### 方法二：全域註冊

適用於 FastAPI 等應用程式啟動時。

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from async_manager import regist_limiter, unregist_limiter, to_async
from anyio import CapacityLimiter

@to_async(limiter="heavy_ops")
def heavy_processing():
    pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 應用程式啟動時註冊
    regist_limiter("heavy_ops", CapacityLimiter(3))
    yield
    # 關閉時清理 (非必要，但好習慣)
    unregist_limiter("heavy_ops")

app = FastAPI(lifespan=lifespan)
```

### 與 FastAPI 整合

在 FastAPI 中，雖然可以定義 `def path_operation():` 來執行同步程式碼，但 FastAPI 預設會為每個請求開啟一個新的 thread。如果請求量大，可能會導致 thread 數量暴增。

使用 `async_manager` 可以更精細地控制 Thread Pool 的使用。

```python
from fastapi import FastAPI
from async_manager import to_async

app = FastAPI()

@to_async
def cpu_bound_task(data: list):
    # 複雜運算
    return sum(data)

@app.post("/compute")
async def compute(data: list[int]):
    # 轉交給 thread pool 執行，不阻塞 main event loop
    result = await cpu_bound_task(data)
    return {"sum": result}
```

## 常見問題

### Q: 什麼時候該用 `None` (預設 Limiter)？
A: 對於一般的阻塞操作（如寫入 log 檔案、簡單的資料處理），使用預設的 Thread Pool 即可。

### Q: 什麼時候該用自定義 Limiter？
A: 
1. **保護資源**：如資料庫連線池有限、外部 API 有 Rate Limit 限制。
2. **隔離資源**：避免某個耗時的任務佔用掉所有 Thread，導致其他輕量任務無法執行。

---
更多 API 細節請參考 [API 文件](api.md)。
