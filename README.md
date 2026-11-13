# 2ppt — PPT Master for Codex

这是面向 **OpenAI Codex** 的 PPT Master 适配仓库。当前基线选择性同步 `hugohe3/ppt-master v6.9.0` 的核心能力，同时保留显式 `$ppt-master` 触发、Codex 原生工具优先和轻量 JSON fallback。

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

## Windows + Codex 安装

在仓库根目录使用 PowerShell 和 Python 3.10+，推荐复制安装。共享虚拟环境让安装后的 skill 不依赖当前工作目录，也不需要每次激活环境：

```powershell
git clone https://github.com/vcis-wangchenxu/2ppt.git
cd 2ppt
$venv = Join-Path $HOME '.cache/ppt-master/venv'
py -3 -m venv $venv
$python = Join-Path $venv 'Scripts/python.exe'
& $python -m pip install -r skills/ppt-master/requirements.txt
& $python install.py
& ./skills/ppt-master/scripts/run-python.ps1 ./skills/ppt-master/scripts/doctor.py --json
& ./skills/ppt-master/scripts/run-python.ps1 ./skills/ppt-master/scripts/smoke_test.py
```

若没有 `py` 启动器，第一步换成已安装的 Python 3.10+ 的完整路径。若系统策略阻止运行 `.ps1`，可直接用 `& $python <脚本路径> <参数>`；不需要修改全局执行策略。不要把 Microsoft Store 的 Python 占位程序当成已安装 Python。

## macOS / Linux + Codex 安装

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

python3 install.py --symlink
sh skills/ppt-master/scripts/run-python.sh skills/ppt-master/scripts/doctor.py --json
sh skills/ppt-master/scripts/run-python.sh skills/ppt-master/scripts/verify_attribution.py
ls -la ~/.agents/skills/ppt-master
```

安装依赖时需要激活 `.venv`；Codex 实际运行时不需要激活 Terminal 环境，Skill 会通过 `run-python.sh` 自动优先使用仓库 `.venv/bin/python`。

安装目标默认是 `~/.agents/skills/ppt-master`，也可使用 `--target` 指定当前 Codex 的用户技能目录。已有安装需加 `--force`，旧版会保存在技能发现目录之外的 `skill-backups/` 中，避免备份被再次加载。请只保留一个活动安装位置。

安装后下一轮即可显式调用 `$ppt-master`；若未出现，再重启 Codex。[官方技能说明](https://learn.chatgpt.com/docs/build-skills)

OCR 可按需在同一虚拟环境安装 `rapidocr>=3.0` 和 `onnxruntime>=1.17`。图片生成、网页搜索优先使用 Codex 已提供的能力；本地 provider 与旁白服务的凭据、联网和费用另行配置。`doctor.py` 基础通过不代表所有可选功能及视觉渲染都可用。

## 路由

| 目标 | Route |
|---|---|
| 新建、重设计、截图重建 | Generate PPTX |
| 建 Brand/Style/Layout/Deck 可复用工作区 | Create Template |
| 用现有 PPTX 模板填内容、选择性改页、删页换序、补备注/链接/动画/转场 | Edit Native PPTX |

旧 `fill-template` 与 `enhance` 都兼容映射到 Edit Native PPTX。

## 上游同步

`tools/sync_ppt_master.py` 是可重复的选择性 vendoring 工具。GitHub workflow 固定从 `v6.9.0` 同步并生成 `UPSTREAM_MANIFEST.json`，不会覆盖本仓库的 Codex 控制层。

Git 连接受限时可下载官方发布 ZIP，执行 `python tools/sync_ppt_master.py --upstream-archive <发布包.zip> --repo-root .`；脚本先校验固定的 SHA-256。CI 在 Windows / Linux 上覆盖安装、启动器、JSON 生成、原生 SVG 导出、PPTX 往返和原文件防覆盖；这些结构回归不能替代真实演示文稿的逐页视觉验收。

详细来源与边界见 [UPSTREAM.md](UPSTREAM.md) 和 [NOTICE.md](NOTICE.md)。
