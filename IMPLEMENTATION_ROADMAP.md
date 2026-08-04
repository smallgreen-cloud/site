# SmallGreen Cloud 網站實作路線圖

> 狀態：網站工程、正式部署與搜尋平台驗證已完成；30 天 SEO／AEO 分析基線持續累積
> 更新日期：2026-08-04
> 範圍：公開網站、SEO、AEO、Cloudflare Pages 與品質閘門
> 排除：論文與沙盒工作

## 目前上線基準（2026-08-04）

- 正式 canonical：`https://smallgreen.cooperation.tw`
- Cloudflare 技術備援：`https://smallgreen-site-9pi.pages.dev`
- 原始碼：GitHub 公開 repo `smallgreen-cloud/site`；`main` 為唯一正式部署來源
- 部署：GitHub Actions 完成契約檢核、網站建置、Browser QA、公開產物敏感資料掃描後，以 Wrangler 部署既有 Cloudflare Pages Direct Upload 專案 `smallgreen-site`
- 自動部署已由 PR #3 建立；自訂網域與 portable canonical 由 PR #4 完成；Bing HTML 驗證由 PR #5 完成
- 目前建置輸出：13 個服務、6 個概念、68 個 HTML 頁面；架構測試 20 項
- Cloudflare Web Analytics 已啟用，正式站 beacon、CSP 與 HTTP 200 已驗證
- Cloudflare AI Crawl Control 採監測模式；Managed robots.txt 關閉，避免以全站單一訊號覆蓋目前按 crawler 與路徑區分的授權政策
- Google Search Console Domain property 已驗證；`sitemap.xml` 狀態成功，已探索 52 個網頁
- Bing Webmaster 已以 HTML meta 驗證網站所有權；`sitemap.xml` 狀態成功，已探索 52 個 URL
- Bing DNS 驗證 CNAME 保留為第二驗證路徑；首頁 `msvalidate.01` meta 保留為主要可重現驗證路徑
- 尚未完成的外部結果只有資料成熟度：搜尋／AI 成效資料與正式站連續 30 天分析基線

| 里程碑 | PR | Main merge commit | 驗證結果 |
|---|---|---|---|
| GitHub Actions → Cloudflare Pages 自動部署 | [#3](https://github.com/smallgreen-cloud/site/pull/3) | `40ae3ab` | Main push 觸發建置與 production deploy |
| 自有 canonical 網域與 Pages 備援 | [#4](https://github.com/smallgreen-cloud/site/pull/4) | `3681d44` | 兩個 hostname HTTP 200；canonical 與 sitemap 只指向自有網域 |
| Bing Webmaster HTML 驗證 | [#5](https://github.com/smallgreen-cloud/site/pull/5) | `0d02416` | CI、Browser QA 與 production deploy 成功；Bing 顯示 Site addition successful |

## 執行順序

### Phase 1　雙語資料模型

狀態：已完成並通過 Registry／網站架構測試

- Registry 建立可驗證的 `i18n` 欄位或對應翻譯檔
- 中文原文與英文翻譯具有明確 source locale、review 狀態與 fallback 規則
- 網站建置器不得以逐項硬編碼字典作為長期真相源
- 新服務缺少必要語言時建置失敗並指出缺口
- 可見內容、JSON-LD、`cards.json`、`llms.txt` 使用相同語言資料

完成條件：新增服務不需修改網站程式碼即可產生完整中英文頁面

### Phase 2　概念與 Evidence 內容

狀態：已完成並通過公開產物與敏感資料檢查

- 概念頁補齊 Direct Answer、Why It Matters、Scope、Out of Scope、How It Works、Example、Machine-readable References、Evidence and Limitations、Related Concepts、Version
- Evidence 首頁成為可搜尋與比較的公開證據索引
- 服務頁呈現經清理的真實截圖、Evidence Pack、已知限制與 withheld 狀態
- Evidence 發布前執行 secret、識別碼、私人 URL、個資與截圖清理檢查

完成條件：每項公開宣稱都能回到版本、日期、commit 與 Evidence Pack

### Phase 3　Cloudflare 聚合分析與 SEO／AEO 基線

狀態：資料源與平台驗證均已完成；30 天基線尚在累積

採三個互補資料面，不建立使用者層追蹤

1. **Cloudflare Web Analytics**
   - 由 Pages 專案啟用自動注入
   - 收集聚合 page view、referrer、landing path 與 Core Web Vitals
   - 不使用 cookie、不建立使用者 ID、不加入自訂事件
   - CSP 明確允許 `static.cloudflareinsights.com` 與站內 `/cdn-cgi/rum`
2. **Cloudflare Edge Analytics／AI Crawl Control**
   - 觀察 request、熱門路徑、crawler、AI referral 與目的頁群組
   - 將 Search crawler、Agent access 與 Model Training crawler 分開報告
   - 不把 bot request 誤當成人類 page view
   - AI Crawl Control 保持監測，不啟用會覆蓋細緻路徑政策的 Managed robots.txt
3. **Google Search Console／Bing Webmaster**
   - 追蹤 impression、click、query、index coverage 與 sitemap 狀態
   - 搜尋曝光與點擊不得以 Cloudflare page view 推估
   - Google Domain property 與 Sitemap 已成功；目前探索 52 個網頁
   - Bing 網站所有權與 Sitemap 均已成功，已探索 52 個 URL

每週基線報告至少包含：

- 人類 page views 與 unique visits
- Organic search landing pages
- Search impressions、clicks、CTR 與平均排名
- AI crawler requests，依 crawler 類型與目的路徑分組
- AI referral sessions 與 landing pages
- `/concepts/`、`/services/`、`/evidence/` 的流量占比
- Core Web Vitals 與 404／redirect 異常

隱私邊界：只使用聚合資料，不公開原始請求紀錄，不收 query string、自訂事件、使用者 ID、部署紀錄或個人層行為。任何分析能力變更都必須先更新內容政策與資料流揭露。

完成條件：正式站連續收集 30 天基線，能分辨人類搜尋、AI referral 與 crawler access

目前唯一未達成條件是連續 30 天觀測期；不得在資料成熟前填入推估流量、排名或 AI 引用成效。

### Phase 4　CI QA 與安全標頭

狀態：已完成；52 條路由 × 3 個 viewport、無障礙、SEO、安全標頭與公開邊界檢查均通過

- 375／768／1280 px 瀏覽器檢查進入 CI
- 自動檢查 overflow、console error、鍵盤操作、focus、200% zoom 與 WCAG AA
- 驗證 JSON-LD、canonical、hreflang、sitemap、feed 與內部連結
- 建立 `_headers`、`_redirects` 與 `404.html`
- CSP 同時滿足零非必要第三方資源與 Cloudflare Web Analytics 必要端點
- 公開建置輸入執行 secret 與敏感資料掃描

完成條件：PR 無法繞過瀏覽器、無障礙、SEO、安全與公開邊界閘門

### Phase 5　正式部署驗證

狀態：已完成；正式 canonical 端點 `https://smallgreen.cooperation.tw` 與 Cloudflare 備援端點已通過路由、雙語 404、machine-readable outputs、安全標頭與 Web Analytics beacon 驗證

- 使用自有網域 `smallgreen.cooperation.tw` 作 canonical base URL，Cloudflare Pages 網域保留為技術備援
- Cloudflare Pages production build 成功
- 公開首頁、語言路由、服務頁、machine-readable outputs 與 404 行為驗證
- 驗證 HTTP status、security headers、redirect、sitemap 與 Web Analytics beacon
- Sitemap 已提交至 Google Search Console 與 Bing Webmaster；兩者均已成功讀取並探索 52 個 URL
- 記錄可回復的前一個 Pages deployment

完成條件：正式端點通過完整 smoke test，且 SEO／AEO 與聚合分析開始建立基線
