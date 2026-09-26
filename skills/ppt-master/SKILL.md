---
name: ppt-master
description: "仅在用户明确调用 `$ppt-master` 时使用。Codex-native PPT 工作流：生成/重设计可编辑 PPTX、创建 Brand/Style/Layout/Deck 模板工作区，以及通过原生 round-trip 编辑已有 PPTX（含模板填充、选择性改页、页序调整、备注、链接、图表/表格/公式、动画与转场）。不要因一般 PPT/PPTX 请求隐式调用。"
---

# PPT Master for Codex

这是 `hugohe3/ppt-master@v6.6.0` 的 Codex-native 适配版。控制层保持轻量，重大能力由同步进来的上游工作流与原生 PPTX 引擎提供。

## 0. 运行根目录

把当前 `SKILL.md` 所在目录解析为绝对路径 `SKILL_ROOT`。不要依赖当前工作目录。

首次使用先运行：

```bash
python3 "$SKILL_ROOT/scripts/doctor.py" --json
```

项目、缓存、转换结果与最终 PPTX 必须写在 Skill 目录之外。

## 1. 固定加载顺序

1. 读取 [Codex 运行时映射](references/codex-runtime.md)。
2. 读取 [三路由入口](workflows/routing.md)。
3. 选择且只选择一个顶层路由：Generate PPTX、Create Template、Edit Native PPTX。
4. 只读取所选路由及其明确触发的 supporting references/stages。
5. 生成或修改文件前读取 [质量门禁](references/quality-gates.md) 与 [项目契约](references/project-contract.md)。

旧术语 `fill-template` 与 `enhance` 都是 `edit-native` 的兼容别名，不再是独立顶层路由。

## 2. Codex 优先级

1. Codex 原生能力优先：会话提供 Presentations、网页检索、ImageGen 或视觉检查能力时优先使用；PPT Master 负责路由、规划、保真和验收。
2. PPT Master 6.6 原生引擎：需要确定性 SVG→DrawingML、原生公式/图表/表格/链接、模板结构或 PPTX round-trip 保真时，使用 bundled 6.6 scripts。
3. 轻量 JSON builder 最后兜底：只用于 `generate` 与 Create Template 的可选评审 deck；绝不伪造原生编辑保真。

当上游工作流提到 provider-specific `image_gen.py` / `image_search.py` 时，Codex 中默认先用原生 ImageGen/Web。只有原生能力不可用或用户明确要求本地 provider 时才调用 bundled provider。

## 3. 三条顶层路线

### Generate PPTX
用于从主题、文档、数据、现有 deck 或页面图生成/重设计新 deck。继续支持 Ordinary、Beautify、Image-to-PPTX；Quick/Default 是执行模式，不是路由。

### Create Template
用于生成可复用 Brand / Style / Layout / Deck 工作区。不要把来源 PPTX 就地“升级”为模板。

### Edit Native PPTX
用于保留已有 PPTX 的 native design 并进行模板填充、选择性改页、删页/换序/重复、添加备注/链接/动画/转场等。优先使用 `pptx_to_svg.py --roundtrip` → 编辑 workspace → `svg_to_pptx.py --roundtrip`；未改页面应保持原生恢复。

## 4. 关键设计纪律

- Plan 只决定事实、叙事、页面 roster、关系、全局约束和已准备资产；Executor 决定 canvas 上的 composition、carrier、geometry、preset 与 treatment。
- 使用 vocabulary-led semantic selection：先判断页面语义关系，再选择文字/图片/原生形状/图表/表格/公式，而不是按关键词硬套模板。
- 每页可声明 `order/link/parent/membership/contrast/overlap` 等 Relationships；是否需要 topology 由 Executor 决定。
- 文字区域先测量再排版；复杂数学优先原生 Office Math；数据图表/表格优先可编辑 native 对象并做 parity 检查。
- Revision Round 只重跑受影响层，不因小改动整套重建。
- 任何路线都不得以“文件生成成功”替代结构、内容、视觉和保真 QA。

## 5. 交付

最终至少交付：目标 PPTX/模板工作区、采用路由、验证结果、来源/许可提示与仍存在的限制。若核心保真门禁失败，明确阻断，不把部分成功描述为完整交付。
