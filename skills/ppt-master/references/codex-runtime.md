# Codex 运行时与工具映射

先检测能力，再选实现。不要仅凭工具名称假设功能，也不要在已有原生能力时重复实现同一操作。

## 能力优先级

1. 使用 Codex 原生或已安装的专用 Skill/工具。
2. 用 bundled 脚本补足检查、确定性构建与离线运行。
3. 若关键能力仍缺失，保留原件、明确限制，不静默交付降级结果。

运行诊断：

```bash
SKILL_ROOT="/absolute/path/to/ppt-master"
python "$SKILL_ROOT/scripts/doctor.py" --json
```

`SKILL_ROOT` 必须是当前 `SKILL.md` 所在目录的绝对路径。其余命令也必须传入绝对输入、输出路径。

## Presentations

会话提供 `Presentations` Skill 时，先读取并遵守它，用于创建/编辑 PPTX、复用模板、渲染页面和做视觉 QA。PPT Master 继续负责：

- 四路由判定与阶段拆分；
- `generate` 的 profile 与 `default|quick` 模式选择（`image-to-pptx` 固定 `quick`）；
- 项目契约、来源记录与保留约束；
- 原生工具与 bundled builder 之间的切换；
- 路线专属验收和最终交付。

原生实现不能满足确定性复现，或当前环境没有 Presentations 时，使用 JSON Deck Spec 与 builder。不要同时让两个运行时写同一个输出文件。

## ImageGen

仅在定制插画、背景、纹理、场景图或难以用可编辑形状表达的视觉能显著改善结果时使用 ImageGen。

- 编辑现有图片前先查看原图，并把所有目标图片作为引用输入。
- 不让生成模型绘制需要准确拼写的大段文字、表格、图表或品牌标识；这些内容在 PPTX 中原生排版。
- 保存生成提示、输出文件和使用页面；保持分辨率与页面裁切匹配。
- ImageGen 不可用时，优先使用用户素材、可编辑形状或经许可的在线素材，不伪造已生成资产。

## 浏览器

当请求要求最新信息、精确出处、网页材料或在线素材时使用可用的浏览器/网页检索能力；若存在专用连接器或 API，优先使用它。

- 优先引用原始、权威来源；记录标题、URL、访问日期和所支持的具体断言。
- 下载或截取素材前核对许可、分辨率与品牌限制；不要把搜索缩略图当原图。
- 需要登录态或页面交互时使用可访问现有会话的浏览器控制能力。
- 浏览器不可用时不得声称信息为最新；在项目契约中记录离线限制。

## 子代理

仅把边界清楚且可独立验证的任务交给子代理，例如：来源研究、叙事大纲、素材候选清单、逐页视觉复核。

- 不让多个代理同时编辑同一个 PPTX、Deck Spec 或项目清单。
- 由主代理统一版本、来源、路径和最终验收。
- 第二轮 QA 代理应看到原始材料与待验 deck，而不是预设结论。
- 子代理不可用时串行执行同样的检查，不降低验收标准。

## Bundled JSON builder

在 Skill 目录之外初始化项目：

```bash
python "$SKILL_ROOT/scripts/init_project.py" "quarterly-review" --root "/absolute/project-parent"
```

按 [Deck Spec](deck-spec.md) 编写 JSON 后构建：

```bash
python "$SKILL_ROOT/scripts/build_deck.py" "/absolute/project/deck.json" -o "/absolute/project/output/deck.pptx"
```

builder 只支持 `generate`，以及 `create-template/exports` 中的可选评审 deck；`fill-template` 与 `enhance` 会直接拒绝。已有常规输出默认不覆盖，确认它是当前项目生成物后才可加 `--force`；符号链接输出始终禁止。

检查现有或生成的 PPTX：

```bash
python "$SKILL_ROOT/scripts/validate_pptx.py" "/absolute/project/output/deck.pptx" --json
python "$SKILL_ROOT/scripts/inspect_pptx.py" "/absolute/project/output/deck.pptx" --json
python "$SKILL_ROOT/scripts/verify_attribution.py"
```

把命令退出码视为判定信号；不要只解析人类可读文本。若 doctor 报告缺少依赖，先查安装说明并获得必要权限，不要擅自修改系统环境。

## 降级边界

- builder 是确定性的离线后备，不代表支持 PowerPoint 的全部 OOXML 功能。
- JSON builder 生成 deck，不生成完整 `create-template` 工作区；该路线用文件系统组织 `templates/` 及可选资产，builder 只可生成 `exports/` 中的可选评审 deck。
- 对模板填充或原生增强，先检查 builder 是否能保留所需母版、版式、备注、媒体、关系和转场；不能证明保真时，不要静默扁平化或从头重建。
- 不支持的单项可在用户同意后降级；影响路线核心承诺的能力缺口必须在交付前阻断。
- 无论采用哪种运行时，都必须执行 [质量门禁](quality-gates.md)。
