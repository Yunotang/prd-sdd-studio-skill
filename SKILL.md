---
name: prd-sdd-studio
description: >-
  CLI 版的 AI 軟體開發文件與開發工作室。用「諮詢式對話 → 生成 PRD / SDD → 自動出架構圖 → 規劃 TASK.md → 一步步實際開發」
  把專案構想一路帶到可運行的程式碼,並在開發/迭代時自動維護 CHANGELOG、主動詢問本地 git 同步、commit 後半自動把改動回寫
  PRD/SDD 保持文件最新。當使用者說「啟動 PRD 諮詢 / SDD 架構師」「幫我把這個構想做成 PRD」「根據 PRD 生成 SDD」
  「依 SDD 開發專案 / 規劃 TASK」「開新專案並留變更紀錄」「prd-sdd-studio」「devstudio」,或在一個由本 skill 起頭的
  專案裡要求修改/迭代時,都觸發。大腦是你(Claude/Codex),不呼叫任何外部 LLM API。平台中立,Claude Code 與 Codex 皆可用。
---

# PRD/SDD Studio (CLI)

把原 AI DevStudio web app 的全部提示詞與選項邏輯,搬到由**你自己當大腦**的 CLI 流程,
並加上本地端的 **變更紀錄 / git 同步 / 文件跳板** 能力。**不呼叫任何外部 LLM API** —— 原本送給 Gemini 的每段提示詞,現在是你自己依循執行。

## 你必須遵守的鐵則

1. **大腦是你**:`references/` 裡的「系統指令」是你要扮演的角色,「生成模板」是你產文件要照的結構。逐字依循,不要自行精簡章節。
2. **全程繁體中文**輸出文件與對話(技術術語/識別碼/檔名除外)。
3. **日期一定查真**:任何文件的日期欄位、CHANGELOG 時間戳,都先用工具取得**當下真實日期**再填,**絕不沿用模板範例或編造**。提示詞裡關於日期的「嚴重警告」原樣有效。
4. **CLI 選項介面**:用編號選單與使用者互動(可用 AskUserQuestion,或純文字編號選單讓使用者輸入數字/關鍵字)。
5. **動到使用者 codebase = 觸發本地工作流**:任何修改/迭代後,照 `references/workflow-local.md` 走「寫 CHANGELOG → 主動問 git → commit 後問文件同步」。
6. **Git 安全**:絕不直接 commit/push `main`、絕不 `--force`、commit 前先 `git status` 給使用者看、預設只做本地 commit。碰到敏感檔(`.env`/`*.key`/`*secret*` 等)停下來提醒。
7. **先偵測、後問、不重來**:每次呼叫 skill,**先掃描專案資料夾**(見下「啟動偵測」)。有半成品就接力、有現成文件就讀懂後確認直接開發,**絕不無視既有進度或擅自從頭重生成**。

## 啟動偵測(每次呼叫的第一件事,先於主選單)

**載入 `references/startup-scan.md` 並照做。** 在顯示主選單前,先確定工作目錄、掃描既有 `PRD.md`/`SDD.md`/`TASK.md`/`CHANGELOG.md` 與原始碼,依結果路由:

- **有 `TASK.md` 且有未完成任務** → 開發到一半:讀 TASK.md + CHANGELOG 重建脈絡,主動回報進度、從下一個未完成任務**接力續開發**(進功能 4 開發迴圈),**不重新規劃、不重生成文件**。
- **有 PRD/SDD 但沒 TASK.md**(含使用者自備的文件)→ **讀文件、摘要回報你的理解**、請使用者確認 → 同意就依**現有**文件直接進開發(功能 4 規劃 TASK.md),不重生成。
- **只有零星程式碼、無文件** → 詢問要逆向補 PRD/SDD、或直接改程式碼迭代。
- **空 / 全新** → 顯示主選單從功能 1 開始。
- **使用者明確要放棄舊專案改做新的** → **不刪舊檔**,強烈建議**另建乾淨新資料夾**再開始(避免新舊 PRD/SDD/TASK/程式碼混雜);堅持原地重來要二次確認。

## 主選單(啟動偵測判定為「全新/使用者要求看選單」時顯示)

```
=== PRD/SDD Studio ===
請選擇功能（輸入數字）：
  [1] 專案 PRD 諮詢 — MVP 範圍       （多輪對話 → 生成 PRD + 概念架構圖）
  [2] 專案 PRD 諮詢 — 完整專案        （業界標準完整 PRD）
  [3] SDD 架構師（需要 PRD）          （4 種模式 → 生成 SDD + 技術架構圖）
  [4] 依 SDD 實際開發專案             （規劃 TASK.md → 一步步開發）
  [5] 繼續 / 迭代現有專案             （讀既有 PRD/SDD/TASK/CHANGELOG，接續開發）
>
```

**輸出位置(預設:從 skill 啟動的「當前目錄」長出來):** 產物一律建立在 **skill 被啟動時的當前工作目錄** 底下,讓使用者就在自己所在的資料夾裡找得到 —— **絕不**寫到使用者工作區外的固定絕對路徑(那會讓人找不到)。
- **先用工具確認當前工作目錄**(如 `pwd`),不要臆測。
- **新專案**:問使用者一個**專案名稱**(英文 kebab-case,如 `kpi-system`),在當前目錄下建立子資料夾 `<當前目錄>\<專案名>\`,產物寫在那裡:`PRD.md`、`SDD.md`、`docs/diagrams/*.puml` + `*.png`、`TASK.md`、`CHANGELOG.md`。
  - 若使用者本來就把終端 cd 到一個空的/專屬資料夾、想直接拿它當專案根,就問一句要「直接用當前目錄」還是「在當前目錄下開子資料夾」,依其選擇。
- **覆寫彈性**:使用者想放別處(指定絕對/相對路徑)一律尊重。

---

## 功能 1 & 2:PRD 諮詢(Consultant)

載入 `references/prompts-consultant.md`。

**流程(保留原 app 行為):**
1. 依模式選用系統指令:`[1]` → `CONSULTANT_SYSTEM_INSTRUCTION_MVP`;`[2]` → `..._FULL`。以該角色開場,用 CLI 跟使用者**多輪對話**澄清需求(每次 1–2 問,逐步收斂範圍)。支援使用者貼圖/貼參考資料。
2. 對話進行 **≥2 輪**(使用者已給足資訊)後,提供選項:`[g] 生成 PRD 與架構圖`。
3. 生成時**平行產出兩樣**:
   - **PRD**:`[1]` 用 `GENERATE_PRD_PROMPT`、`[2]` 用 `GENERATE_PRD_PROMPT_FULL`(`{{目標平台}}` 預設 `Web Application (React + Node.js)`,可讓使用者改;`{{對話歷史}}` 帶入逐字對話)。寫到 `PRD.md`。
   - **概念架構圖**:用 `GENERATE_PLANTUML_PROMPT`(給 PM 看、不含技術棧)。依「出圖步驟」產圖。
4. 產出後進入本地工作流(見下方「每次產出/修改後」)。
5. **主動接力**:PRD 生成完成後,依 `references/workflow-build.md` 第 1 節**主動詢問**是否進入 SDD 架構師(功能 3)。

---

## 功能 3:SDD 架構師(Architect)

載入 `references/prompts-architect.md`。

1. 取得 PRD 內容:讀專案的 `PRD.md`,或讓使用者貼上 / 指定 `.md`/`.txt` 檔。
2. CLI 選**模式**:
   ```
   選擇 SDD 生成模式：
     [1] 完整版   COMPREHENSIVE  — 企業級 SDD（一次生成）
     [2] 精簡版   SIMPLIFIED     — 快速驗證 / 初學者（一次生成）
     [3] 特定技術 SPECIFIC       — 先推薦技術棧、你確認後才生成
     [4] 互動式   INTERACTIVE    — 漸進式逐步詢問技術決策後生成
   ```
3. 依模式行為(完整保留):
   - `[1]/[2]` **一次生成**:套對應模板產 SDD → 寫 `SDD.md` → **再用 `GENERATE_UML_FROM_SDD_PROMPT` 從 SDD 反推架構圖**(確保圖文一致)。
   - `[3]/[4]` **先對話再生成**:先用對應模板開場(`[3]` 推薦技術棧並問是否接受;`[4]` 先做 PRD 分析再逐步問)。對話往返、技術拍板後,使用者要「生成最終 SDD」時,用 `COMPREHENSIVE` 模板搭配**對話歷史**產 SDD,再反推架構圖。
4. 全程搭配 `ARCHITECT_SYSTEM_INSTRUCTION`。SDD 結尾必含「實作路徑 (Implementation Roadmap)」。預設排除 Docker/K8s/CI-CD(除非使用者要求)。
5. 產出後進入本地工作流。
6. **主動接力到開發**:SDD 生成完成後,依 `references/workflow-build.md` 第 1 節**主動詢問**是否「參考 PRD 了解需求、依 SDD 實際開發專案」。使用者同意 → 進入功能 4。

---

## 功能 4:依 SDD 實際開發專案(規劃 TASK.md → 一步步開發)

載入 `references/workflow-build.md`,**務必照它做**。這是把規格落地成程式碼的閉環。摘要:

1. **讀 PRD 與 SDD**:PRD 抓需求與驗收標準、SDD 抓技術架構與「§10 實作路徑」。
2. **規劃 `TASK.md`**:把 SDD 實作路徑拆成可勾選任務,ID 用 `TASK-NNN`(3 位數,對齊 `[TASK-xxx]` commit 慣例),每筆含狀態/對應 SDD 段落/驗收/產出檔。先給使用者確認再開工。
3. **一步步開發**:一次一個任務 → 依 SDD 規格實作 → 驗證 → 進本地工作流(寫 CHANGELOG、主動問 git、commit 用 `[TASK-NNN]`、commit 後問 PRD/SDD 同步)→ 把 TASK.md 該項標 ✅ → 問是否繼續下一個。
4. **失敗處理**:同一任務失敗 ≥2 次 → TASK.md 標 ⏸ 阻塞、CHANGELOG 記 root cause、停下來告知使用者,不硬撐。

---

## 功能 5:繼續 / 迭代現有專案

讀專案既有 `PRD.md`/`SDD.md`/`TASK.md`/`CHANGELOG.md` 建立脈絡:
- 還沒有 `TASK.md` 但有 SDD → 走功能 4 規劃任務。
- 已有 `TASK.md` → 接續未完成任務繼續開發。
- 純粹要改某段程式/文件 → 直接做,完成後一律進本地工作流(CHANGELOG → 問 git → 文件同步)。

---

## 出圖步驟(取代原 web 內嵌渲染 —— 直接出圖檔)

每當任一提示詞產出 PlantUML 原始碼:

1. 把 `@startuml ... @enduml` 原始碼寫到 `docs/diagrams/<有意義的名字>.puml`(例 `concept-architecture.puml`、`technical-architecture.puml`)。
2. **自動執行 render 腳本**直接吐出圖檔,使用者完全不用手動轉:
   ```
   python "<skill>/scripts/render_puml.py" "<專案>/docs/diagrams/<name>.puml"
   ```
   - 預設輸出 PNG 到同目錄同名 `<name>.png`;要 SVG 加 `--format svg`。
   - 成功 → 告知使用者圖檔路徑(可用 Read 預覽確認)。
   - 失敗(無網路/語法錯,exit code 2)→ 保留 `.puml`,把錯誤回報給使用者,並可檢查 PlantUML 語法(常見錯:用了 `!include`、識別碼含中文)後重產。
3. 圖的提示詞規則(禁 `!include`/外部庫、`!theme plain`、識別碼不用中文、標籤可中文)務必遵守,否則渲染會失敗。

> 腳本沿用原 app `PlantUMLRenderer.tsx` 的 deflate + 自訂 base64 編碼,純 Python 標準庫,零安裝依賴,需要網路連線 plantuml.com。

---

## 「每次產出/修改後」:本地工作流(所有功能共用)

**這是 CLI 版的核心新增能力。完整規則在 `references/workflow-local.md`,務必載入照做。** 功能 1～5 任何一次對 codebase 的產出/修改/迭代完成後,都要走這套。摘要:

- 任何一次對 codebase 的修改/迭代完成後,依序:
  1. **寫 CHANGELOG**:在專案根 `CHANGELOG.md` 追加一筆(做了什麼/為什麼/影響檔案/Git/文件同步),先標 `⏸ 未版控`、`⏸ 未同步`。時間戳用真實當下時間。
  2. **主動問 git 同步**(不等使用者開口):同意 → 走 git 安全協議(`git status` 給看 → 確認非 main 分支 → 本地 commit → 回填 CHANGELOG 的 commit hash);不同意 → 留 `⏸ 未版控`。
  3. **commit 後才問文件同步跳板**(半自動):同意 → 分析這次改動對 PRD/SDD 的落差 → **先提 diff(原文→改後)等使用者確認** → 寫回文件並更新「最後更新」日期 → 回填 CHANGELOG → 再問文件變更是否也 commit(不再觸發新一輪文件同步,避免迴圈)。

---

## 與原 web app 的對照(確保沒漏)

| 原 app | CLI 版對應 |
|--------|-----------|
| Gemini `gemini-3-flash-preview` | **你自己**(無外部 API) |
| 三個分頁(MVP/FULL/Architect) | 主選單 `[1][2][3]` |
| 對話 ≥2 輪才出現「生成」按鈕 | 同邏輯,出 `[g]` 選項 |
| PRD + UML 平行生成 | 同(Consultant) |
| Architect 4 模式 + 從 SDD 反推 UML | 同(`[1]/[2]` 一次生成、`[3]/[4]` 先對話) |
| IndexedDB 自動存檔 | 落地成 `PRD.md`/`SDD.md`/`TASK.md`/`CHANGELOG.md` 等檔案 |
| PlantUML 瀏覽器內嵌渲染 | `render_puml.py` 直接輸出 `.png`/`.svg` |
| 複製 / 下載 .md | 直接寫進專案資料夾 |
| (無) | **新增**:CHANGELOG、主動 git 同步、PRD/SDD 文件跳板 |
| (無) | **新增**:依 SDD 規劃 `TASK.md` → 一步步實際開發專案 |

## 參考檔案

- `references/startup-scan.md` — 啟動偵測與續傳:掃描專案、接力/讀現成文件/引導新資料夾
- `references/prompts-consultant.md` — PRD 系統指令與生成模板
- `references/prompts-architect.md` — SDD 系統指令、4 模式、架構圖 prompt
- `references/workflow-local.md` — CHANGELOG + git 協議 + PRD/SDD 文件同步跳板
- `references/workflow-build.md` — 生成後主動接力:規劃 TASK.md → 一步步開發
- `scripts/render_puml.py` — PlantUML 編碼 + 自動抓圖出檔
