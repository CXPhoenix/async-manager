# Async Manager

`async_manager` 是一個用於管理非同步執行與並發限制的 Python 工具庫。它基於 `anyio` 構建，提供了將同步函式轉換為非同步函式的裝飾器，並支持精細的並發控制（Capacity Limiting）。

## 特性

- **同步轉非同步**：輕鬆將阻塞的同步函式轉換為非同步 awaitable 函式。
- **並發限制 (Concurrency Limiting)**：使用 `anyio.CapacityLimiter` 防止過多執行緒同時運行。
- **靈活的 Limiter 管理**：支持直接傳遞 Limiter 物件或使用名稱註冊/查找 Limiter。
- **Context Manager 支持**：自動管理 Limiter 的生命週期。

## 安裝

此模組為專案內部庫，請確保已安裝依賴：

```bash
pip install anyio
```

## 核心組件

### `AsyncManager` 類別

核心管理類別，負責 Limiter 的註冊與查找，以及提供裝飾器。

```python
from async_manager import AsyncManager

manager = AsyncManager()
```

### 全域便捷函式

為了方便使用，`async_manager` 模組導出了一個預設的 `AsyncManager` 實例的方法：

- `to_async`
- `regist_limiter`
- `unregist_limiter`
- `create_limiter`

你可以直接從 `async_manager` 導入使用。

```python
from async_manager import to_async, regist_limiter
```

## 使用指南

### 1. 基本用法：轉換同步函式

最簡單的用法是不帶參數直接使用 `@to_async`。這會將函式放入預設的執行緒池中執行。

```python
import time
import asyncio
from async_manager import to_async

@to_async
def heavy_computation(x):
    time.sleep(1) # 模擬阻塞操作
    return x * x

async def main():
    result = await heavy_computation(10)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. 並發限制 (Limiter)

你可以限制特定函式的同時執行數量。

#### 方法 A：直接傳遞 `CapacityLimiter` 物件 (推薦用於簡單腳本)

```python
from anyio import CapacityLimiter
from async_manager import to_async

# 限制同時只能有 2 個執行緒執行此函式
limiter = CapacityLimiter(2)

@to_async(limiter=limiter)
def limited_task(n):
    # ...
    pass
```

#### 方法 B：使用 Limiter 名稱 (推薦用於大型應用/FastAPI)

在大型應用中，定義與使用通常是分離的。你可以先註冊一個 Limiter，然後在裝飾器中引用其名稱。

```python
from async_manager import AsyncManager, to_async
from anyio import CapacityLimiter

manager = AsyncManager()

# 1. 註冊 Limiter
manager.regist_limiter("db_pool", CapacityLimiter(5))

# 2. 使用名稱引用
@manager.to_async(limiter="db_pool")
def db_operation():
    # 最多同時 5 個併發
    pass
```

> **注意**：如果使用名稱引用，該名稱必須在呼叫函式之前被註冊，否則執行時會拋出 `RuntimeError`。

### 3. 動態 Limiter 管理

使用 `create_limiter` context manager 可以自動註冊與註銷 Limiter，適合臨時性的並發控制。

```python
from async_manager import AsyncManager

manager = AsyncManager()

# 在這個區塊內，"temp_pool" limiter 是有效的
with manager.create_limiter("temp_pool", max_worker=3):
    
    @manager.to_async(limiter="temp_pool")
    def job():
        pass
        
    # 執行任務...
    
# 離開區塊後，"temp_pool" 會被自動移除
```

## API 參考

### `AsyncManager` 方法

- **`regist_limiter(name: str, limiter: anyio.CapacityLimiter)`**
  註冊一個命名 limiter。

- **`unregist_limiter(name: str)`**
  移除一個命名 limiter。

- **`get_limiter(name: str) -> anyio.CapacityLimiter | None`**
  獲取指定名稱的 limiter。

- **`create_limiter(name: str, max_worker: int)`**
  Context manager，用於創建並自動管理 limiter 生命週期。

- **`to_async(func=None, *, limiter=None)`**
  裝飾器。
    - `func`: 目標同步函式。
    - `limiter`: 
        - `None`: 使用預設機制。
        - `capacityLimiter`: 直接使用此實例。
        - `str`: 使用已註冊的 limiter 名稱。
