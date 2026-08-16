# Deck Spec v1

Deck Spec 是 bundled builder 的确定性 JSON 输入，主要承载 `generate` 的三个 profiles；route、profile 与 mode 仍记录在项目契约中。它也可生成 `create-template/exports` 中的可选评审 deck，但不能表达完整模板工作区。builder 明确拒绝 `fill-template` 与 `enhance`，因为此 schema 没有原生 PPTX 来源或保留关系。使用 UTF-8、合法 JSON，不写注释、尾随逗号、`NaN` 或无穷值。它描述要生成的页面，不替代项目契约或来源清单。

## 最小示例

```json
{
  "schema_version": 1,
  "meta": {
    "title": "季度回顾",
    "author": "Example Team",
    "language": "zh-CN"
  },
  "slide_size": "wide",
  "theme": {
    "fonts": {
      "heading": "Aptos Display",
      "body": "Aptos"
    },
    "colors": {
      "background": "F7F8FA",
      "text": "172033",
      "primary": "2F6BFF",
      "muted": "667085",
      "white": "FFFFFF"
    }
  },
  "slides": [
    {
      "background": "background",
      "notes": "先讲结论，再解释两个驱动因素。",
      "elements": [
        {
          "type": "text",
          "x": 0.7,
          "y": 0.55,
          "w": 11.9,
          "h": 0.6,
          "text": "季度回顾",
          "font_size": 28,
          "font_face": "Aptos Display",
          "color": "text",
          "bold": true
        },
        {
          "type": "shape",
          "shape_type": "rounded_rect",
          "x": 0.7,
          "y": 1.55,
          "w": 3.5,
          "h": 1.4,
          "fill": "E8EEFF",
          "line": { "color": "B9C8FF", "width": 1 },
          "text": "收入 +18%",
          "font_size": 22,
          "color": "2346A0",
          "bold": true,
          "align": "center",
          "valign": "middle"
        },
        {
          "type": "chart",
          "chart": "column",
          "x": 4.6,
          "y": 1.45,
          "w": 7.7,
          "h": 4.8,
          "categories": ["Q1", "Q2", "Q3", "Q4"],
          "series": [
            { "name": "收入", "values": [84, 91, 103, 118] }
          ],
          "title": "季度收入指数",
          "legend": "none",
          "colors": ["2F6BFF"]
        }
      ]
    }
  ]
}
```

构建命令：

```bash
SKILL_ROOT="/absolute/path/to/ppt-master"
python "$SKILL_ROOT/scripts/build_deck.py" "/absolute/project/deck.json" -o "/absolute/project/output/deck.pptx"
```

输出已存在时默认停止。只有确认它是当前项目此前生成的常规文件时，才在迭代重建中加 `--force`；输出为符号链接时即使加 `--force` 也会拒绝，且输出永远不能与 spec 指向同一文件。

## 坐标、尺寸与颜色

- `x`、`y`、`w`、`h`、`x1`、`y1`、`x2`、`y2` 均以英寸为单位；原点在页面左上角，向右、向下为正。
- `slide_size` 可为 `"wide"`（13.333 × 7.5）、`"standard"`（10 × 7.5），或 `{ "width": 13.333, "height": 7.5 }`。
- 颜色使用六位 RGB 十六进制字符串，例如 `"2F6BFF"`，也可引用 `theme.colors` 中的名称。
- `elements` 的数组顺序决定层级：后出现的元素位于更上层。
- 所有元素必须完全位于页面边界内；需要满版出血时，把元素尺寸精确设为画布尺寸。

## 顶层字段

| 字段 | 必需 | 说明 |
| --- | --- | --- |
| `schema_version` | 是 | 当前固定为整数 `1` |
| `route` | 否 | builder 允许 `generate`（默认）或 `create-template`（仅可选评审 deck）；其他顶层 route 会被拒绝 |
| `profile` | 否 | `generate` 的 profile；存在时必须与项目契约一致 |
| `meta` | 否 | 文档元数据：`title`、`subject`、`author`、`keywords`、`comments`、`category`、`content_status`、`identifier`、`language`、`version`；每项最多 255 字符 |
| `slide_size` | 否 | 页面预设或英寸尺寸对象；省略时为 `wide` |
| `theme` | 否 | 默认字体和语义颜色；元素级值覆盖主题 |
| `slides` | 是 | 非空页面数组 |

`theme.fonts` 定义 `heading` 与 `body`；`theme.colors` 定义命名调色板，例如 `background`、`text`、`primary`、`secondary`、`accent`、`muted`、`white`。接受颜色的字段可写六位 RGB，也可引用调色板名称。不要依赖未声明的机器字体；品牌字体不可用时在项目契约中记录回退字体。

## 页面字段

每个 `slides[]` 对象支持：

| 字段 | 必需 | 说明 |
| --- | --- | --- |
| `name` | 否 | 可读页面名称，用于来源和 QA 映射 |
| `background` | 否 | 页面背景颜色；省略时继承主题 |
| `notes` | 否 | 演讲者备注纯文本 |
| `elements` | 否 | 页面元素数组；省略时为空页，空页必须有明确理由 |

## 通用元素字段

每个元素必须有 `type`。除 `line` 外，元素通常还需要 `x`、`y`、`w`、`h`。可用 `name` 提供可读对象名、用 `alt` 提供替代文本。位置和尺寸必须为有限非负数；`w`、`h` 必须大于 0。

### `text`

使用 `text` 字符串，或使用 `paragraphs` 表达多段/多样式内容，二者不要同时出现。

```json
{
  "type": "text",
  "x": 0.8,
  "y": 1.0,
  "w": 5.0,
  "h": 1.2,
  "paragraphs": [
    {
      "runs": [
        { "text": "关键结论：", "bold": true },
        { "text": "留存率提升 6 个百分点" }
      ],
      "align": "left"
    },
    "第二段可以直接写字符串。"
  ],
  "font_face": "Aptos",
  "font_size": 18,
  "color": "172033",
  "valign": "top",
  "margin": 0.05
}
```

支持的常用样式包括 `font_face`、`font_size`（磅）、`color`、`bold`、`italic`、`align`（`left|center|right|justify`）、`valign`（`top|middle|bottom`）和 `margin`。`margin` 可为统一英寸数值，或 `{ "left": 0.08, "right": 0.08, "top": 0.04, "bottom": 0.04 }`。文本框还可用 `fill` 与 `line`，格式同 shape。段落对象只允许 `text|runs|align|level`，其中 `level` 为 0–8；run 只允许 `text|font_face|font_size|color|bold|italic`。每个文本框最多 200 段，每段最多 200 个 runs。

### `shape`

```json
{
  "type": "shape",
  "shape_type": "rect",
  "x": 1.0,
  "y": 1.0,
  "w": 2.5,
  "h": 1.0,
  "fill": "FFFFFF",
  "line": { "color": "D0D5DD", "width": 1 },
  "rotation": 0,
  "text": "原生形状",
  "font_size": 18,
  "color": "text",
  "align": "center",
  "valign": "middle"
}
```

`shape_type` 使用 `rect|rectangle|rounded_rect|rounded_rectangle|ellipse|oval|triangle|diamond|chevron|pentagon|hexagon|arrow_right|arrow_left|arrow_up|arrow_down`。`fill` 是颜色、主题颜色名或 `"none"`；`line` 是颜色、`"none"`，或包含 `color`、`width`、`dash` 的对象。形状内文字直接使用外层 `text` 或 `paragraphs`，并在同一对象中写文本样式，不使用嵌套文本对象。

### `line`

```json
{
  "type": "line",
  "x1": 1.0,
  "y1": 3.0,
  "x2": 5.0,
  "y2": 3.0,
  "color": "667085",
  "width": 1.5,
  "dash": "solid",
  "begin_arrow": "none",
  "end_arrow": "triangle"
}
```

线条使用两个端点，不使用 `x/y/w/h`。`dash` 为 `solid|dash|dot|dash_dot|long_dash`；`begin_arrow` 与 `end_arrow` 为 `none|triangle|stealth|diamond|oval|arrow`。不确定时省略，使用默认直线。

### `image`

```json
{
  "type": "image",
  "x": 7.1,
  "y": 1.0,
  "w": 5.2,
  "h": 3.2,
  "path": "assets/images/product.png",
  "fit": "contain",
  "alt": "产品界面截图，展示新的筛选器"
}
```

`path` 必须是相对于 Deck Spec 文件、且仍位于该目录树中的安全路径；不得使用绝对路径或 `..`。builder 会规范化路径并拒绝目录外逃逸。`fit` 为 `contain`、`cover` 或 `stretch`，省略时为 `contain`；满版照片通常应显式使用 `cover`，图标和截图通常使用 `contain`，仅明确需要形变时使用 `stretch`。非装饰图片必须提供准确 `alt`。单张图片文件不得超过 100 MiB，像素数不得超过 8000 万。

### `table`

```json
{
  "type": "table",
  "x": 0.8,
  "y": 1.4,
  "w": 11.8,
  "h": 3.6,
  "rows": [
    ["指标", "本季", "环比"],
    ["收入", "118", "+15%"],
    ["留存", "86%", "+6pp"]
  ],
  "header_rows": 1,
  "column_widths": [3.8, 3.8, 4.2]
}
```

`rows` 必须是列数一致的二维数组；单元格可为字符串、数字、布尔值或 `null`。`header_rows` 表示开头作为表头的行数，默认 1，也可为 0；`column_widths` 以英寸计，其总和必须等于表格宽度 `w`（允许 0.02 英寸舍入误差）。样式字段为 `align`、`font_face`、`font_size`、正文 `color`、`header_color`、`header_fill` 与 `cell_fill`；默认表头使用 `primary` 底色和白字，正文使用 `white` 底色和 `text` 颜色。

### `chart`

```json
{
  "type": "chart",
  "chart": "line",
  "x": 0.8,
  "y": 1.4,
  "w": 11.8,
  "h": 4.8,
  "categories": ["1月", "2月", "3月"],
  "series": [
    { "name": "实际", "values": [72, 81, 93] },
    { "name": "计划", "values": [75, 80, 86] }
  ],
  "title": "月度趋势",
  "legend": "bottom",
  "colors": ["2F6BFF", "98A2B3"]
}
```

`chart` 为 `bar|column|line|pie`。每个 `series` 只允许 `name` 与 `values`，且 `values` 数量必须等于 `categories` 数量；非饼图允许用 `null` 表示缺失点，其余值必须是有限数值；饼图只能有一个 series。每个图表最多 100 个 series、1000 个 categories。`legend` 为 `none|bottom|top|left|right`；还可用 `style`（1–48）和布尔值 `data_labels`。保留原始数据来源，不把图表预渲染成图片。

## 路径与可移植性

- 把 spec、资产和输出放在项目目录，不引用 Skill 安装目录中的临时文件。
- 优先使用相对 spec 的资产路径，使项目可移动；调用 CLI 时仍传入 spec 与输出的绝对路径。
- 不在 JSON 中放密钥、登录凭据、`file://` URL 或不可重现的临时下载地址。
- JSON 文件不得超过 32 MiB；字段名严格校验，拼写错误会直接失败而不是静默忽略。
- 构建后先运行 `validate_pptx.py` 安全/结构预检，再运行 `inspect_pptx.py` 与逐页视觉 QA；schema 合法不代表排版正确。

## 不可表达的功能

Deck Spec v1 聚焦常见可编辑元素。它不能代替 `create-template` 的 `templates/` 及配套资产。复杂母版继承、SmartArt、嵌入对象、宏、精细动画、音视频关系或高级转场若未被 builder 明确支持，不要虚构字段。`fill-template` 或 `enhance` 需要这些功能时，优先交给 Presentations/原生 OOXML 路径；否则按项目契约阻断或经用户同意后降级。
