# 版权与发行说明

本仓库是对 PPT Master 的 Codex 定向重构。

## 上游署名

- 原项目：PPT Master
- 原作者：Hugo He
- 原仓库：https://github.com/hugohe3/ppt-master
- 采用基线：`main@090a133040d9bf41dca887dab78386c553af5dc6`
- 原项目许可证：MIT

Copyright (c) 2025-2026 Hugo He

Codex 重构与发行维护：

Copyright (c) 2026 Chenxu Wang

完整许可条款见 [LICENSE](LICENSE)。本说明不替代许可证，发布本仓库的副本或实质性部分时，应同时保留版权声明和 MIT 许可文本。

## 非镜像声明

本仓库不是 `hugohe3/ppt-master` 的官方镜像，也不代表原作者发布。它保留 Generate、Create Template、Fill Native PPTX、Enhance Native PPTX 四个顶层 artifact routes；Generate 下的 Ordinary、Beautify、Image-to-PPTX 是 profiles，Default/Quick 是独立 mode。Create Template 的主产物是 Brand、Style、Layout 或 Deck 可复用工作区，而不是把来源原地改写为 PPTX。Codex 入口、工具映射、后备运行时、安装与验证流程均为重构实现。详细映射见 [UPSTREAM.md](UPSTREAM.md)。

## 未打包的第三方素材

本发行版不打包上游的大型第三方素材，包括但不限于：

- Tabler、Phosphor、Simple Icons、CHUNK 等图标集合；
- Kenney、BigSoundBank 等声音集合；
- Apache POI 的 DrawingML 预设几何数据；
- 上游示例 deck、截图、模板库和其他大型二进制资源。

因此，这些素材的许可证并不会因本仓库的安装而授予用户。仓库中的 `THIRD_PARTY_NOTICES.md` 仅存档上游来源链，便于未来在实际引入某项素材时重新审核；它不表示本发行版包含相应文件。

若未来加入第三方资源，维护者必须同时提交对应的许可证、署名、固定版本或 commit、来源链接及必要的完整性记录。

## 商标

PowerPoint、Microsoft、OpenAI、Codex 以及其他名称和标志可能属于各自权利人。本仓库对这些名称的描述性使用不构成官方认可、合作关系或商标许可。
