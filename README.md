# 2ppt — PPT Master for Codex

这是面向 **OpenAI Codex** 的 PPT Master 适配仓库。当前基线选择性同步 `hugohe3/ppt-master v6.6.0` 的核心能力，同时保留显式 `$ppt-master` 触发、Codex 原生工具优先和轻量 JSON fallback。

## 核心能力

- 三路由：Generate PPTX / Create Template / Edit Native PPTX；
- Ordinary / Beautify / Image-to-PPTX + Default / Quick；
- PPTX → SVG → PPTX source-preserving round-trip；
- native shapes、gradients、effects、charts、tables、Office Math、hyperlinks；
- Master/Layout/slot structured export；
- text measurement、多语言排版、source converters；
- transitions、object animations、Morph、notes/narration tooling；
- Brand/Style/Layout/Deck template workflow；
- image composition / slicing / treatment；
- Revision Round、visual review、native parity 与 fail-closed QA；
- 原有 `build_deck.py` 继续作为 Generate 的确定性最后兜底。

为保持 Codex Skill 可维护性，没有 vendoring 上游的巨大 `ai-image-comparison`、brands、12k icons 与 sounds 资产库；这些场景优先使用用户素材或 Codex 原生 Web/ImageGen。

## Mac + Codex 安装

推荐把仓库作为唯一真源，并用 symlink 安装：

```bash
mkdir -p ~/Developer
cd ~/Developer
git clone https://github.com/vcis-wangchenxu/2ppt.git
cd 2ppt

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r skills/ppt-master/requirements.txt

python3 install.py --symlink --force
python3 skills/ppt-master/scripts/doctor.py --json
python3 skills/ppt-master/scripts/verify_attribution.py
ls -la ~/.agents/skills/ppt-master
```

重启 Codex 后运行 `/skills`，再显式调用 `$ppt-master`。

## 路由

| 目标 | Route |
|---|---|
| 新建、重设计、截图重建 | Generate PPTX |
| 建 Brand/Style/Layout/Deck 可复用工作区 | Create Template |
| 用现有 PPTX 模板填内容、选择性改页、删页换序、补备注/链接/动画/转场 | Edit Native PPTX |

旧 `fill-template` 与 `enhance` 都兼容映射到 Edit Native PPTX。

## 上游同步

`tools/sync_ppt_master.py` 是可重复的选择性 vendoring 工具。GitHub workflow 固定从 `v6.6.0` 同步并生成 `UPSTREAM_MANIFEST.json`，不会覆盖本仓库的 Codex 控制层。

详细来源与边界见 [UPSTREAM.md](UPSTREAM.md) 和 [NOTICE.md](NOTICE.md)。
