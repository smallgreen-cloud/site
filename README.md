# SmallGreen Cloud 目錄站

> 經驗證的 Cloudflare 免費層小型開源服務目錄。**registry 服務卡 YAML＝真相源，本站只 render 不另存資料。**

[![site](https://github.com/smallgreen-cloud/site/actions/workflows/site.yml/badge.svg)](https://github.com/smallgreen-cloud/site/actions/workflows/site.yml)

- 線上：https://smallgreen-site-9pi.pages.dev
- 資料來源：[registry](https://github.com/smallgreen-cloud/registry)（cards/＋taxonomy.yaml）
- 標準：[spec](https://github.com/smallgreen-cloud/spec) v0.2.1
- 網站規範：[DESIGN_AND_CONTENT_POLICY.md](DESIGN_AND_CONTENT_POLICY.md)（設計系統、雙語、SEO／AEO、公開內容邊界）
- 實作路線圖：[IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)（雙語資料、Evidence、聚合分析、CI 與部署）

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

License：Apache-2.0（程式碼）；卡片內容隨 registry。
