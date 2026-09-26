# 上游来源与同步策略

本仓库基于 [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) 的公开实现，面向 Codex 做选择性集成。

- 固定版本：`v6.6.0`
- 固定提交：`a50758ac29ec027e85966db33e2ae80031446756`
- 上游作者：Hugo He
- 上游许可证：MIT
- 本仓库：`vcis-wangchenxu/2ppt`

同步包含 6.6 的三路由体系、Generate profiles、Edit Native round-trip、Plan/Executor ownership、semantic vocabulary selection、Relationships/topology、text measurement、native charts/tables/formulas/hyperlinks、Master/Layout/slots、Create Template、template apply、source conversion、image composition、Revision Round、visual QA、animations/transitions/narration runtime 与安全修复。

Codex 改造：仅显式 `$ppt-master` 调用；Codex Presentations/Web/ImageGen 优先；provider-specific image/web scripts 作 fallback；保留 lightweight JSON builder；`fill-template` / `enhance` 合并为 `edit-native`；不 vendoring 上游巨量视觉比较素材、brands/icons/sounds。

`tools/sync_ppt_master.py` 从固定 tag checkout 中复制审计后的 runtime subset，并写 `UPSTREAM_MANIFEST.json`。由于上游 v5.0 重写过 Git 历史，本仓库不尝试把旧 4.7 基线与 6.6 做 Git merge。
