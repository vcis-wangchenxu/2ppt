# 四路由、Generate Profiles 与执行模式

先选择一个顶层 artifact route。只有 `generate` 继续选择 profile；profile 不是第五条路线。若请求跨越多个路线，声明阶段顺序，并分别应用每阶段的保留约束。

## 四个顶层路由

| 路由 | 典型输入与意图 | 核心承诺 | 主要产物 |
| --- | --- | --- | --- |
| `generate` | 内容资料、现有 deck 或页面图，需要制作/重设计演示文稿 | 根据 profile 保留事实、逐页映射或页面视觉，并输出可交付 deck | 新生成或重构的 PPTX |
| `create-template` | 品牌指南、参考 deck 或视觉样例，需要可反复使用的设计资源 | 把规则与资产组织成 Brand/Style/Layout/Deck 模板；不要把特定演示内容焊死 | 含必需 `templates/` 及可选 `images/icons/exports` 的模板工作区 |
| `fill-template` | 原生 `.pptx` 模板 + 新内容 | 继承母版、版式、主题、品牌字体、占位符语义和视觉语言 | 使用原模板的新内容 deck |
| `enhance` | 原生 `.pptx` + 备注、讲稿、音频、转场或元数据增强 | 保留可见页面，只添加明确要求的非改版增强 | 视觉基本不变的增强版 PPTX |

## Generate 的三个互斥 profiles

| Profile | 选择条件 | 额外保留约束 |
| --- | --- | --- |
| `ordinary` | 从文本、数据、资料包或宽泛风格参考新建 deck | 事实、来源、信息层级和项目契约 |
| `beautify` | 对现有 deck 逐页美化或重设计 | 页数、页序、旧页→新页映射，以及每页信息归属；用户明确授权时才合并/拆页 |
| `image-to-pptx` | 从截图、页面图、扫描图或逐页渲染图重建 | 构图、层级、对齐、颜色和可识别文字；文字、基础形状、线条与简单图表优先原生可编辑 |

不得同时选择多个 profile。混合输入以用户的主要交付目标判定；确需组合时拆成两个独立 `generate` 阶段并分别验收。

## 两种执行模式

- `default`：完整执行材料理解、叙事、设计、素材、构建、渲染和多轮 QA。用户未指定时采用此模式。
- `quick`：为预览、低复杂度或用户明确要求速度的任务减少候选方案与迭代轮数，优先复用已提供的内容和资产。`generate/image-to-pptx` 强制使用此模式。不得跳过结构验证、逐页视觉检查、来源检查或路线保真门禁。

模式影响过程深度，不改变 artifact route、profile 或交付标准。不要把 `quick` 当成“允许交付未验证文件”。

## 判定顺序

1. 目标是创建可反复复用的 Brand/Style/Layout/Deck 模板工作区：选择 `create-template`。
2. 已有原生模板，目标是套入新内容：选择 `fill-template`。
3. 已有原生 deck，目标仅是增加备注、音频、转场或非视觉元数据：选择 `enhance`。
4. 其余选择 `generate`，再判定 profile：页面图重建用 `image-to-pptx`；现有 deck 逐页重设计用 `beautify`；其余用 `ordinary`。
5. `image-to-pptx` 固定选 `quick`；其他 profile/route 在用户明确要求快速预览或快速版本时选 `quick`，否则选 `default`。

## 易混淆场景

- “保持每页内容但重新设计”是 `generate/beautify`，不是 `enhance`。
- “把这组截图做成能改字的 PPT”是 `generate/image-to-pptx`，不是顶层独立路线。
- “基于这套品牌规范做一个以后能反复用的模板库”是 `create-template`；PPTX 可作为参考输入或可选评审导出，但不是该路线唯一或必需产物。
- “用这份模板做一套新汇报”是 `fill-template`；模板只是风格参考且不要求原生复用时，可选择 `generate/ordinary` 并记录假设。
- “在这份 deck 中补备注并加转场，页面不要动”是 `enhance`。
- “先做模板，再填内容、补备注”拆成 `create-template` → `fill-template` → `enhance`。

## 最低输入

### `generate`

至少获得内容来源或可读取的视觉输入，以及交付目标。默认比例为 16:9；未指定页数时按叙事需要决定。`beautify` 必须先建立逐页映射；`image-to-pptx` 必须先确认页序、裁切、尺寸和清晰度。

### `create-template`

至少获得视觉/品牌约束和预期使用场景，并在 `Brand|Style|Layout|Deck` 中选择模板类别。输出工作区必须包含 `templates/`；按需要加入 `images/`、`icons/`、`exports/`。模板应写清适用场景、变量/占位语义、字体回退和资产许可；示例内容必须易替换或明确标为说明。

### `fill-template`

至少获得可读取的原生模板和新内容。先检查母版、版式、主题、占位符、页脚及示例页；区分可删除的示例内容和必须保留的模板结构。

### `enhance`

至少获得可读取的原生 deck 与增强清单。先生成视觉基线；除用户授权项外，把所有可见对象视为冻结。

## 改路由条件

发现输入与预期不符时停止写入并重新判定。例如：所谓模板只是 PDF；用户要的不是可复用模板而是一套成品页；所谓“增强”实际要求全面改版；页面图分辨率不足以识别文字。改变 route/profile 会影响可编辑性或保真度时，先向用户说明。
