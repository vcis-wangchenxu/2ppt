# 2ppt：面向 Codex 的 PPT Master Skill

2ppt 是对 [Hugo He 的 PPT Master](https://github.com/hugohe3/ppt-master) 进行的 Codex 定向重构。它用四路由约束演示文稿任务，优先调用 Codex 已提供的 Presentations、ImageGen、浏览器和子代理能力；当原生演示文稿能力不可用，或需要可重复的离线构建时，可使用随 Skill 提供的 `python-pptx` JSON builder。

本项目不是上游镜像，也不打包上游约 80 MB 的 Skill 素材库、大型示例、图标、声音或 DrawingML 预设几何数据。来源、重构映射和版权边界见 [UPSTREAM.md](UPSTREAM.md)、[NOTICE.md](NOTICE.md) 与 [LICENSE](LICENSE)。

> 重要：本 Skill **只在提示词中明确写出 `$ppt-master` 时启用**。普通的“帮我做 PPT”不会隐式触发，以免与 Codex 内置 Presentations Skill 发生路由冲突。

## 目录

- [能力与四路由](#能力与四路由)
- [运行方式：Codex 原生能力与后备 builder](#运行方式codex-原生能力与后备-builder)
- [前置条件](#前置条件)
- [安装](#安装)
- [在 Codex Desktop、CLI 与 IDE 中调用](#在-codex-desktopcli-与-ide-中调用)
- [升级](#升级)
- [卸载与恢复](#卸载与恢复)
- [API Key、联网与隐私](#api-key联网与隐私)
- [权限与安全边界](#权限与安全边界)
- [验证安装与端到端冒烟测试](#验证安装与端到端冒烟测试)
- [故障排查](#故障排查)
- [开发与 CI](#开发与-ci)

## 能力与四路由

Skill 会为一次任务选择一个主路由。跨路由请求会拆成有顺序的阶段，并分别应用保留约束。

| 顶层路由 | 适用场景 | 核心保留约束 | 示例调用 |
|---|---|---|---|
| `generate` | 从文本、数据和资料创建新 deck；逐页美化现有 deck；或从页面图像重建 deck | 保留事实和信息层级；由 Beautify 或 Image-to-PPTX profile 追加各自的 1:1/视觉保真约束 | `$ppt-master 把这份季度报告做成 10 页 16:9 中文管理层汇报。` |
| `create-template` | 从 PPTX/SVG、页面图、文档、网站、品牌资产或文字要求创建可复用模板工作区 | 参考文件只读；产出独立的 Brand、Style、Layout 或 Deck 工作区，不把原文件就地“升级”为模板 | `$ppt-master 从 brand-guide.pdf 创建可复用的 Brand 工作区。` |
| `fill-template` | 把新内容填入原生 `.pptx` 模板 | 保留母版、版式、主题、品牌字体、页脚和占位符语义 | `$ppt-master 使用 brand-template.pptx 填入 q3-data.xlsx，保持模板母版。` |
| `enhance` | 给已有 deck 增加备注、讲稿、音频、转场或非视觉元数据 | 默认冻结所有可见对象、页序、尺寸、位置、样式和内容 | `$ppt-master 为 final.pptx 补演讲者备注和转场，页面视觉不要变化。` |

`generate` 内部先选择互斥的 profile：Ordinary、Beautify 或 Codex 专用的 Image-to-PPTX。Default/Quick 是与 profile 分开的执行 mode：Ordinary 和 Beautify 可按显式快速意图选择 Quick，否则使用 Default；Image-to-PPTX 固定使用 Quick。Beautify 用于保留文案、页数和页序的 1:1 美化；Image-to-PPTX 用于把幻灯片截图、扫描图或逐页渲染图重建为尽量可编辑的页面。它们都不是第五条顶层 artifact route。

几个容易混淆的边界：

- “每页内容不变，但重新设计”属于 `generate`，不是 `enhance`。
- 一般新建、改写、扩写或重新设计属于 `generate` 的 Ordinary profile。
- “严格保留文案、页数和页序做 1:1 美化”属于 `generate` 的 Beautify profile。
- “把截图还原成可编辑文件”属于 `generate` 的 Image-to-PPTX profile，不能用整页截图覆盖来冒充可编辑。
- “从这套参考资料提炼一个以后可复用的模板系统”属于 `create-template`。
- “把新内容套入这份原生模板”属于 `fill-template`。
- “页面不要动，只补备注/音频/转场”属于 `enhance`。
- “先套模板，再加备注”会按 `fill-template` → `enhance` 分阶段执行。
- “把原 PPTX 变成可复用工作区，再基于它生成新 deck”会按 `create-template` → `generate` 分阶段执行。

`create-template` 的主要产物是独立的 Brand、Style、Layout 或 Deck 工作区（必需 `templates/`，可按需要包含 `images/`、`icons/` 与评审 `exports/`），不是把来源文件原地改成一个 PPTX。原生 PPTX 可以作为参考输入；评审 PPTX 只是可选导出。

详细判定规则见 [skills/ppt-master/references/routing.md](skills/ppt-master/references/routing.md)。

## 运行方式：Codex 原生能力与后备 builder

两条实现路径互补，但不能同时写同一个输出文件。

### 1. Codex 原生能力优先

当当前会话具备对应能力时，Skill 会优先使用：

- **Presentations Skill**：创建、编辑、复用模板、渲染和视觉 QA；这是处理高保真 PPTX、模板填充和原生增强的首选。
- **ImageGen**：只用于定制插画、背景、纹理、场景图或图片分层；准确文字、表格、图表和品牌标识仍在 PPTX 中原生排版。
- **浏览器/网页检索**：处理最新事实、精确出处、网页材料和经许可的在线素材。
- **子代理**：承担边界清楚的研究、素材候选或第二轮 QA；只允许一个执行者写最终 deck 或 spec。

这些能力由 Codex 应用、会话和已安装插件提供，不由本仓库模拟。能力缺失时，Skill 必须说明限制，不能伪造浏览、图片生成或视觉验证结果。

### 2. `python-pptx` JSON builder 后备

仓库自带一个确定性、离线、无需 API Key 的 JSON→PPTX 后备运行时，适合：

- 当前会话没有 Presentations Skill；
- 需要相同 JSON 重复生成相同结构；
- 只需要 builder 已声明支持的文本、形状、图片等基础对象；
- CI 或无界面的服务器环境。

它不是完整 PowerPoint/OOXML 引擎，不能自动承诺保留任意模板母版、已有媒体关系、复杂动画或全部原生特性。builder 只接受 `generate`，以及为 `create-template/exports` 生成可选评审 deck；它会明确拒绝 `fill-template` 和 `enhance`。这些原生路线无法证明所需保真时，应停止并改用 Presentations，而不是静默扁平化或重建。

最小 Deck Spec 示例：

```json
{
  "schema_version": 1,
  "slides": [
    {
      "elements": [
        {
          "type": "text",
          "x": 1,
          "y": 1,
          "w": 8,
          "h": 1,
          "text": "Hello"
        }
      ]
    }
  ]
}
```

构建命令：

```bash
python "/absolute/path/to/ppt-master/scripts/build_deck.py" \
  "/absolute/path/to/project/deck.json" \
  -o "/absolute/path/to/project/output/deck.pptx"
```

默认页面为 16:9。完整字段见安装后的 `references/deck-spec.md`。

builder 默认拒绝覆盖已有输出。确认目标是本项目此前生成的常规文件后，迭代重建可在命令末尾加 `--force`；符号链接输出始终拒绝，spec 与输出也不能指向同一文件。

## 前置条件

### 必需

- Codex Desktop、Codex CLI，或支持 Codex Skills 的 IDE 集成；
- Python 3.10 或更高版本（CI 覆盖 3.10–3.13）；
- Git（若使用 clone/升级流程）；
- `python-pptx` 与 Pillow，通过 Skill 内的 `requirements.txt` 安装。

### 可选

- Codex Presentations Skill：高保真创建、编辑、模板复用、渲染和 QA；
- ImageGen：定制位图视觉或页面图分层；
- 浏览器/连接器：最新事实、网页来源和在线素材；
- LibreOffice/`soffice`：额外的 PPTX 渲染与兼容性检查；
- Poppler 的 `pdftoppm`：把 PDF 页面转换为检查用图片；
- `ffmpeg`：检查或处理任务明确需要的音视频素材；
- 能打开 `.pptx` 的桌面应用：最终人工复核。

LibreOffice、Poppler 与 `ffmpeg` 是按场景安装的系统工具，不在 Python `requirements.txt` 中；`doctor.py` 会报告是否找到，但缺失它们不会阻止基础 JSON builder 运行。桌面演示应用同样只是最终人工复核所需的可选项。

检查 Python：

```bash
python --version
```

Windows 若没有 `python` 命令，可使用：

```powershell
py -3 --version
```

下文所有以 `python` 开头的命令在 Windows 上都可等价改为 `py -3`；若使用虚拟环境，则优先调用该环境中的 `python.exe`。

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/vcis-wangchenxu/2ppt.git
cd 2ppt
```

### 2. 安装 Python 依赖

建议先创建虚拟环境，尤其是在开发或 CLI 场景：

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r skills/ppt-master/requirements.txt
```

Windows PowerShell：

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r skills\ppt-master\requirements.txt
```

确保 Codex 调用的是安装了依赖的同一个 Python。若使用虚拟环境，请从已激活该环境的终端启动 Codex CLI 或 IDE；Codex Desktop 无法看到该环境时，可改为给其实际使用的 Python 安装依赖，并用 `doctor.py` 验证。

### 3A. 用户级安装（默认）

```bash
python install.py
```

默认采用复制安装：

- macOS / Linux：`~/.agents/skills/ppt-master`
- Windows：`%USERPROFILE%\.agents\skills\ppt-master`

适合让同一用户的多个 Codex 项目使用。

### 3B. 仓库级安装

```bash
python install.py --project "/absolute/path/to/your-project"
```

目标为：

```text
<your-project>/.agents/skills/ppt-master
```

适合让 Skill 与某个项目绑定。团队是否提交 `.agents/skills/` 应由项目策略决定；安装器不会替你提交文件。

### 3C. 开发用符号链接

用户级链接：

```bash
python install.py --symlink
```

项目级链接：

```bash
python install.py --project "/absolute/path/to/your-project" --symlink
```

符号链接会立即反映 clone 中的改动。Windows 通常需要开启“开发者模式”或管理员权限；失败时去掉 `--symlink`，使用默认复制安装。

### 3D. 明确指定目标目录（高级）

```bash
python install.py --target "/absolute/path/to/skills/ppt-master"
```

`--target` 与 `--project` 互斥；它适合宿主明确要求其他 Skill 根目录的场景。默认复制模式也可显式写为 `--copy`。除非你清楚当前 Codex 宿主扫描哪些目录，否则优先使用默认用户级路径或 `--project`，以免文件安装成功但 Codex 无法发现。

为避免误把项目或其他目录当成安装目标，`--target` 指定的最终目录名必须是 `ppt-master`；卸载常规目录时还会核对其中 `SKILL.md` 的 `name`。

### 已有安装的保护

目标目录已存在时，安装器默认拒绝覆盖并退出，不会修改现有文件。确认替换时使用：

```bash
python install.py --force
```

或：

```bash
python install.py --project "/absolute/path/to/your-project" --force
```

`--force` 会先把原目标移动到同级的 `ppt-master.backup-<UTC时间>`，新安装失败时会自动尝试恢复。

### 4. 重新加载 Codex

安装后重启或重新加载 Codex/IDE，再在提示词中显式调用 `$ppt-master`。若当前任务在安装前已经打开，建议新建任务，避免旧会话没有刷新 Skill 清单。

## 在 Codex Desktop、CLI 与 IDE 中调用

### Codex Desktop

1. 打开存放来源和交付物的项目文件夹。
2. 把 PDF、PPTX、图片、表格等放到项目目录，或在消息中附加文件。
3. 在第一条请求中明确写 `$ppt-master`，并说明受众、用途、语言、比例、页数和保留要求。
4. 允许 Skill 在安装目录之外建立项目目录；不要把交付文件写入 `~/.agents/skills/ppt-master`。

示例：

```text
$ppt-master 使用 ./source/q3-report.pdf 生成一份 10 页、16:9、中文管理层汇报。
受众是董事会，所有数字必须可追溯，输出到 ./output/q3-review.pptx。
```

### Codex CLI

先进入你的项目目录，再启动 Codex CLI：

```bash
cd "/absolute/path/to/your-project"
codex
```

随后输入：

```text
$ppt-master 使用 source/report.docx 制作 PPTX，输出到 output/report.pptx。
```

若使用项目级安装，请确保当前工作目录位于包含 `.agents/skills/ppt-master` 的仓库内。

### IDE 集成

1. 用支持 Codex Skills 的 IDE/扩展打开项目根目录；
2. 确认用户级安装可见，或项目内存在 `.agents/skills/ppt-master/SKILL.md`；
3. 重新加载 IDE 窗口；
4. 在 Codex 聊天面板中显式写 `$ppt-master`。

无论使用哪种宿主，普通 PPT 请求都不会隐式调用本 Skill。

## 推荐任务信息

为了减少无意义追问，首次请求最好提供：

- 输入文件或主题；
- 受众与要促成的决定/行动；
- 语言、比例、页数或演讲时长；
- 品牌、模板和字体约束；
- 必须原生可编辑的对象；
- 可否联网、使用 ImageGen 或外部素材；
- 输出目录与文件名；
- 对原 deck 必须保留或允许改变的内容。

未指定比例时采用 16:9。Skill 只会对会实质改变结果且无法安全推断的缺口提问。

## 升级

### 复制安装

在 clone 目录执行：

```bash
git pull --ff-only
python -m pip install -r skills/ppt-master/requirements.txt
python install.py --force
```

项目级安装：

```bash
git pull --ff-only
python -m pip install -r skills/ppt-master/requirements.txt
python install.py --project "/absolute/path/to/your-project" --force
```

升级前的安装会保留为时间戳备份。验证新版本后再自行清理旧备份。

### 符号链接安装

链接本身无需重建：

```bash
git pull --ff-only
python -m pip install -r skills/ppt-master/requirements.txt
```

若目录结构发生变化，再重新运行 `install.py --symlink --force`。

生产环境建议固定仓库 commit，审核变更后升级，不要在关键交付中自动跟随远端分支。

## 卸载与恢复

用户级卸载：

```bash
python install.py --uninstall
```

项目级卸载：

```bash
python install.py --project "/absolute/path/to/your-project" --uninstall
```

卸载是可恢复的：安装器会把当前目标移动为同级的 `ppt-master.backup-<UTC时间>`，不会直接删除。确认不再需要后，可由用户自行删除备份。

恢复时，先确保目标路径不存在，再把备份改回 `ppt-master`；或直接用 `install.py --force` 安装一个新副本。

卸载或升级后重新加载 Codex/IDE。

## API Key、联网与隐私

### 无需 API Key 的部分

- 安装器；
- 环境诊断、署名验证、PPTX 检查与验证；
- bundled JSON builder；
- 单元测试和冒烟测试。

这些本地脚本不需要联网生成 deck。

### Codex 原生工具

Presentations、ImageGen、浏览器和连接器是否可用，由当前 Codex 产品、账号、组织策略和已安装插件决定。通常应通过 Codex 的连接/登录界面授权，而不是把凭据写进本仓库。

本仓库的后备 builder 不读取 `OPENAI_API_KEY`，也不会因为发现某个 Key 就自动调用外部模型。

### 需要联网的操作

- `git clone` / `git pull`；
- `pip install`；
- 浏览最新事实、网页或在线素材；
- 调用 ImageGen、云端连接器或其他外部服务。

联网前确认材料是否允许发往对应服务。机密、个人信息、受版权限制或受合同约束的内容，不应在未授权时上传。

### 密钥规则

- 不把 Key、Token、Cookie 写入 prompt、Deck Spec、PPTX、日志或仓库；
- 优先使用 Codex/插件的安全连接配置或进程环境变量；
- `.env` 已被 `.gitignore` 排除，但“被忽略”不等于“适合明文长期保存”；
- 若怀疑密钥进入 git 历史，应立即轮换，而不只是删除工作区文件。

## 权限与安全边界

Skill 可能需要的权限取决于任务：

| 权限 | 用途 | 安全边界 |
|---|---|---|
| 读取输入文件 | 分析 PDF、PPTX、图片、表格和模板 | 原件只读；不直接覆盖用户来源 |
| 写项目目录 | 保存契约、素材、spec、QA 和最终 PPTX | 不在 Skill 安装目录写项目数据 |
| 写 `~/.agents/skills` | 用户级安装/升级 | 已有目标默认拒绝；`--force` 先备份 |
| 写 `<repo>/.agents/skills` | 项目级安装 | 仅写明确指定的项目；团队自行决定是否提交 |
| 网络 | 下载依赖、检索事实、调用原生在线工具 | 需要时再授权；记录来源和素材许可 |
| 浏览器/登录会话 | 读取需要交互或登录的页面 | 优先专用连接器；不泄露会话信息 |
| 符号链接 | 开发安装 | Windows 可能需要开发者模式/管理员权限 |

Codex 因沙箱或组织策略请求批准时，只批准与当前任务相符、目标路径明确的操作。不要授权宽泛删除、覆盖整个主目录或不明网络命令。

## 验证安装与端到端冒烟测试

以下命令中的 `SKILL_ROOT` 应替换为实际安装路径。

### 1. 环境诊断

用户级安装：

```bash
python ~/.agents/skills/ppt-master/scripts/doctor.py --json
```

项目级安装：

```bash
python "/absolute/project/.agents/skills/ppt-master/scripts/doctor.py" --json
```

### 2. 署名验证

```bash
python ~/.agents/skills/ppt-master/scripts/verify_attribution.py
```

### 3. 内置冒烟测试

```bash
python ~/.agents/skills/ppt-master/scripts/smoke_test.py
```

冒烟测试在临时目录生成最小 deck、运行 validator，并用退出码报告结果；不会把交付文件写入 Skill 目录。

### 4. 手工构建并验证

初始化隔离项目：

```bash
python ~/.agents/skills/ppt-master/scripts/init_project.py demo --root "/absolute/path/to/work"
```

准备 Deck Spec 后：

```bash
python ~/.agents/skills/ppt-master/scripts/build_deck.py \
  "/absolute/path/to/work/demo/deck.json" \
  -o "/absolute/path/to/work/demo/output/deck.pptx"

python ~/.agents/skills/ppt-master/scripts/validate_pptx.py \
  "/absolute/path/to/work/demo/output/deck.pptx" --json

python ~/.agents/skills/ppt-master/scripts/inspect_pptx.py \
  "/absolute/path/to/work/demo/output/deck.pptx" --json
```

脚本退出码必须为 0。最后还要用 Presentations 或可用渲染器检查整套缩略图和逐页大图；结构验证不能替代视觉检查。

### 5. 验证 Codex 发现 Skill

重新加载 Codex 后发起一个低风险请求：

```text
$ppt-master 请只检查当前环境和可用能力，不生成文件。
```

若 Codex 没有识别 `$ppt-master`，按下一节排查路径和刷新问题。

## 故障排查

### Codex 不识别 `$ppt-master`

依次检查：

1. 用户级文件是否存在：`~/.agents/skills/ppt-master/SKILL.md`；
2. 或项目级文件是否存在：`<repo>/.agents/skills/ppt-master/SKILL.md`；
3. 没有多套一层目录，例如 `ppt-master/ppt-master/SKILL.md`；
4. 已重启 Codex、重新加载 IDE，或新建任务；
5. 提示词中确实写了 `$ppt-master`，而不是只说“做 PPT”；
6. 项目级安装时，Codex 打开的是对应项目根目录。

### `install.py` 提示“目标已存在”

这是保护机制。先查看现有目录；确认替换后运行 `--force`。旧安装会被移动到时间戳备份，而不是直接删除。

### `doctor.py` 报 `python-pptx` 或 Pillow 缺失/无法导入

使用运行 `doctor.py` 的同一个解释器安装：

```bash
python -m pip install -r "/absolute/path/to/ppt-master/requirements.txt"
```

避免混用 `pip`、`python`、`python3` 和 `py` 所指向的不同环境。可比较：

```bash
python -c "import sys; print(sys.executable)"
python -m pip --version
```

### Windows PowerShell 禁止激活虚拟环境

可以先不激活，直接调用虚拟环境解释器：

```powershell
.\.venv\Scripts\python.exe -m pip install -r skills\ppt-master\requirements.txt
.\.venv\Scripts\python.exe install.py
```

不要为了本项目随意放宽整台机器的执行策略。

### Windows 符号链接失败

开启 Windows 开发者模式或用有权限的终端；更简单的方案是去掉 `--symlink`，采用默认复制安装。

### Codex Desktop 找不到虚拟环境依赖

GUI 启动的应用不一定继承终端激活状态。先用 `doctor.py --json` 确认 Codex 实际调用的 Python；必要时把依赖安装到该解释器，或从已激活虚拟环境的终端使用 Codex CLI/IDE。

### Presentations、ImageGen 或浏览器不可用

- 新建 deck 且对象在 builder 能力范围内：使用 JSON builder；
- 需要复杂模板保留或原生增强：等待/安装 Presentations 能力，不要静默改走重建；
- ImageGen 不可用：使用用户素材、经许可在线素材或可编辑形状；
- 浏览器不可用：不要声称信息是最新的，在项目契约中记录离线限制。

### builder 报 Deck Spec 错误

先阅读安装目录下 `references/deck-spec.md`。检查：

- `schema_version`；
- 页面和元素数组；
- 坐标、宽高、颜色和图片路径；
- JSON 是否有效、文件编码是否为 UTF-8；
- 图片路径是否可读取。

不要通过删掉验证规则来“修复”输入。

### PPTX 已生成但打不开或 validator 失败

运行：

```bash
python "/absolute/path/to/ppt-master/scripts/validate_pptx.py" FILE.pptx --json
python "/absolute/path/to/ppt-master/scripts/inspect_pptx.py" FILE.pptx --json
```

根据错误修复拥有该对象的 Deck Spec 或源文件后重新完整构建。不要直接修改 ZIP 内部 XML 来掩盖生成错误。

### 文件能打开但视觉有问题

结构检查不会发现所有溢出、错位、低对比度和图片裁切问题。使用 Presentations 或可用渲染器逐页渲染，先看整套缩略图，再看大图；修复后重新运行结构和视觉门禁。

### `verify_attribution.py` 失败

确认 Skill 安装目录中的 `LICENSE` 与 `references/upstream.md` 没有被删除或错误替换。仓库发行副本还应保留根级 `NOTICE.md`、`UPSTREAM.md` 与 `LICENSE`。不要绕过署名门禁；从可信 clone 重新安装并保留本地项目数据。

### 网络或权限错误

- `git`/`pip` 网络失败：确认代理、组织网络策略和证书配置；
- 写 `~/.agents` 失败：检查当前用户权限，不要用宽泛管理员权限覆盖整个主目录；
- Codex 沙箱拒绝读取来源或写输出：把文件放到已授权项目目录，或只批准具体路径。

## 开发与 CI

仓库布局：

```text
.
├── install.py
├── skills/ppt-master/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/
│   ├── requirements.txt
│   └── scripts/
├── tests/
└── .github/workflows/ci.yml
```

本地验证：

```bash
python -m pip install -r skills/ppt-master/requirements.txt
python -m unittest discover -s tests -v
python skills/ppt-master/scripts/doctor.py --json
python skills/ppt-master/scripts/verify_attribution.py
python skills/ppt-master/scripts/smoke_test.py
```

GitHub Actions 在 Python 3.10、3.11、3.12 和 3.13 上执行同一组单元测试、环境诊断、署名验证和冒烟测试。

提交前还应人工审阅：

- Skill 是否仍只允许显式 `$ppt-master`；
- 四路由保留约束是否被削弱；
- builder 的声明能力与实际实现是否一致；
- 是否意外加入密钥、生成文件或未经许可的素材；
- README、Deck Spec、CLI 帮助和实际行为是否同步。

## 许可证与来源

本仓库采用 MIT 许可证，并保留原作者 Hugo He 与本重构维护者的版权声明。它不是 PPT Master 上游的官方发行版。

- [LICENSE](LICENSE)
- [NOTICE.md](NOTICE.md)
- [UPSTREAM.md](UPSTREAM.md)
- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
