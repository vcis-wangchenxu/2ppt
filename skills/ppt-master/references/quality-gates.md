# 质量门禁

“导出了 PPTX”不等于完成。最终交付至少通过以下门禁。

## 1. 结构 / 包体

- 输出可重新打开；
- OOXML 关系与媒体资源有效；
- 页数、canvas、roster 与计划一致；
- 原生 round-trip 不产生孤儿关系、丢失 Master/Layout 或错误代理对象。

```bash
python3 "$SKILL_ROOT/scripts/validate_pptx.py" /absolute/result.pptx --json
python3 "$SKILL_ROOT/scripts/inspect_pptx.py" /absolute/result.pptx --json
```

6.6 SVG/native pipeline 同时执行其 `svg_quality_checker.py`、delivery/native parity 检查。

## 2. 内容
核对标题、数字、单位、日期、专名、图表数据、来源、引语和 speaker notes。不得把模板示例文字当事实，不得把推断伪装成来源事实。

## 3. 视觉
逐页渲染并检查 clipping / overflow / overlap、alignment / spacing / contrast / hierarchy、image crop / resolution / watermark / license、deck-wide consistency、text-over-image readability 和多语言字体换行。Codex 可用视觉能力时优先做第二轮独立视觉 QA。

## 4. 路线保真

- Generate：Ordinary 检查叙事/事实；Beautify 检查页数/页序/信息归属；Image-to-PPTX 与源页并排比较并说明不可编辑区域。
- Create Template：验证 workspace、slots、结构、字体回退与至少两个内容样例。
- Edit Native：未修改页面原生恢复；只改变授权对象；检查 native chart/table/formula/link、Master/Layout、notes、animation/transition 与 page plan。

## 5. Revision Round
修改发生在哪一层，就只重跑该层及其下游检查；最终交付前完整重跑所有门禁。

## 6. 署名

```bash
python3 "$SKILL_ROOT/scripts/verify_attribution.py"
```
