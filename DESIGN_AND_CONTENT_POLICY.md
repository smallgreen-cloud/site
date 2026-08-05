# SmallGreen Cloud 網站設計與內容開放政策 v1.0

> **狀態：已定稿並套用至正式網站；外部搜尋平台驗證已完成，長期分析基線依路線圖追蹤。**
> 適用範圍：SmallGreen Cloud 官方網站、服務卡詳頁、概念頁、規格導覽、公開資料介面及其衍生分享素材。
> 真相源分工：Schema、契約、測試及 Evidence Pack 原始資料以 GitHub 為準；網站負責可讀呈現、搜尋發現與 Agent 導覽。

## 一、網站角色

SmallGreen Cloud 網站不是一般 SaaS Landing Page，也不是把 GitHub README 換成漂亮版面。網站有四個責任：

1. 讓人理解 SmallGreen Cloud 建立的是 **Small Software 的所有權與部署層**。
2. 讓使用者比較、選擇並部署經驗證的小型開源服務。
3. 讓搜尋引擎與 AI Agent 找到 canonical definitions、Service Cards、Deployment Contracts 與 Conformance Evidence。
4. 讓每一項驗證宣稱都能追溯到版本、commit、日期與 Evidence Pack。

正式定位文字：

> **We are building the ownership and deployment layer for Small Software.**
> **我們正在建立小型軟體的所有權與部署層。**

互動分工：

> **Humans read Service Cards. Agents read Deployment Contracts.**
> **人看服務卡，Agent 看部署契約。**

## 二、設計方向

### 2.1 主方向：Verified Field Guide

網站採「**開源基礎設施的驗證型錄 × 現代技術期刊**」風格。視覺應先傳達可信、可查證、可執行，再傳達 green。

核心特徵：

- 暖白紙張底色、森林墨色文字、稀少而明確的綠色狀態色。
- 編輯式大標題、清楚格線、索引編號、版本、日期與驗證章。
- 真實截圖、契約生成架構圖與 Evidence Pack 是主要視覺。
- 首頁可局部使用不等寬模組，但不得把所有內容包成相同 Bento 卡片。
- 技術區可借用 Protocol Console 語言；社群案例可有少量 Green Commons 的溫度，但不得改變全站信任基調。

一句驗收描述：

> 看起來像一份值得信任的開源驗證型錄，而不是又一個綠色 SaaS Landing Page。

### 2.2 禁止的視覺捷徑

- 不使用滿版深綠、葉子、地球、雲朵或資料中心 stock image 代表永續。
- 不使用 AI 生成圖冒充服務畫面、架構或驗證證據。
- 不使用黑底、紫藍霓虹、發光邊框與全站 monospace 製造「AI 工具感」。
- 不使用玻璃擬態、厚重陰影、過度圓角、漸層文字或無意義指標圖。
- 不把每個段落做成卡片；卡片只用於需要比較、選擇或操作的獨立內容。
- 不讓動畫遮蔽正文、延遲操作或成為理解內容的必要條件。

## 三、色彩系統

色彩採 Cloud Standard 系統。中性白與墨色負責閱讀，品牌綠代表 SmallGreen，科技藍負責連結與 Agent 操作，狀態綠只表示驗證通過。

| Token | 用途 | Hex | 建議 OKLCH 起點 |
|---|---|---|---|
| `--paper` | 主背景 | `#F7F8F6` | `oklch(98% 0.005 140)` |
| `--moss-surface` | 次背景 | `#EEF1ED` | `oklch(95% 0.01 145)` |
| `--forest-ink` | 主要文字 | `#17201B` | `oklch(23% 0.02 145)` |
| `--olive-muted` | 次要文字 | `#53615A` | `oklch(48% 0.02 155)` |
| `--fern` | 品牌主綠、主要 CTA | `#176B4D` | `oklch(48% 0.1 160)` |
| `--cloud-blue` | 連結、Agent 操作 | `#235FA4` | `oklch(48% 0.13 255)` |
| `--sprout` | 驗證通過 | `#3F8A62` | `oklch(58% 0.1 155)` |
| `--mineral` | 注意、待確認 | `#B7791F` | `oklch(59% 0.12 75)` |
| `--brick` | 失敗、阻擋 | `#B94735` | `oklch(53% 0.15 30)` |
| `--dry-moss-line` | 邊界、格線 | `#CCD3CE` | `oklch(85% 0.015 155)` |

使用規則：

- 約 76% 中性白與霧灰、16% 墨色與格線、5% 品牌綠、2% 科技藍、1% 狀態色。
- 科技藍只用於互動與機器入口，不與品牌綠競爭大面積視覺主導權。
- 驗證綠不得作為大面積背景或裝飾色。
- 驗證狀態不可只靠色彩；必須同時有文字、圖示或形狀。
- 正文對比至少 WCAG 2.2 AA `4.5:1`；大型文字及 UI 元件至少 `3:1`。
- 鍵盤焦點使用至少 2 CSS px 的清楚外框，不以微弱背景變色代替。
- 第一版以 light theme 為唯一正式主題；dark theme 不是上線必要條件。

## 四、字體與排版

### 4.1 字體角色

| 內容 | 英文 | 繁中 | 原則 |
|---|---|---|---|
| Display／文章標題 | Newsreader 或 Instrument Serif | Noto Serif TC 或系統宋體 fallback | 建立出版與標準權威感 |
| 正文／UI | Instrument Sans | Noto Sans TC、PingFang TC、系統 sans | 清晰、適合長文與操作 |
| 程式碼／機器資料 | IBM Plex Mono | mono 搭配繁中 sans fallback | 只用於 JSON、命令、ID、版本 |

載入政策：

- 英文字型可自託管 WOFF2；禁止 runtime 向第三方字型服務請求。
- 中文正文優先系統字型，避免整包 CJK webfont 阻塞首屏。
- 若使用中文 serif webfont，必須 subset 並量測字型大小與 layout shift。
- 字型載入失敗時仍須保有可讀 hierarchy，不得依賴特定字型才能正常排版。

### 4.2 尺寸與文字節奏

- 正文最小 `1rem`；繁中長文建議 `1.0625rem`，行高约 `1.7–1.8`。
- 長文英文 measure 約 `60–68ch`；繁中約 34–38 個中文字。
- 標題使用 `clamp()` 流體縮放；按鈕、標籤與資料欄位維持穩定尺寸。
- 所有標題與正文套用 `text-wrap: pretty` 及長英文 fallback；這是一般換行的安全網，不取代編輯式標題的語意斷行。
- 中文網頁採掃讀節奏：短句、具體 label、適度換行；避免作文式長句與大量斜線。
- 繁中顯示文案以換行與留白取代作文式標點；標題、導語、卡片、步驟與 FAQ 禁用 `。`、`，`、`；`、`：`、`！`、`？`。`、`只保留於真正並列，URL、版本、程式碼與正式產品名稱保留必要技術符號。
- 大、中、小標題（`h1`–`h3`）一律不帶作文式標點，中英文皆同；技術識別碼或正式名稱本身含有的符號除外。
- 標題先以完整語意單元分行，不為追求等字數破壞句法；`的`、`與`、`和`、`或`、`而`、`及`、`之` 不得孤立於行首或行尾。
- Small Software、Deploy Agent、Service Card、Deployment Contract、Evidence Pack、Cloudflare Pages 等混合語言術語視為不可拆的原子單元。
- 大標題必須在內容模型中指定為一行或兩行；若兩行仍不自然，先重寫標題，不以縮小字級或任意第三行補救。
- 字數只能初估寬度；所有指定分行都要用實際字型、容器與 `375`、`768`、`1280px` viewport 驗證，確認每個語意行不發生二次換行。
- 標準例：`我們正在建立`／`小型軟體的所有權與部署層`；`Small Software`／`核心定義`；`小型軟體應該被擁有`／`不該被租用`。
- 資料數字使用 tabular numbers；code 關閉易混淆的 ligature。

## 五、版面與元件

### 5.1 全站骨架

桌機主容器約 `72–80rem`，採 mobile-first；以 4px spacing base 建立 4、8、12、16、24、32、48、64、96px 節奏。

主要導覽：

```text
SmallGreen Cloud | Concepts | Services | Standard | Evidence | Blog | EN / 繁中
```

首頁資訊順序：

1. Manifesto：建立什麼。
2. How it works：Service Card → Deployment Contract → Agent → Evidence。
3. Trust model：為什麼可信、哪些不能宣稱。
4. Verified services：服務探索與比較。
5. Standard／Evidence：規格版本與公開證據入口。
6. Community／Research：案例、更新與研究，不與規格正文混合。

### 5.2 服務目錄

- 桌機採可掃描、可排序的索引式列表；名稱、用途、驗證日期、資源預算與相容 Agent 可直接比較。
- 手機改為垂直服務卡，不把桌機表格縮小或依賴橫向捲動。
- 篩選條件必須能用鍵盤操作，並在 URL 或可分享狀態中重現。
- 卡片牆不是首頁第一屏；使用者先理解標準與信任模型，再進入服務選擇。

### 5.3 服務詳頁

固定資訊順序：

1. 名稱、用途與適合對象。
2. 真實服務截圖；無 UI 時顯示由契約機械生成的架構圖。
3. Evidence Strip：部署、驗收、teardown、外連與版本狀態。
4. 「交給 Agent 安裝」入口。
5. 資料流、外部服務與遙測揭露。
6. 免費層作為 Resource Budget 的限制與降級行為。
7. 相容 Agent、驗證 commit、日期與 spec 版本。
8. Evidence Pack 時間線。
9. Deployment Contract 與 machine-readable references。
10. 已知限制、未驗證項目與退場方式。

Evidence Strip 是品牌辨識元件，格式示意：

```text
DISCOVERED  ✓ DEPLOYED  ✓ ACCEPTANCE  ✓ TEARDOWN  ✓ NO UNDECLARED EGRESS
Spec v0.2.1 · Verified 2026-08-03 · Commit 8a0372a
```

### 5.4 圖像政策

公開網站只接受：

1. Evidence Pack 可追溯的真實部署截圖。
2. 由 Deployment Contract／Service Card 機械生成的架構與資料流圖。
3. 少量品牌結構圖、圖示、索引標記與經人工確認的內容插圖。

任何示意圖必須明示為示意；不得讓 mockup、合成資料或 AI 圖看起來像驗證證據。

## 六、互動、RWD 與無障礙

- 只使用解釋狀態變化的動畫：流程進度、列表展開、Evidence 時間線。
- 一般轉場 `180–350ms`，只動 `transform` 與 `opacity`，並支援 `prefers-reduced-motion`。
- 互動目標至少 44×44 CSS px；hover 不能是唯一提示。
- 所有操作支援鍵盤；focus 順序與視覺順序一致。
- 375、768、1280 px 三種 viewport 為每次重大視覺修改的最低 QA。
- 三種 viewport 都要分別檢查整頁水平 overflow 與指定標題行的 `scrollWidth <= clientWidth + 1`；Grid／Flex 裁切不會必然形成整頁捲軸。
- 中文寬度不得用 `ch` 當作中文字數；以實際 production font stack、容器與 rendered width 驗證。
- 每次重大視覺修改必須在部署前查看 production build 截圖，部署後再查看正式網址截圖。
- 200% zoom 不得遺失內容或操作。
- 中文標題檢查孤字行；複雜表格在 mobile 改為 vertical card／definition list。
- 圖片有具體 alt；裝飾圖使用空 alt；架構圖另有可讀文字摘要。

## 七、雙語政策

英文為國際主版本，繁中完整覆蓋核心使用旅程：

```text
/                                英文首頁
/concepts/deploy-agent/          英文概念頁
/services/sink/                  英文服務卡
/zh-tw/                          繁中首頁
/zh-tw/concepts/deploy-agent/    繁中概念頁
/zh-tw/services/sink/            繁中服務卡
```

雙語規則：

- 導覽提供 `English | 繁體中文`，切換到同一內容的另一語言版本。
- 不依 IP、瀏覽器語言或 cookie 強制轉址。
- 每個翻譯對有各自 canonical，並互列 `hreflang="en"`、`hreflang="zh-Hant-TW"` 與 `x-default`。
- 首頁、Manifesto、核心 Concepts、FAQ、Glossary、服務卡與信任說明必須雙語。
- Schema、Deployment Contract、AGENTS.md、API／MCP schema、Evidence Pack 原始資料維持英文或機器格式的單一真相源；繁中提供解釋與連結，不另維護第二份規格。
- Blog 與研究採選擇性翻譯；沒有完整正文翻譯就不建立語言替身頁或 `hreflang`。

## 八、SEO／AEO 與 Agent-first

- 每頁只有一個 canonical URL、明確 title、description、H1、作者／組織、更新日期與版本。
- 核心概念採固定 URL；Blog 只能討論與連回 canonical concept，不另立競爭定義。
- 概念頁依序包含 Direct Answer、Why It Matters、Scope、Out of Scope、How It Works、Example、Machine-readable References、Evidence and Limitations、Related Concepts、Version。
- 可見正文、JSON-LD、Registry JSON 與 machine-readable contract 必須一致。
- 服務卡使用與可見內容一致的 `SoftwareApplication`／`WebApplication`；概念頁使用 `DefinedTerm`／`TechArticle`；Evidence Dataset 使用 `Dataset`。
- 提供 `sitemap.xml`、RSS／Atom、`llms.txt`、`cards.json`、穩定 schema URL 與可爬取的 server-rendered HTML。
- 禁止大量建立低價值薄頁、隱藏關鍵字、偽造評分、宣稱模型已收錄或保證 AI 推薦。
- AEO 的成功標準是 Agent 能找到正確定義、契約與證據，不是堆疊 AI crawler 名稱。

## 九、Cloudflare Pages 與公開邊界

### 9.1 部署現況

本站目前以 Cloudflare Pages 靜態站部署，專案設定為：

```toml
name = "smallgreen-site"
pages_build_output_dir = "dist"
```

正式 canonical 端點為 `https://smallgreen.cooperation.tw`，由使用者控制網域身份；`https://smallgreen-site-9pi.pages.dev` 保留作 Cloudflare 技術備援，不作搜尋主網址。網站建置期讀取 Registry YAML，產生靜態 HTML、JSON、文字索引與 sitemap；runtime 不儲存使用者資料、無登入、無 cookie、無個人層遙測。canonical base URL 由建置設定注入，不綁定託管平台配發的子網域。

GitHub `smallgreen-cloud/site` 的 `main` 是正式部署真相源。每次主線更新先通過契約檢核、雙語／SEO 架構測試、三種 viewport Browser QA、無障礙檢查與公開產物敏感資料掃描，再由 GitHub Actions 以 Wrangler 部署 Cloudflare Pages。Direct Upload 專案不轉換成 Cloudflare 原生 Git integration；自動部署責任明確留在版本庫 workflow。

所有 CSS／JS 必須使用內容 hash 或等效的版本化 URL，避免新 HTML 與舊資產混用。部署完成後須同時驗證正式自訂網域與 Pages 備援網域，確認 HTTP 200、HTML 引用本次資產版本，並以實際畫面檢查標題裁切、Grid／Flex 重疊與主要互動區。部署指令成功但 production 畫面未驗證時，不得宣告完成。

### 9.2 核心原則

> **公開網站不等於所有內部資料都公開。公開的是標準、可驗證事實與經清理的證據，不公開的是身份、秘密、私人運行資料與會增加風險的細節。**

是否公開由內容分類決定，不由「檔案已在 repo」「技術上可產生頁面」或「Pages 可以託管」決定。

### 9.3 內容分級

| 等級 | 定義 | 例子 | 網站處理 |
|---|---|---|---|
| **P0 Public Canonical** | 為標準採用、理解與執行所必需 | Manifesto、Concepts、公開 Spec、Service Cards、Schema、驗證等級、公開 Registry 索引、授權與治理政策 | 全文公開、可索引、穩定 URL、明確授權 |
| **P1 Public Evidence** | 支持公開宣稱且完成清理的證據 | 驗證 commit、日期、測試結果、資源類型、經清理的 Evidence Pack、真實截圖、teardown 結果、已知限制 | 公開且可稽核；發布前通過敏感資料掃描 |
| **P2 Public Summary** | 有公共價值，但原始內容含操作或身份風險 | 失敗案例、維護事件、資安修復、實驗彙總、使用回饋 | 公開摘要與必要證據；移除帳號、路徑、日誌細節及可識別資料 |
| **R0 Restricted** | 不應進入公開網站或公開建置輸入 | token、secret、account／zone／resource ID、私人 repo 內容、使用者資料、IP、email、未公開部署 URL、完整營運 log、內部 session、未協調漏洞、未定稿研究 | 不複製、不 render、不建立索引；僅留在授權環境 |

### 9.4 永不公開

- API token、密碼、private key、cookie、session、OAuth 憑證與任何可重建授權的資料。
- Cloudflare account／zone／resource ID、私人服務 URL、GitHub fine-grained token scope 實值。
- 使用者部署紀錄、個資、私人服務內容、會議、名片、聯絡人、檔案與資料庫內容。
- 未協調揭露的漏洞、可直接利用的攻擊步驟或尚未修補的敏感架構細節。
- 私人 repo 原文、內部 agent transcript、debug log、成本帳務與未定稿研究手稿。
- 任何不能確認授權來源的圖片、文字、商標素材或第三方資料集。

### 9.5 Evidence 發布檢查

每個網站建置輸入在公開前至少檢查：

1. 有明確來源與授權。
2. 不含 secret、識別碼、私人 URL 或個資。
3. 宣稱能追溯到 spec version、verified commit、日期和 Evidence Pack。
4. 截圖已清除帳號、email、token、私有名稱與瀏覽器個人資訊。
5. 失敗與限制如實呈現，不因行銷目的省略。
6. 原始證據不能公開時，改發可驗證摘要並說明 withheld 的原因。

### 9.6 Crawler 與授權

Crawler 分為三種控制面：

1. **Search／即時引用**：預設允許搜尋引擎、OAI-SearchBot、ChatGPT-User、Claude-SearchBot、Claude-User 等索引、摘要與使用者發起的讀取。
2. **Agent 執行**：公開允許讀取文件、Service Card、Registry JSON、Schema 與唯讀 MCP；任何寫入、部署或私有資源存取仍需使用者自行授權。
3. **Model Training**：依內容授權決定，不與 Search／Agent Access 綁定。規格、Schema、Glossary、公開教學與 Reference Implementation 可依其開放授權允許；P2 摘要與受限制內容不得因 crawler 可到達而視為授權訓練。

`robots.txt` 是存取偏好，不是授權文件。授權仍以每個 repo／資料集的 LICENSE、頁面聲明和內容分級為準。Search crawler 與 Training crawler 必須能分開設定；不得用「全部 Allow」取代政策判斷。

Cloudflare AI Crawl Control 目前只用於觀察與分類 crawler。Managed robots.txt 維持關閉，因其全站單一訓練訊號會覆蓋本站按 crawler 與路徑區分的政策；公開站產生的 `robots.txt` 才是目前 crawler 存取偏好的可版本化真相源。

### 9.7 分析與隱私

- 第一版納入 Cloudflare Web Analytics、Cloudflare 邊緣／AI crawler 聚合指標、Google Search Console 與 Bing Webmaster，作為 SEO／AEO 的必要驗證閉環。
- Cloudflare Web Analytics 只允許 Pages 自動注入的官方 beacon；不使用 cookie、使用者 ID、自訂事件或個人層追蹤。
- Google Search Console 與 Bing Webmaster 均已驗證正式網域並成功讀取 Sitemap，各自探索 52 個 URL；搜尋與 AI 成效報表仍需等待資料累積。
- 搜尋成效、AI referral、crawler access 與一般 page view 必須分開解讀，不得把 bot request 當成人類流量，也不得以 page view 推估 search impression。
- 只使用平台彙總資料，不把個人層事件、query string 或原始請求紀錄回寫 Registry 或 Evidence Dataset。
- 若新增任何分析端點，必須先更新本政策、資料流揭露、`external_services` 與 conformance 檢查；dashboard 本身不構成告知。
- 詳細執行順序與完成條件見 [`IMPLEMENTATION_ROADMAP.md`](IMPLEMENTATION_ROADMAP.md)。

## 十、實作與 Review Gate

網站 PR 至少通過：

- 決定性建置：相同 Registry 輸入產出相同 HTML／JSON。
- HTML 結構、內部連結、canonical、`hreflang`、sitemap 與 JSON-LD 驗證。
- WCAG AA contrast、鍵盤、focus、alt、landmark 與 200% zoom 檢查。
- 375／768／1280 px 截圖、整頁 overflow、標題行 clipping 與 Grid／Flex 重疊檢查。
- production build 與正式網址各做一次視覺驗證；正式 HTML 的 CSS／JS 資產版本必須與本次 build 一致。
- 中文孤字行、英文長 token、表格 mobile 替代版檢查。
- 零非必要外部 runtime script、style、font、image 請求；唯一分析例外為政策明列的 Cloudflare Web Analytics 官方 beacon，並須通過 CSP 與資料流揭露檢查。
- 公開內容敏感資料與 secret 掃描。
- 可見內容、JSON-LD、cards.json 與 Registry 真相源一致性。
- 動畫在 `prefers-reduced-motion` 下停用或降級。

## 十一、治理

- 本文件是網站設計與內容開放的 review baseline；需外部帳號、自訂網域或觀測期間才能完成的項目由 roadmap 明確標示，不得提前宣稱完成。
- 新專案加入網站必須先通過 Registry 的 [新專案發布標準](https://github.com/smallgreen-cloud/registry/blob/main/PROJECT_PUBLISHING_STANDARD.md)；網站不得建立繞過 Registry 的手工專案頁。
- 核心定位、色彩角色、Evidence Strip、雙語 URL、內容分級與公開邊界屬穩定規則。
- 微調 spacing、元件形式或字型時可在不破壞上述規則下演進。
- 變更公開邊界、crawler 授權、驗證語意或 canonical wording 必須先修改本文件，再修改網站。
- 若網站呈現與 GitHub 機器真相源衝突，以 versioned Schema、Registry YAML／JSON、測試與 Evidence Pack 為準，並修正網站。

---

文件版本：v1.0
定稿日期：2026-08-03
現況更新：2026-08-04
Owner：SmallGreen Cloud maintainers
