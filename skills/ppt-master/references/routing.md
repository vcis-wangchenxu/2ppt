# 路由兼容入口

正式路由 authority 已迁移到上游 6.6 同步文件：

- [workflows/routing.md](../workflows/routing.md)

本适配版只保留三个顶层 route：`generate`、`create-template`、`edit-native`。

历史名称 `fill-template` 与 `enhance` 都映射到 `edit-native`，不得再作为独立 route。
