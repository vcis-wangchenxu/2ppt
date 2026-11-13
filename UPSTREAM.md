# 上游来源与同步策略

本仓库基于 [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) 的公开实现，面向 Codex 做选择性集成。

- 固定版本：`v6.9.0`
- 固定提交：`ce92fb43e4ade9c701f4c869e286f13fce743c72`
- 上游作者：Hugo He
- 上游许可证：MIT
- 本仓库：`vcis-wangchenxu/2ppt`

截至 2026-11-13，已核对 [v6.9.0 发布说明](https://github.com/hugohe3/ppt-master/releases/tag/v6.9.0)。本次包含 6.7–6.9 的原生编辑/图表/公式保真、转换源文件防覆盖、OCR 文本证据、图片图层配准和规格评审更新。发布包 SHA-256：`5ac7bf511b1bbaf3809b9fb3d8465918f79ca39b5451203c9eb9e08763acd873`。

同步包含 6.9 的三路由体系、Generate profiles、Edit Native round-trip、Plan/Executor ownership、semantic vocabulary selection、Relationships/topology、text measurement、native charts/tables/formulas/hyperlinks、Master/Layout/slots、Create Template、template apply、source conversion、image composition、Revision Round、visual QA、animations/transitions/narration runtime 与安全修复。

Codex 改造：仅显式 `$ppt-master` 调用；Codex Presentations/Web/ImageGen 优先；provider-specific image/web scripts 作 fallback；保留 lightweight JSON builder；`fill-template` / `enhance` 合并为 `edit-native`；不 vendoring 上游巨量视觉比较素材、brands/icons/sounds。

`tools/sync_ppt_master.py` 仅接受固定提交的干净 checkout，或 SHA-256 匹配的官方发布 ZIP。每个同步文件的 SHA-256 都记录在 `UPSTREAM_MANIFEST.json`，重复同步可复现且不覆盖 Codex 控制层。未来升级需同时更新版本、提交、发布包校验值与回归测试；不会自动跟随上游 main。
