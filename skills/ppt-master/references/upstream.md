# 上游来源与重构边界

本 Skill 基于 [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) 的工作流思想重构。

- 上游固定基线：`main@090a133040d9bf41dca887dab78386c553af5dc6`
- 上游版本：`4.7.0`
- 上游作者：Hugo He
- 上游许可证：MIT
- Codex 适配仓库：https://github.com/vcis-wangchenxu/2ppt

本发行版不是上游仓库的镜像，也没有复制其大型示例、图标、声音、模板库或完整 Python 转换器。它重新实现了 Codex 原生入口、四路由决策、工具映射、确定性 JSON→PPTX 后备运行时、验证脚本和安装流程。

必须保留本文件与 Skill 根目录的 `LICENSE`。运行 `python scripts/verify_attribution.py` 可验证来源信息是否完整。
