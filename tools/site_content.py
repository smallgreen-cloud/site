"""Bilingual editorial copy for the static site.

Facts about services remain owned by registry YAML. This module only owns site
navigation, canonical concept copy, and English translations of service
one-liners. A missing translation is a build error rather than a silent fallback.
"""

LANGS = ("en", "zh-tw")

NAV = {
    "en": {
        "manifesto": "Manifesto", "concepts": "Concepts", "services": "Services",
        "standard": "Standard", "evidence": "Evidence", "faq": "FAQ",
        "language": "繁體中文",
    },
    "zh-tw": {
        "manifesto": "宣言", "concepts": "核心概念", "services": "服務目錄",
        "standard": "標準", "evidence": "驗證證據", "faq": "常見問題",
        "language": "English",
    },
}

HOME = {
    "en": {
        "eyebrow": "01 / OWNERSHIP, NOT ANOTHER PLATFORM",
        "title": "The ownership and deployment layer for Small Software",
        "lede": "Community-verified, serverless-first, resource-budgeted software you can run in your own account.",
        "primary": "Explore verified services",
        "secondary": "Read the standard",
        "how_label": "02 / THE TRUST PATH",
        "how_title_lines": ["Humans read Service Cards", "Agents read Deployment Contracts"],
        "services_label": "03 / VERIFIED SERVICE INDEX",
        "services_title": "Choose by evidence not by promise",
        "services_title_lines": ["Choose by evidence", "Not by promise"],
        "services_text": "Every listing exposes its resource budget, data flow, verification date and known limits.",
        "trust_label": "04 / PUBLIC BY DESIGN",
        "trust_title": "The standard is open Your deployment stays yours",
        "trust_title_lines": ["The standard is open", "Your deployment stays yours"],
        "trust_text": "We publish schemas, service cards and sanitized evidence. We do not collect deployment telemetry or user data.",
    },
    "zh-tw": {
        "eyebrow": "01 / 擁有，而不是再多一個平台",
        "title": "我們正在建立小型軟體的所有權與部署層",
        "title_lines": ["我們正在建立", "小型軟體的所有權與部署層"],
        "lede": "經社群驗證、Serverless 優先、受資源預算約束，部署在你自己的帳號。",
        "primary": "探索已驗證服務",
        "secondary": "閱讀標準",
        "how_label": "02 / 信任路徑",
        "how_title_lines": ["人看服務卡", "Agent 看部署契約"],
        "services_label": "03 / 驗證服務索引",
        "services_title": "依證據選擇 不依承諾選擇",
        "services_title_lines": ["依證據選擇", "不依承諾選擇"],
        "services_text": "每個條目公開資源預算、資料流、驗證日期與已知限制。",
        "trust_label": "04 / 公開是設計，不是附加功能",
        "trust_title": "標準保持開放 部署仍由你擁有",
        "trust_title_lines": ["標準保持開放", "部署仍由你擁有"],
        "trust_text": "公開 Schema、服務卡與經清理的證據；不收集部署遙測或使用者資料。",
    },
}

STATIC_PAGES = {
    "manifesto": {
        "en": {
            "label": "MANIFESTO", "title": "Small Software should be owned not rented",
            "title_lines": ["Small Software should be owned", "Not rented"],
            "lede": "AI made software easier to create. It did not make deployment, trust or maintenance disappear.",
            "sections": [
                ("The gap", "Small tools are repeatedly rebuilt, then abandoned when operating them becomes the hard part. SmallGreen Cloud turns deployment and maintenance into an explicit, testable contract."),
                ("The position", "Free tier is a resource budget, not a discount strategy. Serverless-first means idle infrastructure can disappear, while the user keeps control of code, data and exit."),
                ("The promise", "No phone-home telemetry. No verification by assertion. Every public claim points to a versioned contract and evidence."),
            ],
        },
        "zh-tw": {
            "label": "宣言", "title": "小型軟體應該被擁有 不該被租用",
            "title_lines": ["小型軟體應該被擁有", "不該被租用"],
            "lede": "AI 降低了開發門檻，卻沒有讓部署、信任與維護自動消失。",
            "sections": [
                ("斷層", "小工具被反覆重造，又在真正需要運營時遭到放棄。SmallGreen Cloud 把部署與維護轉成明確、可測試的契約。"),
                ("立場", "免費額度是一項資源預算，不是低價策略。Serverless 優先讓閒置基礎設施歸零，同時讓使用者保有程式碼、資料與退場權。"),
                ("承諾", "不放入 phone-home 遙測，不靠自我宣告完成驗證。每一項公開主張都連回版本化契約與證據。"),
            ],
        },
    },
    "standard": {
        "en": {
            "label": "STANDARD", "title": "Contract gate and human judgment form a feedback loop",
            "title_lines": ["Contract gate and human judgment", "Form a feedback loop"],
            "lede": "SmallGreen Spec defines what can be checked before deployment, during acceptance and at teardown.",
            "sections": [
                ("Profiles", "Small App and Pipeline profiles define eligible resource and execution patterns."),
                ("Deployment contracts", "Profile, acceptance and maintenance contracts turn repository facts into machine-readable instructions."),
                ("Conformance", "Validators and Evidence Packs decide pass or fail. The Agent guides the process but is never the judge."),
            ],
        },
        "zh-tw": {
            "label": "標準", "title": "契約 閘門 人形成回饋迴圈",
            "title_lines": ["契約 閘門 人", "形成回饋迴圈"],
            "lede": "SmallGreen Spec 定義部署前、驗收中與移除後可以被機械檢查的條件。",
            "sections": [
                ("Profile", "Small App 與 Pipeline Profile 定義可接受的資源與執行模式。"),
                ("部署契約", "Profile、acceptance、maintenance 三份契約把 Repo 事實轉成機器可讀的指令。"),
                ("Conformance", "Validator 與 Evidence Pack 決定通過或失敗。Agent 引導流程，但永遠不是裁判。"),
            ],
        },
    },
    "evidence": {
        "en": {
            "label": "EVIDENCE", "title": "Verification is a public trail not a badge",
            "title_lines": ["Verification is a public trail", "Not a badge"],
            "lede": "A result is only as useful as its commit, environment, acceptance checks and teardown record.",
            "sections": [
                ("What is public", "Versioned Service Cards, sanitized Evidence Packs, verification dates, known limits and machine-derived architecture diagrams."),
                ("What stays private", "Secrets, account identifiers, private URLs, user data, operational logs and uncoordinated vulnerability details."),
                ("Append-only history", "New runs supersede older evidence without rewriting history, so stale claims remain visible and reviewable."),
            ],
        },
        "zh-tw": {
            "label": "驗證證據", "title": "驗證是一條公開軌跡 不是一枚徽章",
            "title_lines": ["驗證是一條公開軌跡", "不是一枚徽章"],
            "lede": "結果必須連回 commit、環境、驗收條件與 teardown 紀錄才有意義。",
            "sections": [
                ("公開內容", "版本化服務卡、經清理的 Evidence Pack、驗證日期、已知限制與機械生成架構圖。"),
                ("私人邊界", "Secret、帳號識別、私人 URL、使用者資料、營運 log 與未協調揭露的漏洞細節。"),
                ("Append-only 歷史", "新驗證以 supersedes 接續舊證據，不重寫歷史，讓過期主張仍可辨識與查核。"),
            ],
        },
    },
    "analytics": {
        "en": {
            "label": "ANALYTICS", "title": "Aggregate measurement without user profiles",
            "lede": "SEO and AEO need evidence but not personal tracking",
            "sections": [
                ("What we measure", "Aggregate page views landing paths referrers Core Web Vitals search performance and crawler access"),
                ("What we do not collect", "No cookies user identifiers custom events query strings deployment records or personal behavior profiles"),
                ("How sources differ", "Cloudflare Web Analytics measures visits and performance Cloudflare Edge Analytics and AI Crawl Control measure crawlers while Search Console and Bing Webmaster measure search impressions clicks and indexing"),
            ],
        },
        "zh-tw": {
            "label": "聚合分析", "title": "量測成效 不建立使用者檔案",
            "title_lines": ["量測成效", "不建立使用者檔案"],
            "lede": "SEO 與 AEO 需要證據 不需要個人追蹤",
            "sections": [
                ("量測內容", "聚合 page view landing path referrer Core Web Vitals 搜尋成效與 crawler access"),
                ("不收集內容", "不使用 cookie 使用者 ID 自訂事件 query string 部署紀錄或個人行為檔案"),
                ("資料面分工", "Cloudflare Web Analytics 量測造訪與效能 Edge Analytics 與 AI Crawl Control 量測 crawler 搜尋曝光 點擊與索引則由 Search Console 與 Bing Webmaster 提供"),
            ],
        },
    },
}

CONCEPTS = {
    "small-software": {
        "en": ("What is Small Software", "Focused software with a bounded purpose, small operational footprint and an explicit path to ownership and exit."),
        "zh-tw": ("什麼是 Small Software", "用途聚焦、運營足跡小，並具有明確所有權與退場路徑的軟體。"),
    },
    "ownership-and-deployment-layer": {
        "en": ("The ownership and deployment layer", "The contracts, evidence and tools that turn an open-source repository into an owned and maintainable service."),
        "zh-tw": ("所有權與部署層", "把開源 Repo 轉換成使用者自己擁有且可維護服務的契約、證據與工具層。"),
    },
    "deploy-agent": {
        "en": ("What is a Deploy Agent", "A guide that follows a verified contract to deploy, test and maintain a service in the user's account."),
        "zh-tw": ("什麼是 Deploy Agent", "依照已驗證契約，在使用者帳號中部署、測試與維護服務的引導者。"),
    },
    "service-card": {
        "en": ("What is a Service Card", "The human-readable view of purpose, resource budget, data flow, verification and limitations."),
        "zh-tw": ("什麼是服務卡", "以人能理解的方式呈現用途、資源預算、資料流、驗證與限制。"),
    },
    "deployment-contract": {
        "en": ("What is a Deployment Contract", "Machine-readable facts and checks for profile, acceptance and maintenance."),
        "zh-tw": ("什麼是部署契約", "描述 Profile、驗收與維護事實及檢查條件的機器可讀文件。"),
    },
    "resource-budget": {
        "en": ("Free tier as a resource budget", "Free tier is treated as a measurable operating constraint, with limits and fallback behavior made explicit."),
        "zh-tw": ("免費額度是一項資源預算", "把免費額度視為可量測的運營限制，明示上限與降級行為。"),
    },
}

CONCEPT_DETAILS = {
    "small-software": {
        "en": {
            "why": "Small tools are easy to create but often abandoned when deployment ownership and maintenance remain implicit.",
            "how": "Bound the purpose declare the resource budget publish the deployment contract and keep a tested exit path.",
            "example": "A URL shortener with one deployment contract one evidence trail and a complete teardown path is Small Software.",
            "evidence": "The label describes scope and operability only. It does not prove security reliability or community adoption.",
        },
        "zh-tw": {
            "why": "小工具容易建立 卻常因部署 所有權與維護責任不明而被放棄",
            "how": "限制用途 明示資源預算 公開部署契約 並保留經測試的退場路徑",
            "example": "具備單一部署契約 公開證據與完整移除路徑的短網址服務就是 Small Software",
            "evidence": "這個名稱只描述範圍與可運營性 不代表安全 穩定或社群採用",
        },
    },
    "ownership-and-deployment-layer": {
        "en": {
            "why": "Source code access does not by itself give a person a reproducible deployment or an accountable maintenance path.",
            "how": "Connect the repository to contracts an Agent guide mechanical gates public evidence and a reversible deployment.",
            "example": "A user can move from a Service Card to a verified contract deploy in their account and later remove every resource.",
            "evidence": "Ownership is limited to the deployed instance and data under the user's account and remains subject to upstream licenses.",
        },
        "zh-tw": {
            "why": "取得原始碼不等於擁有可重現部署與可追責的維護路徑",
            "how": "把 Repo 連到契約 Agent 引導 機械閘門 公開證據與可逆部署",
            "example": "使用者能從服務卡進入已驗證契約 在自己的帳號部署 最後完整移除資源",
            "evidence": "所有權限於使用者帳號內的部署與資料 並仍受上游授權約束",
        },
    },
    "deploy-agent": {
        "en": {
            "why": "Deployment instructions become safer when guidance and judgment are deliberately assigned to different actors.",
            "how": "The Agent follows the contract asks only necessary questions records actions and submits results to independent gates.",
            "example": "An Agent may run deployment and smoke tests but cannot mark its own run SmallGreen Ready.",
            "evidence": "Agent compatibility applies only to the recorded model contract version environment and verification date.",
        },
        "zh-tw": {
            "why": "部署引導與成功判定由不同角色負責 才能降低自我宣告成功的風險",
            "how": "Agent 遵循契約 只詢問必要資訊 記錄動作 並把結果交給獨立閘門",
            "example": "Agent 可以執行部署與 smoke test 但不能自行標示 SmallGreen Ready",
            "evidence": "Agent 相容性只適用於記錄中的模型 契約版本 環境與驗證日期",
        },
    },
    "service-card": {
        "en": {
            "why": "People need a concise comparison surface before reading contracts or granting deployment authority.",
            "how": "Render purpose ownership resource budget data flow verification recency and limitations from Registry facts.",
            "example": "A person compares two analytics tools by grade external services maintenance state and dated evidence.",
            "evidence": "A Service Card summarizes evidence. The linked contract and Evidence Pack remain the auditable sources.",
        },
        "zh-tw": {
            "why": "人在閱讀契約或授權部署前 需要清楚而可比較的決策介面",
            "how": "從 Registry 事實呈現用途 所有權 資源預算 資料流 驗證日期與限制",
            "example": "使用者依等級 外部服務 維護狀態與具日期證據比較兩項分析工具",
            "evidence": "服務卡是證據摘要 可稽核來源仍是部署契約與 Evidence Pack",
        },
    },
    "deployment-contract": {
        "en": {
            "why": "Narrative setup guides are ambiguous and cannot reliably support autonomous deployment or mechanical review.",
            "how": "Profile acceptance and maintenance contracts define inputs resources checks failure stops and teardown conditions.",
            "example": "The contract states required bindings a health path expected status and zero-diff uninstall conditions.",
            "evidence": "Passing a contract proves only the declared checks under that Spec version and does not establish universal safety.",
        },
        "zh-tw": {
            "why": "敘事式安裝指南容易產生歧義 無法穩定支援自主部署與機械覆核",
            "how": "Profile acceptance maintenance 契約定義輸入 資源 檢查 停止與移除條件",
            "example": "契約明示必要 binding health path 預期狀態與零差異移除條件",
            "evidence": "通過契約只證明該 Spec 版本下的已宣告檢查 不代表普遍安全",
        },
    },
    "resource-budget": {
        "en": {
            "why": "Free tier is an operating constraint with quotas retention limits and failure modes rather than a permanent price promise.",
            "how": "Declare every required resource derive a grade from measurable limits and publish fallback behavior before deployment.",
            "example": "A service that requires Workers AI receives a constrained grade and explains what stops when quota is exhausted.",
            "evidence": "Grades reflect verified configuration at a date. Cloudflare limits and upstream behavior may later change.",
        },
        "zh-tw": {
            "why": "免費額度是包含配額 保存期限與失敗模式的運營限制 不是永久價格承諾",
            "how": "宣告所有必要資源 依可量測限制推導等級 並在部署前公開降級行為",
            "example": "需要 Workers AI 的服務標示受限等級 並說明額度耗盡後停止的功能",
            "evidence": "等級只反映特定日期的已驗證設定 Cloudflare 限制與上游行為仍可能改變",
        },
    },
}

FAQ = {
    "en": [
        ("Is listing the same as endorsement?", "No. Verification levels describe evidence reached under a specific Spec version; they are not a safety guarantee."),
        ("Does SmallGreen host my service?", "No. The service runs in your own account. SmallGreen publishes contracts, adapters and evidence."),
        ("Does the website track deployments?", "No. The public site has no deployment telemetry, login or user-level analytics."),
        ("Can an Agent deploy directly from the registry?", "An Agent can read the Service Card and follow the adapter AGENTS.md. Mechanical gates still decide pass or fail."),
    ],
    "zh-tw": [
        ("收錄等於背書嗎？", "不是。驗證等級只描述特定 Spec 版本下已取得的證據，不是安全保證。"),
        ("SmallGreen 會代管我的服務嗎？", "不會。服務運行在你自己的帳號；SmallGreen 公開契約、Adapter 與驗證證據。"),
        ("網站會追蹤部署嗎？", "不會。公開網站沒有部署遙測、登入或使用者層級分析。"),
        ("Agent 可以直接從 Registry 部署嗎？", "Agent 可以讀取服務卡並遵循 Adapter 的 AGENTS.md；通過或失敗仍由機械閘門判定。"),
    ],
}
