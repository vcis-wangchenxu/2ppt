# Deck Spec v1（轻量兜底）

Deck Spec 是本仓库自有 `build_deck.py` 的确定性 JSON 输入，只承担 `generate` 的轻量 fallback，以及 `create-template` 中可选的评审 deck。

它不承担 `edit-native`，也不能替代 PPT Master 6.6 的 SVG/round-trip/native chart-table/formula contracts。

当 Codex Presentations 或 6.6 native engine 可用时，优先使用能力更强的路径。历史 `fill-template` / `enhance` Deck Spec 必须拒绝。

现有 schema/元素语法仍以 `build_deck.py` 的校验为准；不要虚构字段。输出已有文件时默认拒绝覆盖，只有确认是当前项目生成物后才使用 `--force`。
