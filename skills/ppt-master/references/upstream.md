# 上游来源

- 上游：https://github.com/hugohe3/ppt-master
- 固定同步版本：v6.9.0
- 固定提交：ce92fb43e4ade9c701f4c869e286f13fce743c72
- 原作者：Hugo He
- 上游许可证：MIT
- Codex 适配仓库：https://github.com/vcis-wangchenxu/2ppt

本仓库不是官方镜像。`tools/sync_ppt_master.py` 选择性同步 6.9 的核心 workflows、references、runtime scripts 与轻量模板库，同时保留自己的 `SKILL.md`、Codex runtime、项目契约、质量门禁、安装器和 JSON fallback。

为避免无谓体积，本适配默认不 vendoring `references/ai-image-comparison/`、`templates/brands/`、`templates/icons/`、`templates/sounds/`。这些缺失资产不得伪造；需要时优先使用用户素材或 Codex 原生 Web/ImageGen。
