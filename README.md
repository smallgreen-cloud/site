# SmallGreen Cloud 目錄站

> 經驗證的 Cloudflare 免費層小型開源服務目錄。**registry 服務卡 YAML＝真相源，本站只 render 不另存資料。**

[![site](https://github.com/smallgreen-cloud/site/actions/workflows/site.yml/badge.svg)](https://github.com/smallgreen-cloud/site/actions/workflows/site.yml)

- 線上：https://smallgreen-site.pages.dev
- 資料來源：[registry](https://github.com/smallgreen-cloud/registry)（cards/＋taxonomy.yaml）
- 標準：[spec](https://github.com/smallgreen-cloud/spec) v0.2.1

## Path A dogfooding

本站本身依 SmallGreen 標準部署（原生採用首例）：[.smallgreen/](.smallgreen/) 契約三檔、conformance CI、Evidence Pack 見 registry evidence/smallgreen-site/。純靜態、零 secrets、零 runtime 資料、零外部資源載入、零遙測。

## Build

```bash
python3 tools/build.py --registry <registry checkout>   # 產出 dist/index.html
npx wrangler pages deploy dist --project-name smallgreen-site --branch main
```

License：Apache-2.0（程式碼）；卡片內容隨 registry。
