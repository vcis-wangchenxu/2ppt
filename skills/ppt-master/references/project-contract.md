# 项目契约

所有项目写在 Skill 目录之外，原始输入只读保存。

| 字段 | 含义 |
|---|---|
| project_id | 稳定且文件系统安全的项目名 |
| route | `generate` / `create-template` / `edit-native` |
| profile | Generate 时：ordinary / beautify / image-to-pptx |
| mode | default / quick |
| source_files | 输入文件与来源 |
| output | 最终产物绝对路径 |
| audience | 受众与观看场景 |
| language | 内容语言 / BCP-47（如已知） |
| canvas | 16:9、4:3 或其他 |
| constraints | 用户明确约束 |
| assumptions | 必要推断 |
| provenance | 外部事实与资源出处 |

## Generate
保留事实、信息层级与来源。Beautify 额外保持原页→新页映射；Image-to-PPTX 保持页面 roster、构图和可识别文字。

## Create Template
记录 kind（Brand/Style/Layout/Deck）、reference inputs、可替换 slots、字体/颜色/结构规则和资产许可。输出必须是独立 workspace。

## Edit Native
记录 source PPTX、round-trip workspace、page plan（如有）、实际修改页面/对象以及必须保持 native 的对象。未授权对象默认冻结。

旧 `fill-template` / `enhance` 项目在读取时可映射到 `edit-native`，新项目不要再写旧 route。
