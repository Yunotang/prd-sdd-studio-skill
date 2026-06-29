# prd-sdd-studio

CLI 版的 AI 軟體開發文件與開發工作室,給 **Claude Code / Codex** 使用的 skill。把專案構想一路帶到可運行的程式碼:

> 諮詢式對話 → 生成 **PRD** → 生成 **SDD** → 自動出**架構圖** → 規劃 **TASK.md** → 一步步**實際開發**

大腦是模型本身(Claude/Codex),**不呼叫任何外部 LLM API**。平台中立,Claude Code 與 Codex 皆可用。

## 流程架構圖

從啟動偵測到一步步開發的完整流程(出圖與本地工作流為所有功能共用的橫切流程):

![PRD/SDD Studio 流程架構圖](docs/diagrams/skill-workflow.png)

> 原始碼:[`docs/diagrams/skill-workflow.puml`](docs/diagrams/skill-workflow.puml);此圖即用本 skill 自帶的 `scripts/render_puml.py` 渲染。

## 功能

1. **啟動偵測 / 續傳** — 每次啟動先掃當前目錄,有半成品就接力、有現成 PRD/SDD 就讀懂確認後直接開發、要放棄就引導去乾淨新資料夾。**從不無視既有進度、從不擅自重來。**
2. **PRD 諮詢**(MVP / 完整專案兩模式)— 多輪對話釐清需求 → 生成 PRD + 概念架構圖。
3. **SDD 架構師**(完整 / 精簡 / 特定技術 / 互動式 四模式)— 依 PRD 生成 SDD + 技術架構圖(從 SDD 反推以保持圖文一致)。
4. **依 SDD 實際開發** — 把 SDD 的「實作路徑」拆成 `TASK.md`,一步步開發。
5. **開發 / 迭代閉環** — 每次修改後自動寫 `CHANGELOG.md`、**主動詢問本地 git 同步**、commit 後**半自動把改動回寫 PRD/SDD 並重出架構圖**,讓文件永遠最新。

## 結構

```
prd-sdd-studio/
├── SKILL.md                       # 主流程:啟動偵測 + 主選單 + 五大功能 + 出圖 + 本地工作流
├── references/
│   ├── startup-scan.md            # 啟動偵測與續傳路由
│   ├── prompts-consultant.md      # PRD 系統指令與生成模板
│   ├── prompts-architect.md       # SDD 系統指令、4 模式、架構圖 prompt
│   ├── workflow-local.md          # CHANGELOG + git 協議 + PRD/SDD 同步跳板
│   └── workflow-build.md          # 規劃 TASK.md → 一步步開發
└── scripts/
    └── render_puml.py             # PlantUML 編碼 + 自動抓圖,直接輸出 PNG/SVG(純標準庫,零依賴)
```

## 安裝

把整個 `prd-sdd-studio/` 資料夾放到你的 skills 目錄:

- **Claude Code**:`~/.claude/skills/prd-sdd-studio/`(Windows:`C:\Users\<你>\.claude\skills\prd-sdd-studio\`)
- **Codex**:放到 Codex 的 skills 目錄。

之後對 Claude/Codex 說「啟動 prd-sdd-studio」「幫我把這個構想做成 PRD」「依 SDD 開發專案」等即可觸發。

## 出圖需求

`scripts/render_puml.py` 用 Python 標準庫(`zlib` + `urllib`)把 PlantUML 原始碼編碼後,向公開的 `plantuml.com` 取回渲染好的圖檔。**需要網路連線**;離線時會保留 `.puml` 原始碼並回報。

## 由來

由原 Google AI Studio 的 PRD/SDD web app(Gemini 驅動)轉製:完整保留其提示詞與選項邏輯,把大腦換成 Claude/Codex、介面改為 CLI,並新增本地端的變更紀錄、git 同步、文件同步跳板與「依 SDD 實際開發」能力。
