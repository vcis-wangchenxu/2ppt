# 项目契约

项目契约是每次任务的单一事实源。开始写 deck 前创建；发现新约束时更新。不要把项目文件写入 Skill 安装目录。

## 最小字段

记录以下内容，可使用 Markdown 或 JSON：

| 字段 | 要求 |
| --- | --- |
| `project_id` | 稳定、文件系统安全的项目名 |
| `route` | `generate`、`create-template`、`fill-template` 或 `enhance` |
| `profile` | 仅 `generate` 必填：`ordinary`、`beautify` 或 `image-to-pptx` |
| `template_type` | 仅 `create-template` 必填：`Brand`、`Style`、`Layout` 或 `Deck` |
| `mode` | `default` 或 `quick`；默认 `default`，`image-to-pptx` 固定 `quick`，两者使用同一验收标准 |
| `goal` | 一句话说明演示要促成的决定、理解或行动 |
| `audience` | 受众、知识水平、阅读/演讲场景 |
| `language` | 正文与备注语言；中英混排规则 |
| `slide_size` | 比例或精确尺寸；未指定时记录采用 16:9 的假设 |
| `slide_plan` | 页数目标、页序、逐页目的；`beautify` 需含旧页→新页映射 |
| `visual_system` | 颜色、字体、网格、图表、图片与品牌规则 |
| `editability` | 哪些元素必须原生可编辑，哪些允许位图化 |
| `preserve` | 路线要求冻结或继承的对象、母版、内容与关系 |
| `sources` | 输入文件、事实来源、在线来源、素材许可与访问日期 |
| `assumptions` | 未经用户明确给出的安全假设及影响 |
| `runtime` | Presentations、bundled builder 及实际使用的辅助能力 |
| `deliverables` | 最终 PPTX、可选中间件和验证报告的绝对路径 |
| `acceptance` | 可机械验证且与路线对应的完成条件 |

## 项目目录

对需要 bundled deck builder 的任务，使用 `init_project.py` 创建隔离结构：

```text
<project>/
├── ppt-master.json   # 项目清单与规范入口
├── deck.json         # Deck Spec v1
├── assets/
│   ├── images/       # 本地、下载或生成的视觉资产
│   └── data/         # 图表数据及其来源
└── output/           # 最终交付物
```

按需增设 `source/` 保存只读输入副本、`qa/` 保存渲染图和修复记录。不要移动脚本生成的清单或 `deck.json`。Deck Spec 内的资产路径相对 `deck.json` 所在目录；CLI 输入与输出使用绝对路径。

`create-template` 不以 `deck.json` 项目为正式产物；创建独立模板工作区：

```text
<template-workspace>/
├── templates/    # 必需：Brand/Style/Layout/Deck 模板定义与可复用资源
├── images/       # 可选：已获许可的图片资产
├── icons/        # 可选：已获许可的图标资产
└── exports/      # 可选：评审用预览或 PPTX/PDF 导出
```

PPTX 可作为参考输入或 `exports/` 中的评审结果，不要把单个 PPTX 冒充完整模板工作区。

所有类别至少写 `templates/design_spec.md`，记录 `template_id`、类别、适用/不适用场景、来源、颜色、字体与回退、图像/图标规则、变量或占位语义、资产相对路径和验证方法。类别边界如下：

- `Brand`：只固化身份事实（颜色、字体、标志、语气、图标方向），不携带页面原型；
- `Style`：只固化可迁移的沟通方法与视觉方向，不声称品牌身份或页面几何；
- `Layout`：固化品牌中立的画布、网格、文本角色、槽位和 `templates/*.svg` 原型 roster；
- `Deck`：固化带身份或重复业务场景语义的完整系统，并提供 `templates/*.svg` 原型 roster。

下游 `generate` 必须接收并读取明确的工作区根目录，不能按一个模糊名称扫描或猜测本机模板。`exports/` 只作评审证据，不是应用模板时的输入。

## 来源与事实

- 对每个外部断言记录来源，并标记它支持的页码或元素。
- 区分用户提供事实、计算结果、在线事实与设计性文案。
- 保留原始数据和计算方法；图表数值不得只存在于图片中。
- 记录第三方资产的作者、链接、许可和修改情况。无法确认许可时不用该资产。
- 使用生成资产时记录生成方式与提示摘要，不把它误记为真实事件照片。

## 路线保留矩阵

### `generate`

所有 profile 冻结事实与用户明确要求。`ordinary` 允许重组叙事和视觉；`beautify` 额外冻结页数、页序、逐页映射和每页信息归属；`image-to-pptx` 冻结页面图的构图与层级目标，并要求文字、基础形状、线条和简单图表优先原生重建。不可可靠分离的复杂照片或纹理可局部位图化，但必须记录。

### `create-template`

冻结品牌、模板类别与使用场景约束。`templates/` 必须存在并能独立复用；可选图片、图标与导出物不得成为隐含依赖。记录变量/占位语义、字体回退、资产许可和适用边界；示例内容不得成为模板结构的必需依赖。

### `fill-template`

冻结母版、版式、主题、品牌字体、页脚规则和占位符语义。内容溢出时先压缩文案或选择同系列版式，不擅自缩到不可读。

### `enhance`

默认冻结所有可见页面对象、页序与尺寸，只改契约中列出的备注、媒体、转场或元数据。建立修改前后的视觉对照。

## 变更控制

以下情况更新契约并在必要时征得用户确认：改变 route/profile、改变页数或比例、替换模板/母版、把可编辑内容位图化、舍弃原内容、引入未经许可的素材、无法实现路线核心保留约束。`default` 与 `quick` 之间的切换也要记录，但不得用它降低验收标准。

安全且局部的排版修复、拼写修复和验证性重建可直接执行，并记录在 QA 修复日志中。
