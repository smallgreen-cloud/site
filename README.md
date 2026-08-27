# SmallGreen 服務目錄

> **SmallGreen 是一套把開源小型專案整理成可自己部署、自己掌握、自己運行的服務目錄與標準。**

本站面向想把開源小型專案變成自己能運行服務的人。Registry 服務卡 YAML 是事實真相源，本站只 render，不另存服務資料。

[![site](https://github.com/smallgreen-cloud/site/actions/workflows/site.yml/badge.svg)](https://github.com/smallgreen-cloud/site/actions/workflows/site.yml)

- 目前入口：https://smallgreen-site.pages.dev
- 自訂網域：`smallgreen.cooperation.tw`（後續處理）
- 資料來源：[registry](https://github.com/smallgreen-cloud/registry)（cards/、onboarding/＋candidates/research-cases.yaml）
- 標準：[spec](https://github.com/smallgreen-cloud/spec) v0.2.1
- 網站規範：[DESIGN_AND_CONTENT_POLICY.md](DESIGN_AND_CONTENT_POLICY.md)（設計系統、雙語、SEO／AEO、公開內容邊界）
- 實作路線圖：[IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)（雙語資料、Evidence、聚合分析、CI 與部署）

## 網站如何呈現專案

每個專案先用人能理解的方式回答：這是什麼專案、解決什麼問題、適合誰、可以做什麼、部署前要準備什麼、開始前要知道哪些限制。接著再揭露架構、資料流、驗證證據、維護與退出方式。

## 服務卡的三個層級

- `Catalogued services`：已有 Registry 服務卡，依 Discovered、Community Verified、SmallGreen Ready 顯示目前證據層級。
- `First-party onboarding`：SmallGreen 自有專案先公開用途、適合對象、目前能力與上架待辦，但不冒充已驗證服務。
- `Research cases`：候選專案依上游 README 與 metadata 整理用途、架構與待辦，但不冒充服務卡或部署證據。

目前 onboarding 清單包含 HomeBox Edge、Free Second Brain（kb-vault）與 Meeting Capture Kit。研究案例則獨立放在 `cards.json` 的 `research_cases` 區塊；完成契約、真實部署驗收與 Evidence Pack 後，才轉入 `cards`。

首頁只展示少量已收錄服務，讓第一次造訪的人先理解 SmallGreen 與服務卡。完整服務、上架準備與研究案例集中在服務目錄，三個層級不混在一起。

目前先以 `https://smallgreen-site.pages.dev` 作為新版入口。Registry 更新後可由 `registry-updated` 事件或 Site workflow 的 `workflow_dispatch` 重建與部署；自訂網域待內容與案例穩定後再切換。

## 目前環境狀態（2026-08-27）

- 新版內容直接部署至既有 Cloudflare Pages 專案 `smallgreen-site`
- 目前入口以 Pages URL 產生 canonical、雙語路由、安全標頭、機器介面與研究案例詳頁
- 目前 render 13 張 verified service cards、3 個 first-party onboarding 與 31 個 research cases
- Google Search Console Domain property 已驗證；Sitemap 讀取成功並探索 52 個網頁
- Bing Webmaster 網站所有權已驗證；Sitemap 讀取成功並探索 52 個 URL
- Cloudflare AI Crawl Control 採監測模式；Search／Agent Access 與 Model Training 由版本化 `robots.txt` 分開治理
- 目前剩餘工作是累積 30 天 SEO／AEO 與聚合流量基線，不提前推估流量、排名或 AI 引用結果

相關變更：[PR #3 自動部署](https://github.com/smallgreen-cloud/site/pull/3)、[PR #4 自訂網域](https://github.com/smallgreen-cloud/site/pull/4)、[PR #5 Bing 驗證](https://github.com/smallgreen-cloud/site/pull/5)。

## Path A dogfooding

本站本身依 SmallGreen 標準部署（原生採用首例）：[.smallgreen/](.smallgreen/) 契約三檔、conformance CI、Evidence Pack 見 registry evidence/smallgreen-site/。純靜態、零 secrets、零 runtime 使用者資料；正式站已啟用 Cloudflare Web Analytics 聚合分析，不使用 cookie、使用者 ID或個人層追蹤。

## Build

```bash
python3 tools/build.py --registry <registry checkout>   # 產出 dist/
python3 -m unittest tests/test_site_architecture.py      # 雙語路由與 SEO 契約
npx wrangler pages deploy dist --project-name smallgreen-site --branch main
```

建置器會產生：

- 英文 canonical：`/`、`/manifesto/`、`/concepts/`、`/services/`、`/standard/`、`/evidence/`、`/faq/`
- 繁中版本：對應的 `/zh-tw/` 路徑
- 服務詳頁：`/services/{id}/` 與 `/zh-tw/services/{id}/`
- 舊 `/s/{id}.html` 相容 redirect
- `cards.json`、`llms.txt`、`llms-full.txt`、`robots.txt`、`sitemap.xml`、`feed.xml`

正式網域切換時用 `--base-url https://example.org` 注入 canonical base，不修改模板硬編碼。

正式部署不使用本機手動指令作為常態流程；合併至 `main` 後由 workflow 使用已設定的 GitHub Actions secrets 執行 Wrangler。任何 Cloudflare account ID、API token 或其他授權資料不得寫入版本庫或公開文件。

License：Apache-2.0（程式碼）；卡片內容隨 registry。
