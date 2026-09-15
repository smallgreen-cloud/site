"""Bilingual editorial copy for the static site.

Facts about services remain owned by registry YAML. This module only owns site
navigation, canonical concept copy, and English translations of service
one-liners. A missing translation is a build error rather than a silent fallback.
"""

LANGS = ("en", "zh-tw")

BRAND = "SmallGreen"

POSITIONING = {
    "en": {
        "definition": "SmallGreen is a service directory and standard for turning open-source small projects into services you can deploy, control and run yourself.",
        "audience": "People who want to turn an open-source small project into a service they can run themselves.",
        "problem": "A repository can be useful without being understandable, deployable or maintainable as a service.",
        "promise": "See what a project does, who it is for, what it needs, what has been checked and how to leave before you run it.",
    },
    "zh-tw": {
        "definition": "SmallGreen 是一套把開源小型專案整理成可自己部署、自己掌握、自己運行的服務目錄與標準。",
        "audience": "想把開源小型專案變成自己能運行的服務的人",
        "problem": "一個 Repo 可以被下載，不代表它已經容易看懂、部署、維護與退出。",
        "promise": "在開始運行前，先看懂專案要解決什麼、適合誰、需要什麼、檢查過什麼，以及如何離開。",
    },
}

NAV = {
    "en": {
        "manifesto": "About", "concepts": "Concepts", "services": "Services",
        "standard": "Standard", "evidence": "Evidence", "faq": "FAQ",
        "language": "繁體中文",
    },
    "zh-tw": {
        "manifesto": "關於 SmallGreen", "concepts": "核心概念", "services": "服務目錄",
        "standard": "標準", "evidence": "驗證證據", "faq": "常見問題",
        "language": "English",
    },
}

HOME = {
    "en": {
        "eyebrow": "01 / SMALLGREEN / SERVICE DIRECTORY + STANDARD",
        "title": "Find a small project you can run yourself",
        "title_lines": ["Find a small project", "you can run yourself"],
        "definition_label": "WHAT SMALLGREEN IS",
        "definition": POSITIONING["en"]["definition"],
        "lede": POSITIONING["en"]["promise"],
        "meta_description": POSITIONING["en"]["definition"],
        "primary": "Find a project",
        "secondary": "See the six questions",
        "secondary_path": "concepts",
        "how_label": "02 / BEFORE YOU RUN IT",
        "how_title_lines": ["Decide from the project", "not the stack"],
        "how_text": "A useful decision starts with three plain questions.",
        "trust_items": [
            ("What does it solve", "Start with the project purpose, audience and boundaries."),
            ("What does it need", "See data flow, resources, external services and limits."),
            ("Can you keep control", "Check evidence, maintenance and the path to remove it."),
        ],
        "services_label": "03 / OPEN-SOURCE PROJECTS",
        "services_title_lines": ["Choose by the problem", "then inspect the deployment"],
        "services_text": "Each entry starts with what the project does and who it is for. Open the Service Card for architecture, requirements, limits and evidence.",
    },
    "zh-tw": {
        "eyebrow": "01 / SMALLGREEN / 服務目錄與標準",
        "title": "找一個自己能運行的開源小型專案",
        "title_lines": ["從開源小型專案", "找到自己能運行的服務"],
        "definition_label": "SMALLGREEN 是什麼",
        "definition": POSITIONING["zh-tw"]["definition"],
        "lede": POSITIONING["zh-tw"]["promise"],
        "meta_description": POSITIONING["zh-tw"]["definition"],
        "primary": "找一個專案",
        "secondary": "看六個判斷問題",
        "secondary_path": "concepts",
        "how_label": "02 / 開始運行之前",
        "how_title_lines": ["先看專案本身", "再看部署方式"],
        "how_text": "一個有用的判斷　先回答三個問題。",
        "trust_items": [
            ("它要解決什麼", "先看專案用途、適合對象與使用邊界。"),
            ("它需要什麼", "看清楚資料流、資源、外部服務與限制。"),
            ("能不能自己掌握", "確認證據、維護方式與移除服務的路徑。"),
        ],
        "services_label": "03 / 開源小型專案",
        "services_title_lines": ["先按要解決的問題找", "再確認部署方式"],
        "services_text": "每個條目先說明專案要做什麼與適合誰　開啟服務卡查看架構、部署前提、限制與證據。",
    },
}

STATIC_PAGES = {
    "manifesto": {
        "en": {
            "label": "ABOUT SMALLGREEN",
        },
        "zh-tw": {
            "label": "關於 SmallGreen",
        },
    },
    "standard": {
        "en": {
            "label": "STANDARD", "title": "How a project becomes deployable and ownable",
            "title_lines": ["How a project becomes", "deployable and ownable"],
            "lede": "The SmallGreen standard turns project facts into checks for deployment, acceptance, maintenance and exit.",
            "sections": [
                ("Project profile", "Small App and Pipeline profiles describe the service shape, resources and execution pattern."),
                ("Deployment contract", "Profile, acceptance and maintenance contracts turn repository facts into machine-readable instructions."),
                ("Independent checks", "Validators and Evidence Packs decide pass or fail. An Agent can guide the process but is never the judge."),
            ],
        },
        "zh-tw": {
            "label": "標準", "title": "專案如何變成自己能運行的服務",
            "title_lines": ["專案如何變成", "自己能運行的服務"],
            "lede": "SmallGreen 標準把專案事實轉成部署、驗收、維護與退出時可以檢查的條件。",
            "sections": [
                ("專案 Profile", "Small App 與 Pipeline Profile 說明服務形狀、資源與執行方式。"),
                ("部署契約", "Profile、acceptance、maintenance 三份契約把 Repo 事實轉成機器可讀的指令。"),
                ("獨立檢查", "Validator 與 Evidence Pack 決定通過或失敗。Agent 可以引導流程，但永遠不是裁判。"),
            ],
        },
    },
    "evidence": {
        "en": {
            "label": "EVIDENCE", "title": "Verification is a public trail not a badge",
            "title_lines": ["Verification is a public trail", "Not a badge"],
            "lede": "Evidence shows what was checked, for which version and when. It is a public trail, not a badge.",
            "sections": [
                ("What is public", "Versioned Service Cards, sanitized Evidence Packs, verification dates, known limits and machine-derived architecture diagrams."),
                ("What stays private", "Secrets, account identifiers, private URLs, user data, operational logs and uncoordinated vulnerability details."),
                ("Append-only history", "New runs supersede older evidence without rewriting history, so stale claims remain visible and reviewable."),
            ],
        },
        "zh-tw": {
            "label": "驗證證據", "title": "驗證是一條公開軌跡 不是一枚徽章",
            "title_lines": ["驗證是一條公開軌跡", "不是一枚徽章"],
            "lede": "證據讓人知道檢查了什麼、適用哪個版本與何時檢查。它是一條公開軌跡，不是一枚徽章。",
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
                ("資料面分工", "Cloudflare Web Analytics 量測造訪與效能；Edge Analytics 與 AI Crawl Control 量測 crawler；搜尋曝光、點擊與索引則由 Search Console 與 Bing Webmaster 提供。"),
            ],
        },
    },
}

MANIFESTO = {
    "en": {
        "label": "ABOUT SMALLGREEN",
        "title": "A repository is not yet a service you own",
        "title_lines": ["A repository is not yet", "a service you own"],
        "lede": "Our operating policy is to document deployment, data, maintenance and exit so they can be checked.",
        "mission": ("Mission", "Help people turn an open-source small project into a service they can understand, run, maintain and remove in their own account."),
        "vision": ("Vision", "A healthy software ecosystem is not only one where code is reusable. It is one where people can run useful services without surrendering their data or their ability to leave."),
        "principles_label": "Principles",
        "principles": [
            ("Own the running service", "Code ownership is not enough. The account, data, configuration and exit path must belong to the person running the service."),
            ("Put claims on evidence", "A claim is useful when its version, environment, checks and limitations are visible to someone else."),
            ("Let automation guide without judging", "An Agent may guide and execute a deployment. An independent check decides whether the claim can be made."),
        ],
        "practice_label": "How we act",
        "practice": [
            ("Our publication rule", "We publish purpose, deployment prerequisites, verification state and known limits where they can be checked."),
            ("We do not claim", "That a project is deployable, secure or sustainable without a traceable check and evidence."),
            ("We preserve choice", "The user can change provider, maintain the service or remove the deployment."),
        ],
    },
    "zh-tw": {
        "label": "關於 SmallGreen",
        "title": "有了 Repo 還不等於擁有一個服務",
        "title_lines": ["有了 Repo 還不等於", "擁有一個服務"],
        "lede": "我們的工作原則，是把部署、資料、維護與退場寫清楚，並讓它們可以被檢查。",
        "mission": ("使命", "協助人們把開源小型專案，變成自己看得懂、能運行、能維護、也能移除的服務。"),
        "vision": ("願景", "健康的軟體生態不只是程式碼可以重用　也要讓人能運行真正有用的服務　不用交出資料與離開的能力。"),
        "principles_label": "我們相信的原則",
        "principles": [
            ("擁有正在運行的服務", "擁有程式碼還不夠　帳號、資料、設定與退場路徑也要由運行它的人掌握。"),
            ("讓主張連回證據", "一項主張必須讓別人看見它的版本、環境、檢查方式與限制　才真正有用。"),
            ("讓自動化引導，不讓它裁判", "Agent 可以引導與執行部署　是否能宣稱通過則由獨立檢查決定。"),
        ],
        "practice_label": "我們如何行動",
        "practice": [
            ("公開規則", "公開用途、部署前提、驗證狀態與已知限制　並讓它們可以被查核。"),
            ("我們不宣稱", "沒有可追溯檢查與證據　就說 Repo 一定可部署、安全或永續。"),
            ("我們保留選擇", "使用者可以更換供應商、維護服務或移除部署。"),
        ],
    },
}

CONCEPT_GUIDE = {
    "en": {
        "label": "CONCEPTS",
        "title_lines": ["Before you run a project", "answer six useful questions"],
        "lede": "Use these questions to decide whether an open-source project is understandable, deployable and something you can keep control of.",
        "pass_label": "Pass condition",
        "evidence_label": "Check",
        "stages": [
            ("01 / UNDERSTAND THE PROJECT", "Start with a bounded purpose", "Know what the project is for before you choose how to run it.", [
                ("small-software", "Is the purpose and scope bounded", "The project has one stated job, a clear boundary and an owner for operation.", "Service Card: project type, problem and limits."),
                ("service-card", "Can a person understand what it does", "Purpose, audience, data flow and known limits are visible before deployment.", "Service Card: summary, data flow and limitations."),
            ]),
            ("02 / CHECK THE DEPLOYMENT", "Turn assumptions into checks", "Know what the service needs before you give it an account or your data.", [
                ("resource-budget", "Are resources and failure behavior visible", "Quota, runtime resources, free-tier limits and fallback behavior are stated.", "Service Card: resource budget and limits."),
                ("deployment-contract", "Can deployment acceptance and removal be checked", "Prerequisites and checks are machine-readable and include teardown.", "Deployment Contract and Evidence Pack."),
                ("deploy-agent", "Does the Agent guide without judging", "The Agent executes declared steps; an independent check decides pass or fail.", "Deploy Agent log and independent validator result."),
            ]),
            ("03 / KEEP CONTROL", "Keep control after deployment", "A service is yours to run only when you can maintain, move or remove it.", [
                ("ownership-and-deployment-layer", "Can you maintain move or remove the service and its data", "Account, configuration, data export and resource-zero steps are documented and testable.", "Maintenance and teardown evidence."),
            ]),
        ],
    },
    "zh-tw": {
        "label": "核心概念",
        "title_lines": ["開始運行之前", "先回答六個實用問題"],
        "lede": "用這六個問題判斷一個開源專案是否看得懂、部署得了，以及部署後能不能繼續由自己掌握。",
        "pass_label": "通過條件",
        "evidence_label": "查看證據",
        "stages": [
            ("01 / 先看懂專案", "先把用途劃清楚", "先知道專案要做什麼　再決定要怎麼運行。", [
                ("small-software", "用途與範圍有界嗎", "專案只有一項清楚的工作　邊界明確　也有人負責運行。", "服務卡的專案類型、問題與限制。"),
                ("service-card", "人看得懂它要做什麼嗎", "部署前就能看見用途、適合對象、資料流與已知限制。", "服務卡的摘要、資料流與限制。"),
            ]),
            ("02 / 確認部署方式", "把假設轉成檢查", "在交出帳號或資料前　先知道服務需要什麼。", [
                ("resource-budget", "資源與失敗行為說清楚了嗎", "配額、運行資源、免費額度限制與降級行為都有說明。", "服務卡的資源預算與限制。"),
                ("deployment-contract", "部署、驗收與移除檢查得了嗎", "前提與檢查條件是機器可讀　也包含 teardown。", "部署契約與 Evidence Pack。"),
                ("deploy-agent", "Agent 只引導而不裁判嗎", "Agent 執行已宣告的步驟　是否通過則由獨立檢查決定。", "Deploy Agent log 與獨立 Validator 結果。"),
            ]),
            ("03 / 保留掌握權", "部署後仍然能掌握", "只有能維護、搬遷或移除的服務　才是真正由自己運行。", [
                ("ownership-and-deployment-layer", "能維護、搬遷或移除服務與資料嗎", "帳號、設定、資料匯出與資源歸零步驟都有文件並可測試。", "維護與 teardown 證據。"),
            ]),
        ],
    },
}

CONCEPTS = {
    "small-software": {
        "en": ("What is Small Software", "Focused software with a bounded purpose, small operational footprint and an explicit path to ownership and exit."),
        "zh-tw": ("什麼是 Small Software", "用途聚焦、運行足跡小，並具有明確所有權與退場路徑的軟體。"),
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
        "zh-tw": ("免費額度是一項資源預算", "把免費額度視為可量測的運行限制，明示上限與降級行為。"),
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
            "evidence": "這個名稱只描述範圍與可運行性 不代表安全 穩定或社群採用",
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
            "evidence": "所有權僅限於使用者帳號內的部署與資料 並仍受上游授權約束",
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
            "why": "免費額度是包含配額 保存期限與失敗模式的運行限制 不是永久價格承諾",
            "how": "宣告所有必要資源 依可量測限制推導等級 並在部署前公開降級行為",
            "example": "需要 Workers AI 的服務標示受限等級 並說明額度耗盡後停止的功能",
            "evidence": "等級只反映特定日期的已驗證設定 Cloudflare 限制與上游行為仍可能改變",
        },
    },
}

FAQ = {
    "en": [
        ("What does SmallGreen provide?", "A clear way to understand an open-source small project before you deploy it: purpose, audience, requirements, architecture, evidence, limits and exit."),
        ("Do I need to be a developer?", "Not necessarily. You need enough access to deploy and maintain a service in your own account; the Service Card helps you decide what to ask before you start."),
        ("Is listing the same as endorsement?", "No. Verification levels describe evidence reached under a specific Spec version; they are not a safety guarantee."),
        ("Does SmallGreen host my service?", "No. The service runs in your own account. SmallGreen publishes contracts, adapters and evidence."),
        ("Does the website track deployments?", "No. The public site has no deployment telemetry, login or user-level analytics."),
        ("Can an Agent deploy directly from the registry?", "An Agent can read the Service Card and follow the adapter AGENTS.md. Mechanical gates still decide pass or fail."),
    ],
    "zh-tw": [
        ("SmallGreen 提供什麼？", [
            "在部署開源小型專案前",
            "先看懂用途、適合誰、部署前提、架構、證據、限制與退場方式",
        ]),
        ("我需要是開發者嗎？", [
            "不一定",
            "你需要能在自己的帳號部署與維護服務",
            "服務卡會幫你判斷開始前應該確認什麼",
        ]),
        ("收錄等於背書嗎？", [
            "不是",
            "驗證等級只描述特定 Spec 版本下已取得的證據",
            "不是安全保證",
        ]),
        ("SmallGreen 會代管我的服務嗎？", [
            "不會代管",
            "服務會運行在你自己的帳號",
            "SmallGreen 會公開部署契約、Adapter 與驗證證據",
        ]),
        ("網站會追蹤部署嗎？", [
            "不會",
            "公開網站沒有部署遙測、登入或使用者層級分析",
        ]),
        ("Agent 可以直接從 Registry 部署嗎？", [
            "Agent 可以讀取服務卡並遵循 Adapter 的 AGENTS.md",
            "通過或失敗仍由機械閘門判定",
        ]),
    ],
}
