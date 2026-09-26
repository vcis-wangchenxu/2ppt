# Codex 运行时映射

本文件是上游 PPT Master 6.6 在 Codex 中的宿主适配层；若与 provider-specific 说明冲突，本文件优先。

## 能力优先级

1. Codex Presentations / 原生文件能力。
2. bundled PPT Master 6.6 native engine。
3. bundled JSON builder（仅 Generate / 模板评审 deck）。

不要让两个运行时同时写同一个输出文件。

## Python 运行器

所有 bundled Python 脚本必须通过 `sh "$SKILL_ROOT/scripts/run-python.sh" ...` 调用。运行器按顺序选择：`PPT_MASTER_PYTHON` → 仓库 `.venv/bin/python` → Skill `.venv/bin/python` → 当前 `VIRTUAL_ENV` → PATH 中的 `python3`，并强制要求 Python 3.10+。

## Generate

默认先使用 Codex Presentations 完成创建、编辑、渲染和视觉检查。需要确定性 DrawingML、原生数据对象、公式或上游 SVG contract 时使用 6.6 pipeline。

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
sh "$SKILL_ROOT/scripts/run-python.sh" "$SKILL_ROOT/scripts/svg_quality_checker.py" /absolute/workspace/authoring-svg-flat --roundtrip --json
sh "$SKILL_ROOT/scripts/run-python.sh" "$SKILL_ROOT/scripts/svg_to_pptx.py" /absolute/workspace/authoring-svg-flat -o /absolute/workspace/exports/result.pptx --roundtrip
```

需要页序/删页/重复时按 `workflows/edit-native-pptx.md` 写 `page_plan.json`。不要用 JSON builder 模拟 native round-trip。

## Create Template

使用同步进来的 Create Template workflow、schemas、scaffolds、Style/Layout/Deck library 与 `apply_template.py`。本适配版故意不内置上游巨量 icons/sounds/brand asset packs；遇到这些资源时优先使用用户提供素材或 Codex 原生检索/图像能力。

## 图片与网页

Codex 默认：事实/来源/在线图片用原生 Web；定制插画/背景/元素用原生 ImageGen；上游 `image_gen.py` / `image_search.py` 仅作为显式 fallback。仍可使用 bundled `slice_images.py`、`image_treat.py`、图片 provenance 与 composition rules。

## 原生能力

bundled 6.6 engine 提供或保留 native shapes/Boolean geometry/gradients/effects、native charts/tables、Office Math、hyperlinks、Master/Layout/slots、transitions、object animations、Morph、source-preserving round-trip、多语言 text measurement、source conversion 和 revision/visual QA。

## 验证

```bash
sh "$SKILL_ROOT/scripts/run-python.sh" "$SKILL_ROOT/scripts/doctor.py" --json
sh "$SKILL_ROOT/scripts/run-python.sh" "$SKILL_ROOT/scripts/verify_attribution.py"
```

最终仍需结构检查 + 渲染视觉检查 + 路线保真检查。
