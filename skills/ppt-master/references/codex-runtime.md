# Codex 运行时映射

本文件是上游 PPT Master 6.9 在 Codex 中的宿主适配层；若与 provider-specific 说明冲突，本文件优先。

## 能力优先级

1. Codex Presentations / 原生文件能力。
2. bundled PPT Master 6.9 native engine。
3. bundled JSON builder（仅 Generate / 模板评审 deck）。

不要让两个运行时同时写同一个输出文件。

## Python 运行器

所有 bundled Python 脚本通过当前宿主的运行器调用：Windows 使用 `& "$SKILL_ROOT/scripts/run-python.ps1" ...`，macOS/Linux 使用 `sh "$SKILL_ROOT/scripts/run-python.sh" ...`。下文及上游的 Bash 示例在 Windows 上换用 PowerShell 运行器，参数保持不变；不要求安装 WSL。

选择顺序：`PPT_MASTER_PYTHON` → 仓库 `.venv` → Skill `.venv` → 用户共享 `~/.cache/ppt-master/venv` → 当前 `VIRTUAL_ENV` → PATH。Windows 使用 `Scripts/python.exe` 并跳过 Microsoft Store 的 Python 占位程序；macOS/Linux 使用 `bin/python`。运行器检查 Python 3.10+、启用 UTF-8，并传递子进程退出码。`PPT_MASTER_PYTHON` 应设为完整的解释器路径，不能包含参数。

只在受信的 Python 环境中安装依赖；虚拟环境不随 skill 发布。依赖安装与解释器选择见仓库 README。`doctor.py` 的 `ok` 只表示基础运行时就绪；具体 capability、外部渲染工具、模型凭据和服务可用性分别判断。

## Generate

默认先使用 Codex Presentations 完成创建、编辑、渲染和视觉检查。需要确定性 DrawingML、原生数据对象、公式或上游 SVG contract 时使用 6.9 pipeline。

```bash
sh "$SKILL_ROOT/scripts/run-python.sh" "$SKILL_ROOT/scripts/source_to_md.py" <source> -o <output>
sh "$SKILL_ROOT/scripts/run-python.sh" "$SKILL_ROOT/scripts/text_measure.py" --help
sh "$SKILL_ROOT/scripts/run-python.sh" "$SKILL_ROOT/scripts/svg_quality_checker.py" --help
sh "$SKILL_ROOT/scripts/run-python.sh" "$SKILL_ROOT/scripts/svg_to_pptx.py" --help
```

JSON builder 仍保留为最后兜底：

```bash
sh "$SKILL_ROOT/scripts/run-python.sh" "$SKILL_ROOT/scripts/build_deck.py" /absolute/project/deck.json -o /absolute/project/output/deck.pptx
```

它不承担 Edit Native PPTX。

## Edit Native PPTX

这是原 `fill-template` 与 `enhance` 的统一替代路线。

```bash
sh "$SKILL_ROOT/scripts/run-python.sh" "$SKILL_ROOT/scripts/pptx_to_svg.py" /absolute/source.pptx -o /absolute/workspace --inheritance-mode both --roundtrip
```

先读 `authoring-svg-flat/authoring_summary.json`，只打开需要判断或修改的 SVG。未修改页面与未修改 native objects 依赖 round-trip backing 恢复。

```bash
sh "$SKILL_ROOT/scripts/run-python.sh" "$SKILL_ROOT/scripts/svg_quality_checker.py" /absolute/workspace --roundtrip --json
sh "$SKILL_ROOT/scripts/run-python.sh" "$SKILL_ROOT/scripts/svg_to_pptx.py" /absolute/workspace -o /absolute/workspace/exports/result.pptx --roundtrip
```

需要页序/删页/重复时按 `workflows/edit-native-pptx.md` 写 `page_plan.json`。不要用 JSON builder 模拟 native round-trip。

导出的位置参数是 workspace 根目录，不能传 `authoring-svg-flat/` 子目录。输出必须与原始输入 PPTX 和 `sources/source.pptx` 不同；不得绕过上游的防覆盖检查。

## Create Template

使用同步进来的 Create Template workflow、schemas、scaffolds、Style/Layout/Deck library 与 `apply_template.py`。本适配版故意不内置上游巨量 icons/sounds/brand asset packs；遇到这些资源时优先使用用户提供素材或 Codex 原生检索/图像能力。

## 图片与网页

Codex 默认：事实/来源/在线图片用原生 Web；定制插画/背景/元素用原生 ImageGen；上游 `image_gen.py` / `image_search.py` 仅作为显式 fallback。仍可使用 bundled `slice_images.py`、`image_treat.py`、图片 provenance 与 composition rules。

Image-to-PPTX 使用 6.9 的 OCR 文本证据、去字底图和图层配准流程。`rapidocr` / `onnxruntime` 是按需依赖，模型文件可能需下载；未安装时先使用宿主视觉能力，并明确文字定位尚未经过 OCR 检查。原生图像编辑同样遵守参考图、配准、残留检查与重试上限，不因没有本地 provider key 就切换到收费 API。旁白与动画图像仅在用户任务需要时启用。

上游角色描述不自动要求创建子 agent。当前宿主不提供该能力或任务不需要时，在当前会话执行相应阶段。浏览器确认界面不可用时，用宿主已有的澄清工具解决实质歧义；已有授权不重复询问。

## 原生能力

bundled 6.9 engine 提供或保留 native shapes/Boolean geometry/gradients/effects、native charts/tables、Office Math、hyperlinks、Master/Layout/slots、transitions、object animations、Morph、source-preserving round-trip、多语言 text measurement、source conversion 和 revision/visual QA。

## 验证

```bash
sh "$SKILL_ROOT/scripts/run-python.sh" "$SKILL_ROOT/scripts/doctor.py" --json
sh "$SKILL_ROOT/scripts/run-python.sh" "$SKILL_ROOT/scripts/verify_attribution.py"
```

最终仍需结构检查 + 渲染视觉检查 + 路线保真检查。
