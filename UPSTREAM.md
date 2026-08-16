# 上游来源与重构说明

本仓库基于 [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) 的公开工作流与实现经验，面向 Codex 重新设计。

- 上游仓库：`hugohe3/ppt-master`
- 固定基线：`main@090a133040d9bf41dca887dab78386c553af5dc6`
- 上游版本：`4.7.0`
- 上游作者：Hugo He
- 上游许可证：MIT
- 本仓库：`vcis-wangchenxu/2ppt`

## 性质与边界

这是一次重构，不是上游镜像、同步分支或完整再发行版。本仓库保留 PPT Master 的四个顶层 artifact routes——Generate、Create Template、Fill Native PPTX、Enhance Native PPTX——以及原作者署名，但重新定义了 Codex 的触发方式、工具选择、交互边界、轻量后备运行时、安装流程与验证标准。Generate 下仍区分 Ordinary、Beautify、Image-to-PPTX 三个 profile；Default/Quick 是独立执行 mode，不提升为路由或 profile。

本仓库不声称与上游逐文件兼容，也不会自动跟随上游 `main`。以后吸收上游变更时，必须先固定新的 commit，审核许可证、行为和安全边界，再人工迁移。

## 变更映射

| 上游基线 | 本仓库重构 | 说明 |
|---|---|---|
| `skills/ppt-master/SKILL.md` 与 `workflows/routing.md` | `skills/ppt-master/SKILL.md` 及精简 references | 保留 Generate、Create Template、Fill Native PPTX、Enhance Native PPTX 四个顶层路由；Generate 继续拥有 Ordinary、Beautify、Image-to-PPTX profiles，并把 Default/Quick 作为独立 mode；整体改为 Codex 可执行的渐进式加载规则 |
| Create Template 的 Brand/Style/Layout/Deck 子工作流 | 可复用工作区合同 | 主要产物是含 `templates/`、可选 `images/`、`icons/`、评审 `exports/` 的独立工作区；来源 PPTX/SVG 等保持只读，评审 PPTX 不是主产物 |
| 面向全部 PPT 请求的宽泛触发 | 显式 `$ppt-master` | 避免与 Codex 内置演示文稿能力发生隐式路由冲突 |
| `.claude-plugin/*` 与 Claude Marketplace | `skills/ppt-master/agents/openai.yaml` | 使用 Codex Skill 元数据，不把 Claude 插件元数据当作 Codex 安装入口 |
| `TeamCreate`、`Agent`、`SendMessage` | Codex 子代理与串行回退约定 | 不依赖 Claude Code 专属多代理原语 |
| Codex Image-to-PPTX 文字约定 | Codex 原生图片查看、生成与编辑工具映射 | 直接使用 Codex 可用能力；不可用时明确降级或阻塞，不伪造成功 |
| 大型 SVG、图标、声音、模板与示例库 | 不打包 | 降低安装体积，并避免把未实际分发的第三方素材许可证混入运行时 |
| 完整 SVG→DrawingML 工具链 | Codex 原生工具优先，确定性 JSON→PPTX 后备 | 后备路径只覆盖其声明支持的对象集合，不冒充上游完整转换器 |
| 上游署名完整性约束 | 本仓库署名验证与 `NOTICE.md` | 同时保留 Hugo He 与本重构维护者的版权声明 |

## 上游同步原则

1. 不运行自动镜像、强制覆盖或不经审核的目录复制。
2. 每次同步先在本文件记录新的上游 commit 与迁移范围。
3. 只迁移可证明需要的规则或实现；保持 Codex 原生工具优先。
4. 引入任何第三方素材前，先补齐对应许可证、来源、版本和哈希。
5. 同步后必须运行仓库的单元测试、环境诊断、署名验证与冒烟验证。

详细版权说明见 [NOTICE.md](NOTICE.md) 和 [LICENSE](LICENSE)。
