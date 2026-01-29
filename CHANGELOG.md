# 更新日誌

本專案的所有重大變更都將記錄在此文件中。

格式基於 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，
並遵守 [Semantic Versioning](https://semver.org/spec/v2.0.0.html) 規範。

## [0.1.0] - 2026-01-29

### 新增
- Async Manager 首次發布。
- 新增 `to_async` 裝飾器 (Decorator)，可將同步函式 (Synchronous Functions) 轉換為非同步函式 (Asynchronous Functions)。
- 新增 `AsyncManager` 類別，負責管理 Capacity Limiter。
- 支援使用 `CapacityLimiter` 進行並發控制 (Concurrency Control)。
- 支援 Context Manager，可透過 `create_limiter` 自動管理 Limiter 生命週期。
- 提供 `regist_limiter`、`unregist_limiter`、`get_limiter` 等輔助函式。
