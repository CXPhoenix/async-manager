# API 參考文件 📚

本文件詳細說明 `async_manager` 套件的核心 API。

## AsyncManager 類別

核心管理器，負責管理 Capacity Limiter 並提供轉換裝飾器。

```python
from async_manager import AsyncManager
manager = AsyncManager()
```

### 方法 (Methods)

#### `to_async`

將同步函式 (Synchronous Function) 轉換為非同步函式 (Asynchronous Function) 的裝飾器。

**定義：**

```python
def to_async(
    self, 
    func: Callable[P, T] | None = None, 
    *, 
    limiter: str | anyio.CapacityLimiter | None = None
) -> Callable[..., Awaitable[T]]
```

**參數：**

| 參數名稱 | 類型 | 說明 |
|----------|------|------|
| `func` | `Callable` | 要被裝飾的同步函式。 |
| `limiter` | `str` \| `CapacityLimiter` \| `None` | (選用) 用於限制並發數量的 Limiter。<br> - `None`: 使用預設執行緒池。<br> - `CapacityLimiter`: 直接使用傳入的 Limiter 物件。<br> - `str`: 使用已註冊的 Limiter 名稱。 |

**使用範例：**

```python
@manager.to_async
def heavy_task():
    # 執行耗時操作
    pass

@manager.to_async(limiter="db_pool")
def db_query():
    # 使用名為 "db_pool" 的 limiter
    pass
```

#### `regist_limiter`

註冊一個命名的 Capacity Limiter。

**定義：**

```python
def regist_limiter(self, name: str, limiter: anyio.CapacityLimiter)
```

**參數：**

| 參數名稱 | 類型 | 說明 |
|----------|------|------|
| `name` | `str` | Limiter 的識別名稱。 |
| `limiter` | `anyio.CapacityLimiter` | AnyIO 的 CapacityLimiter 實例。 |

#### `create_limiter` (Context Manager)

建立並自動管理 Limiter 生命週期的 Context Manager。當離開 Context 時，會自動取消註冊。

**定義：**

```python
@contextmanager
def create_limiter(self, name: str, max_worker: int)
```

**參數：**

| 參數名稱 | 類型 | 說明 |
|----------|------|------|
| `name` | `str` | Limiter 的識別名稱。 |
| `max_worker` | `int` | 最大並發工作數 (Maximum Concurrent Workers)。 |

**使用範例：**

```python
with manager.create_limiter("api_calls", max_worker=5) as limiter:
    # 在此區塊內，"api_calls" limiter 可用
    pass
# 離開區塊後，"api_calls" limiter 自動移除
```

#### `get_limiter`

取得已註冊的 Limiter。

**定義：**

```python
def get_limiter(self, name: str) -> anyio.CapacityLimiter | None
```

## 模組層級別名 (Module Aliases)

為了方便使用，`async_manager` 預設實例化了一個全域的 `AsyncManager` 並匯出了常用函式：

- `async_manager.to_async`
- `async_manager.regist_limiter`
- `async_manager.unregist_limiter`
- `async_manager.create_limiter`

這意味著你可以直接從模組匯入使用，而不需要自己建立實例（除非你需要隔離的環境）。

```python
from async_manager import to_async, create_limiter
```
