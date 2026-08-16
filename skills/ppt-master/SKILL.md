---
name: ppt-master
description: "仅在用户明确调用 `$ppt-master` 时使用。把材料或现有演示文稿制作成可交付的 PPTX 或可复用模板工作区，支持生成演示文稿、创建 Brand/Style/Layout/Deck 模板工作区、向原生 PPTX 模板填充内容，以及在保留视觉的前提下增强原生 deck；生成路线还支持逐页美化与从页面图像重建可编辑图层。不要因一般 PPT/PPTX 请求隐式调用。"
---

# PPT Master

把内容、模板或页面图像转换成结构清晰、尽量可编辑且经过验证的 `.pptx` 或可复用模板工作区。保留输入原件；不要直接覆盖用户文件。

## 定位运行根目录

把当前 `SKILL.md` 所在目录解析为绝对路径 `SKILL_ROOT`，不要根据当前工作目录猜测。Skill 自带的 `references/` 与 `scripts/` 均相对于 `SKILL_ROOT`；项目的 `assets/` 相对于项目根和 `deck.json`，不在 Skill 目录中查找。执行脚本时始终使用绝对脚本、输入和输出路径。

首次运行先检查环境：

```bash
SKILL_ROOT="/absolute/path/to/ppt-master"
python "$SKILL_ROOT/scripts/doctor.py" --json
```

## 按需读取参考

- 开始任何任务前读取 [路由规则](references/routing.md) 与 [项目契约](references/project-contract.md)。
- 选择工具或遇到能力缺口时读取 [Codex 运行时](references/codex-runtime.md)。
- 使用 bundled JSON builder 时读取 [Deck Spec](references/deck-spec.md)。
- 生成或修改文件前读取 [质量门禁](references/quality-gates.md)。
- 处理许可证、再分发或署名时读取 [上游来源与重构边界](references/upstream.md)。

## 执行工作流

1. 检查输入文件、交付目标、受众、语言、比例、页数、品牌约束与时效要求；只对会实质改变结果且无法安全推断的缺口提问。
2. 在 `generate`、`create-template`、`fill-template`、`enhance` 中选择一个主路由。选择 `generate` 时再从 `ordinary`、`beautify`、`image-to-pptx` 中选择一个互斥 profile，并选择 `default` 或 `quick` 执行模式；`image-to-pptx` 固定为 `quick`。混合任务拆成有顺序的阶段。
3. 在 Skill 目录之外建立项目目录，记录项目契约、来源、假设、资产和输出路径。原始文件只读保存。
4. 优先使用会话提供的 Codex `Presentations` Skill 完成创建、编辑、渲染和检查；同时遵守它的指令。PPT Master 负责路由、保真约束与验收，不与它争夺底层文件操作。
5. 仅在需要定制位图视觉时使用 ImageGen；需要当前事实、出处或在线资产时使用浏览器；把独立研究、素材搜集或第二轮 QA 委托给子代理，但只允许一个执行者写最终 deck/spec。
6. 缺少原生 Presentations 能力，或需要可重复的确定性构建时，先形成 JSON Deck Spec，再调用 bundled builder。builder 只处理 `generate`，以及 `create-template/exports` 中的可选评审 deck；不得用于 `fill-template` 或 `enhance`：

```bash
python "$SKILL_ROOT/scripts/build_deck.py" "/absolute/project/deck.json" -o "/absolute/project/output/deck.pptx"
```

首次构建默认拒绝覆盖已有文件。只有确认目标是本项目先前生成的常规文件时，迭代重建才加 `--force`；符号链接输出始终禁止。

7. 先运行 `validate_pptx.py` 安全预检，再运行 `inspect_pptx.py`、逐页视觉检查和路线专属保真检查；修复后重新完整验证。未通过质量门禁时不要宣称完成。
8. 交付 `.pptx`、验证摘要和仍存在的限制；只在用户要求时附带中间产物。

## 硬性约束

- 不要把截图式整页图片冒充可编辑幻灯片；`generate/image-to-pptx` 应拆分文字、形状、线条和图片图层，并如实说明不可编辑部分。
- 不要为“增强”路线擅自改版，也不要在模板填充时悄悄替换母版、主题或品牌字体。
- 不要伪造来源、浏览结果、音频、转场或验证结论。缺少能力时明确降级，并优先给出仍可验证的结果。
- 不要在 Skill 安装目录写项目数据或交付文件。
- 不要删除来源与许可证信息；交付前运行署名校验。
