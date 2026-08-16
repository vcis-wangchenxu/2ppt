# 第三方声明存档

本 Codex 重构版不打包上游的大型图标、声音或 DrawingML 预设几何数据。为保留上游归属链和方便未来按许可证选择性引入资源，下列声明按固定基线存档；仅将指向未打包本地许可证文件的链接改为官方链接并明确说明未包含。只有将相应资源加入发行版时，对应许可证和署名义务才会实际生效。

## 上游声明存档 1: `skills/ppt-master/templates/icons/THIRD_PARTY_NOTICES.md`

# Third-Party Icon Notices

The SVG files under this directory include third-party assets. PPT Master's
MIT license covers PPT Master itself; it does not replace the licenses,
attribution requirements, brand guidelines, or trademark rights that apply to
these assets.

## Bundled snapshots

Snapshot date: **2026-08-09**.

| Directory | Upstream baseline | Bundled files | Compatibility boundary |
|---|---|---:|---|
| `chunk-filled` | [CHUNK Icons](https://www.figma.com/community/file/1327310800295849271/chunk-icons), versionless snapshot cross-checked against the [SVG Repo collection](https://www.svgrepo.com/collection/chunk-16px-thick-interface-icons/) and [Wikimedia Commons category](https://commons.wikimedia.org/wiki/Category:Chunk_Icons) | 641 | PPT Master-normalized files; historical local basenames remain stable |
| `tabler-filled` | [Tabler Icons v3.46.0](https://github.com/tabler/tabler-icons/releases/tag/v3.46.0), commit `8ac7d81b72ece11072ef25ea9fd92e80c6f3c9fc` | 1,055 | 1,054 upstream files plus 1 legacy spelling alias |
| `tabler-outline` | [Tabler Icons v3.46.0](https://github.com/tabler/tabler-icons/releases/tag/v3.46.0), commit `8ac7d81b72ece11072ef25ea9fd92e80c6f3c9fc` | 5,138 | 5,130 upstream files plus 8 legacy spelling aliases |
| `phosphor-duotone` | [`@phosphor-icons/core@2.1.1`](https://www.npmjs.com/package/@phosphor-icons/core/v/2.1.1), npm integrity `sha512-v4ARvrip4qBCImOE5rmPUylOEK4iiED9ZyKjcvzuezqMaiRASCHKcRIuvvxL/twvLpkfnEODCOJp5dM4eZilxQ==` | 1,518 | 1,512 upstream files plus 6 legacy aliases; upstream `-duotone` filename suffixes are removed locally |
| `simple-icons` | [Simple Icons 16.28.0](https://github.com/simple-icons/simple-icons/releases/tag/16.28.0), commit `fc91ef03ec113d06627b2d47c1f9644ca202b6f9` | 3,675 | 3,453 current files plus 222 compatibility files matching the 12.4.0 snapshot at commit `32b07a5b798b84b97f2cbbb5b69ec7cb80472f73` |

The Tabler compatibility aliases are `mood-confuzed` in `tabler-filled`, plus
`brand-adobe-after-effect`, `brand-kako-talk`, `currency-rubel`,
`gender-trasvesti`, `ikosaedr`, `mood-confuzed`, `physotherapist`, and
`sport-billard` in `tabler-outline`.

The Phosphor compatibility aliases are `archive-box`, `archive-tray`,
`folder-notch`, `folder-notch-minus`, `folder-notch-open`, and
`folder-notch-plus`. Their current upstream equivalents are respectively
`box-arrow-down`, `tray-arrow-down`, `folder`, `folder-minus`, `folder-open`,
and `folder-plus`.

Simple Icons compatibility files are retained because existing templates,
examples, and user projects may still reference removed brand IDs. Their
presence here does not mean that the current Simple Icons project still ships
or recommends those marks.

## CHUNK Icons attribution

**CHUNK Icons** by **Noah Jacobus** is licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

PPT Master modifications: root dimensions were normalized to 24 by 24,
hard-coded black fills were changed to `currentColor`, SVG Repo wrapper
metadata was removed, and historical local filenames were retained. The icon
geometry remains sourced from CHUNK. The `r` glyph was restored from the
public Wikimedia mirror during the 2026-08-09 reconciliation.

## Simple Icons license and trademark notice

The Simple Icons project is released under
[CC0 1.0](https://github.com/simple-icons/simple-icons/blob/16.28.0/LICENSE.md),
but that does not imply that every individual brand icon is CC0. Brand marks
may have separate licenses, usage guidelines, or trademark restrictions.
Before using a bundled brand icon, check its current Simple Icons metadata,
the brand owner's guidelines, and the upstream
[disclaimer](https://github.com/simple-icons/simple-icons/blob/16.28.0/DISCLAIMER.md).
Neither CC0 nor inclusion in this repository grants trademark permission.

## MIT notices

The following copyright notices and MIT terms apply to the Tabler and
Phosphor assets described above.

### Tabler Icons

Copyright (c) 2020-2026 Paweł Kuna

### Phosphor Icons

Copyright (c) 2023 Phosphor Icons

### MIT License terms

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Update policy

- Pin a released upstream version, or record the audit date for a versionless
  source, before copying files.
- Overwrite files that still exist upstream, but do not automatically delete
  local-only names. Review removals and renames as compatibility changes.
- Recheck the Simple Icons disclaimer and per-brand metadata whenever that
  library is refreshed; an upstream removal is not merely a file-sync detail.
- Recount the directories and validate every SVG after each refresh. Update
  this notice and the two icon-library README tables in the same change.


---

## 上游声明存档 2: `skills/ppt-master/templates/sounds/THIRD_PARTY_NOTICES.md`

# Third-Party Sound Notices

The WAV files under this directory are modified copies of third-party CC0
sound assets. PPT Master's MIT license covers PPT Master itself; the source
declarations below describe the bundled sounds.

## Bundled snapshot

Snapshot date: **2026-08-10**.

| Directory | Upstream snapshot | Bundled files | Local modification |
|---|---|---:|---|
| `kenney-interface` | [Kenney Interface Sounds](https://kenney.nl/assets/interface-sounds), archive supplied as version 1.0 | 100 | Ogg Vorbis transcoded to PCM 16-bit 44.1 kHz WAV while preserving mono/stereo layout |
| `kenney-ui` | [Kenney UI Audio](https://kenney.nl/assets/ui-audio), versionless current archive | 51 | Ogg Vorbis transcoded to PCM 16-bit 44.1 kHz WAV while preserving stereo layout; `Preview.ogg` excluded |
| `bigsoundbank` | [BigSoundBank](https://bigsoundbank.com/) sound IDs listed below | 35 | Source WAV resampled and, where needed, reduced to PCM 16-bit at 44.1 kHz while preserving mono/stereo layout |

No sound was trimmed, loudness-processed, or unnecessarily downmixed.
Final-file metadata and SHA-256 digests are recorded in `sounds_index.json`.
The Kenney archive URLs and archive digests are also recorded there.

The normalization pass is equivalent to:

```bash
ffmpeg -i <input> -map_metadata -1 -vn -c:a pcm_s16le -ar 44100 <output.wav>
```

No explicit channel-count option is used, so source mono/stereo layout remains
intact.

The UI Audio asset page reports 50 files, while the current downloaded archive
contains 51 usable files under `Audio/`. This snapshot includes all 51 and does
not count the separate preview track.

## Kenney

The source license files for both Kenney packs declare
[Creative Commons Zero (CC0 1.0)](https://creativecommons.org/publicdomain/zero/1.0/).
They permit personal, educational, and commercial use, and state that credit
to Kenney is appreciated but not mandatory.

- Interface Sounds: created and distributed by Kenney, version 1.0, source
  creation date 2020-02-11.
- UI Audio: created by Kenney Vleugels / Kenney.nl.

## BigSoundBank

BigSoundBank identifies the selected files as
“CC0 (public domain): Free and royalty-free” and links them to its
[license page](https://bigsoundbank.com/licenses.html). The individual source
pages identify Joseph Sardin as the author.

The snapshot contains exactly these sound IDs:

- Whoosh: `0572`, `0573`, `1795`–`1802`
- Notification: `2059`–`2067`
- Chime: `2079`–`2091`
- Pencil signature: `3236`–`3238`

Each entry in `sounds_index.json` records its individual BigSoundBank source
page. The library keeps the full recordings, including the two long whooshes
and longer chimes; the `recommended` flag keeps those outside the conservative
default discovery shortlist without removing them.

## CC0 terms

CC0 1.0 lets the rights holder waive copyright and related rights to the
greatest extent allowed by law. It provides the work as-is and does not grant
patent, trademark, privacy, or publicity rights. The upstream asset bundle
contains a local copy of the legal code; that asset and local license copy are
not included in this refactored distribution. See the
[official CC0 1.0 legal code](https://creativecommons.org/publicdomain/zero/1.0/legalcode)
for the complete terms.


---

## 上游声明存档 3: `skills/ppt-master/scripts/pptx_shapes/data/NOTICE.md`

# DrawingML preset geometry data provenance

## Apache POI notice

Apache POI

Copyright 2003-2025 The Apache Software Foundation

This product includes software developed at

The Apache Software Foundation (<https://www.apache.org/>).

## Vendored data

`presetShapeDefinitions.xml` is vendored from Apache POI 5.4.1:

- Release tag: `REL_5_4_1`
- Source commit: `4554f204cbbf00ecbcaed134fe57e43a1779a612`
- Source path: `poi/src/main/resources/org/apache/poi/sl/draw/geom/presetShapeDefinitions.xml`
- Source revision: <https://github.com/apache/poi/tree/4554f204cbbf00ecbcaed134fe57e43a1779a612>
- Original release-file SHA-256:
  `a7dad593d27bd70536b41da9b761fa16409536cc0c25ef2b6c7a61c5d9b3e738`
- Vendored SHA-256: `4a762444d8d85876881c02a5b1dedf6f73006fcd8acb7b4e393435615b37c780`
- Modification: line endings normalized from the release JAR's mixed CRLF/LF to LF; XML content is otherwise unchanged.
- License: Apache License 2.0; see `LICENSE-APACHE-2.0.txt`.

The independent completeness list in `shape_type_values.txt` is derived from
the Open XML SDK schema metadata for `a:ST_ShapeType` / `ShapeTypeValues`:

- Repository: `dotnet/Open-XML-SDK`
- Source commit: `00967dc871f06776ae969762c6703d062308a6c9`
- Source path: `data/schemas/schemas_openxmlformats_org_drawingml_2006_main.json`
- Source revision:
  <https://github.com/dotnet/Open-XML-SDK/tree/00967dc871f06776ae969762c6703d062308a6c9>
- Source-file SHA-256:
  `e760b534c96ee02745d2a8084f1be362826da4470a85d0b0102a67c3b1678ab7`
- Vendored enum-list SHA-256:
  `f2c3bdcda8569b358ce3196cfeb183849e33bfc7955fac961dc85fceb6b3b587`
- License: MIT (`dotnet/Open-XML-SDK`); see
  `LICENSE-OPEN-XML-SDK-MIT.txt`.

At the locked revisions, both sources contain exactly 187 unique preset names,
and their sets are identical.

## Evaluator compatibility notes

- The circular-arrow, left-circular-arrow, and left-right-circular-arrow
  definitions each contain `+- xH 0 dxB 0`. Apache POI evaluates the first
  three operands and ignores the inert final zero. The PPT Master evaluator
  accepts only this trailing-zero compatibility form; other arity mismatches
  remain errors.
- A small number of definitions rebind an intermediate guide name later in
  the ordered `gdLst`. Evaluation therefore preserves document order and the
  later value replaces the earlier value, matching Apache POI behavior.
