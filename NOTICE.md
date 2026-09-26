# NOTICE

本仓库包含对 PPT Master 的 Codex-native 适配。

Upstream:
- PPT Master
- Copyright (c) 2025-2026 Hugo He
- https://github.com/hugohe3/ppt-master
- MIT License

Adaptation:
- https://github.com/vcis-wangchenxu/2ppt

本仓库不是上游官方镜像。当前固定审计/同步基线为 v6.6.0 (a50758ac29ec027e85966db33e2ae80031446756)。

顶层 artifact lifecycle 已按上游 6.6 统一为 Generate PPTX、Create Template、Edit Native PPTX；历史 Fill Native PPTX 与 Enhance Native PPTX 作为 edit-native 兼容入口。

为适配 Codex，本仓库保留自己的 SKILL.md、显式调用策略、运行时映射、安装器、验证器与轻量 JSON builder，并选择性排除大型示例/比较图、brand/icon/sound 资产包。
