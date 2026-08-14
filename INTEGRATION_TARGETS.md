# MD2HTML API Integration Targets

Research of 15 open-source projects that could integrate the **MD2HTML API** (https://147.15.103.217.sslip.io/md2html/, 10 endpoints) as an external markdown-rendering service.

Star counts fetched via the GitHub REST API on **2026-08-09**. Potential contacts are the top contributors by commit count (bots excluded); GitHub usernames link to profiles where real names were unavailable.

---

## Summary Table

| # | Project | Category | Stars | Best Contact (GitHub) |
|---|---------|----------|------:|-----------------------|
| 1 | [Hugo](#1-hugo) | Static Site Generator | 89,386 | [@bep](https://github.com/bep) — Bjørn Erik Pedersen |
| 2 | [Astro](#2-astro) | Static Site Generator | 61,659 | [@ematipico](https://github.com/ematipico) — Emanuele Stoppa |
| 3 | [Jekyll](#3-jekyll) | Static Site Generator | 51,624 | [@parkr](https://github.com/parkr) |
| 4 | [Eleventy / Build Awesome](#4-eleventy--build-awesome) | Static Site Generator | 19,839 | [@zachleat](https://github.com/zachleat) |
| 5 | [VitePress](#5-vitepress) | Static Site Generator / Docs | 18,154 | [@brc-dd](https://github.com/brc-dd) — Divyansh Singh |
| 6 | [Docusaurus](#6-docusaurus) | Docs Generator | 65,867 | [@slorber](https://github.com/slorber) |
| 7 | [MkDocs](#7-mkdocs) | Docs Generator | 22,319 | [@d0ugal](https://github.com/d0ugal) — Dougal Matthews |
| 8 | [MkDocs Material](#8-mkdocs-material) | Docs Generator / Theme | 27,232 | [@squidfunk](https://github.com/squidfunk) |
| 9 | [mdBook](#9-mdbook) | Docs Generator | 22,060 | [@ehuss](https://github.com/ehuss) — Eric Huss |
| 10 | [Strapi](#10-strapi) | Headless CMS | 72,827 | [@alexandrebodin](https://github.com/alexandrebodin) |
| 11 | [TinaCMS](#11-tinacms) | Git-backed CMS | 13,717 | [@ncphillips](https://github.com/ncphillips) |
| 12 | [Decap CMS](#12-decap-cms) | Git-backed CMS | 19,286 | [@erquhart](https://github.com/erquhart) — Shawn Erquhart |
| 13 | [Logseq](#13-logseq) | Note-taking App | 44,362 | [@tiensonqin](https://github.com/tiensonqin) |
| 14 | [SiYuan](#14-siyuan) | Note-taking App | 45,688 | [@Vanessa219](https://github.com/Vanessa219) |
| 15 | [AFFiNE](#15-affine) | Note-taking App | 71,358 | [@darkskygit](https://github.com/darkskygit) |

---

## 1. Hugo

- **Category:** Static Site Generator
- **GitHub:** https://github.com/gohugoio/hugo
- **Stars:** 89,386
- **Language:** Go — **License:** Apache 2.0
- **Homepage:** https://gohugo.io

### How they'd use MD2HTML
Hugo has its own fast markdown renderer (Goldmark), but it cannot natively render *advanced* markdown extensions (math, diagrams, GFM-native admonitions, etc.) without heavy shortcodes or external JS. MD2HTML could be offered as an **optional rendering backend / plugin**: users who want server-side-rendered GFM extras, unified output HTML, or a shared rendering contract with a CMS preview pane could route `.md` → MD2HTML → HTML during build or for live preview. It's also a candidate for a **"remote markdown" content adapter** that pulls and renders markdown from external sources at build time.

### Potential contact (maintainer)
- **Bjørn Erik Pedersen** (@bep) — 5,807 commits, creator/maintainer.
  GitHub: https://github.com/bep · Blog: https://bep.is
- Steve Francia (@spf13) — original author, 466 commits.
  GitHub: https://github.com/spf13

---

## 2. Astro

- **Category:** Static Site Generator
- **GitHub:** https://github.com/withastro/astro
- **Stars:** 61,659
- **Language:** TypeScript — **License:** Other (MIT-style)
- **Homepage:** https://astro.build

### How they'd use MD2HTML
Astro is "the web framework for content-driven websites" with first-class Markdown + MDX support. MD2HTML could integrate as a **renderer option in `astro.config.mjs`** (analogous to remark/rehype plugins) for users who want GFM-accurate server-side rendering without a JS pipeline, or as a **"remote content" island** that renders markdown sourced from external repos/APIs at request time. The content-collections layer is a natural injection point: a `markdownRenderer: 'md2html'` option could replace the built-in shiki/remark stack for specific content types.

### Potential contact (maintainer)
- **Emanuele Stoppa** (@ematipico) — 1,171 commits, core member.
  GitHub: https://github.com/ematipico · Company: Cloudflare
- Matthew Phillips (@matthewp) — 2,058 commits, creator.
  GitHub: https://github.com/matthewp

---

## 3. Jekyll

- **Category:** Static Site Generator
- **GitHub:** https://github.com/jekyll/jekyll
- **Stars:** 51,624
- **Language:** Ruby — **License:** MIT
- **Homepage:** https://jekyllrb.com

### How they'd use MD2HTML
Jekyll's converter pipeline (`Jekyll::Converter`) is pluggable — `kramdown` is the default markdown converter. MD2HTML could be added as an **alternative converter gem** (`jekyll-md2html`) that POSTs markdown to the API and returns HTML for pages/posts. This benefits users who want GFM-exact output (Jekyll/kramdown diverge on tables, autolinks, strikethrough) or need a server-side render that matches a frontend preview. Also useful for GitHub Pages-style workflows that need a single canonical HTML contract.

### Potential contact (maintainer)
- **(@parkr)** — 3,747 commits, lead maintainer.
  GitHub: https://github.com/parkr
- **Ashwin Maroli** (@ashmaroli) — 656 commits, core contributor.
  GitHub: https://github.com/ashmaroli

---

## 4. Eleventy / Build Awesome

- **Category:** Static Site Generator
- **GitHub:** https://github.com/11ty/buildawesome (repo "buildawesome", formerly `eleventy`)
- **Stars:** 19,839
- **Language:** JavaScript — **License:** MIT
- **Homepage:** https://build.awesome.me/

### How they'd use MD2HTML
Eleventy is template-engine agnostic and already lets users swap markdown libraries via `setLibrary("md", ...)`. MD2HTML could ship as an **officially listed template library plugin** (`@11ty/eleventy-md2html`) that calls the API for `.md` → HTML rendering, exposing the 10 endpoints (e.g. choose syntax-highlight vs no-highlight, GFM vs CommonMark) as Eleventy config options. Its plugin model makes this a clean, low-friction integration that can coexist with the default `markdown-it`.

### Potential contact (maintainer)
- **(@zachleat)** — 3,205 commits, creator/lead.
  GitHub: https://github.com/zachleat
- Mike (@MadeByMike) — 32 commits, contributor.
  GitHub: https://github.com/MadeByMike

---

## 5. VitePress

- **Category:** Static Site Generator / Docs Generator
- **GitHub:** https://github.com/vuejs/vitepress
- **Stars:** 18,154
- **Language:** TypeScript — **License:** MIT
- **Homepage:** https://vitepress.dev

### How they'd use MD2HTML
VitePress renders docs markdown with `markdown-it` + custom plugins. MD2HTML could be a **`markdownIt` plugin replacement** configured in `.vitepress/config.ts` so that the Vue/Vite docs toolchain gets GFM-accurate HTML without bundling the JS renderer — useful for teams who want consistent output between their docs site and other systems (Notion/markdown CMS) consuming the same MD2HTML API. Endpoint selection maps nicely to VitePress config knobs (code highlight, line numbers, etc.).

### Potential contact (maintainer)
- **Divyansh Singh** (@brc-dd) — 1,106 commits, maintainer.
  GitHub: https://github.com/brc-dd · Bio: "@vuejs core team. VitePress maintainer."
- Evan You (@yyx990803) — 508 commits, Vue creator.
  GitHub: https://github.com/yyx990803
- Kia King (@kiaking) — 231 commits.
  GitHub: https://github.com/kiaking

---

## 6. Docusaurus

- **Category:** Docs Generator
- **GitHub:** https://github.com/facebook/docusaurus
- **Stars:** 65,867
- **Language:** TypeScript — **License:** MIT
- **Homepage:** https://docusaurus.io

### How they'd use MD2HTML
Docusaurus v3 uses MDX with `remark`/`rehype`. MD2HTML could be offered as an **MDX provider plugin** for teams that prefer a hosted/rendered-HTML path over the local JS pipeline — e.g. for CMS-authored docs that need a single canonical HTML before Docusaurus rebuilds. It also fits as a **live-preview renderer** in the Docusaurus CMS/editing canvases, where shipping a heavy JS markdown stack to the browser is undesirable. The plugin API (`remarkPlugins`/`rehypePlugins`) is the natural hook.

### Potential contact (maintainer)
- **(@slorber)** — 1,211 commits, lead maintainer.
  GitHub: https://github.com/slorber
- **Alexey Pyltsyn** (@lex111) — 644 commits.
  GitHub: https://github.com/lex111
- **Endi** (@endiliey) — 628 commits, maintainer.
  GitHub: https://github.com/endiliey · Bio: "Maintainer @Docusaurus"

---

## 7. MkDocs

- **Category:** Docs Generator
- **GitHub:** https://github.com/mkdocs/mkdocs
- **Stars:** 22,319
- **Language:** Python — **License:** BSD-2-Clause
- **Homepage:** https://www.mkdocs.org

### How they'd use MD2HTML
MkDocs renders markdown via the `mdx`/Markdown processors configurable in `mkdocs.yml`. MD2HTML could ship as a **Markdown extension/plugin** (`mkdocs-md2html`) that delegates rendering to the API, letting Python-docs users get GFM-accurate HTML, diagram/math support, and consistent output across themes without depending on a specific JS/CSS pipeline. Given MkDocs' Python plugin architecture (`mkdocs.plugins`), this is a very clean fit.

### Potential contact (maintainer)
- **Dougal Matthews** (@d0ugal) — 680 commits, lead maintainer.
  GitHub: https://github.com/d0ugal · Blog: http://dougalmatthews.com
- **(@oprypin)** — 427 commits, core contributor.
  GitHub: https://github.com/oprypin
- **(@waylan)** — 287 commits (Waylan Limberg, MkDocs creator).
  GitHub: https://github.com/waylan

---

## 8. MkDocs Material

- **Category:** Docs Generator / Theme
- **GitHub:** https://github.com/squidfunk/mkdocs-material
- **Stars:** 27,232
- **Language:** Python + TypeScript — **License:** MIT
- **Homepage:** https://squidfunk.github.io/mkdocs-material/

### How they'd use MD2HTML
Material is the dominant MkDocs theme and ships its own markdown plugin set (tabbed admonitions, annotations, math, task lists). MD2HTML could integrate as an **optional rendering source for the theme's advanced markdown features** — passing MD2HTML-rendered HTML fragments into Material's plugin hooks so the heavy lifting (diagrams, math, syntax highlight, geopolitical/admonition transforms) happens server-side via the API and Material only applies styling. Ideal for the theme's "Insiders" enterprise users who want a managed render path.

### Potential contact (maintainer)
- **(@squidfunk)** — 5,276 commits, sole active maintainer.
  GitHub: https://github.com/squidfunk

---

## 9. mdBook

- **Category:** Docs Generator
- **GitHub:** https://github.com/rust-lang/mdBook
- **Stars:** 22,060
- **Language:** Rust — **License:** MPL-2.0
- **Homepage:** https://rust-lang.github.io/mdBook/

### How they'd use MD2HTML
mdBook renders CommonMark + extensions in Rust via `pulldown-cmark`. MD2HTML could be exposed as a **renderer backend / preprocessor** (`md2html` as an alternative output in `book.toml`) for users who need GFM features mdBook lacks (e.g. footnotes styling, complex tables, extended math) or want HTML identical to their frontend docs. mdBook's preprocessor protocol (JSON in/out) makes it straightforward to pipe chapter content through the MD2HTML API before the final HTML build.

### Potential contact (maintainer)
- **Eric Huss** (@ehuss) — 1,307 commits, top maintainer.
  GitHub: https://github.com/ehuss
- **Mathieu David** (@azerupi) — 427 commits, original creator.
  GitHub: https://github.com/azerupi
- **Michael Bryan** (@Michael-F-Bryan) — 213 commits.
  GitHub: https://github.com/Michael-F-Bryan

---

## 10. Strapi

- **Category:** Headless CMS
- **GitHub:** https://github.com/strapi/strapi
- **Stars:** 72,827
- **Language:** TypeScript — **License:** Other (Strapi SL + Enterprise)
- **Homepage:** https://strapi.io

### How they'd use MD2HTML
Strapi is a headless CMS where content is authored in a rich-text or markdown field. MD2HTML could be a **field plugin /WYSIWYG render backend** that live-converts the markdown field to preview HTML inside the Strapi admin, and/or a **render hook** exposed by Strapi plugins that returns rendered HTML for the API consumers (so frontend clients receive HTML rather than markdown). The plugin architecture (`strapi-plugin-*`) is the natural home; a "Markdown → HTML" service in the Content Manager is a high-demand feature in the Strapi community.

### Potential contact (maintainer)
- **Alexandre BODIN** (@alexandrebodin) — 4,425 commits, current lead.
  GitHub: https://github.com/alexandrebodin · Blog: https://alexandrebodin.com
- **(@soupette)** — 5,682 commits, former lead/architect.
  GitHub: https://github.com/soupette
- **Jim LAURIE** (@lauriejim) — 3,138 commits.
  GitHub: https://github.com/lauriejim

---

## 11. TinaCMS

- **Category:** Git-backed CMS
- **GitHub:** https://github.com/tinacms/tinacms
- **Stars:** 13,717
- **Language:** TypeScript — **License:** Other
- **Homepage:** https://tina.io

### How they'd use MD2HTML
TinaCMS is an editor + git-backed CMS that stores content as markdown/MDX in GitHub repos. MD2HTML could be the **live-preview render backend** inside the Tina visual editor — rendering the markdown field to HTML in real time without bundling `markdown-it`/MDX compiler into the browser, and as a **field-render plugin** producing preview HTML on the server side. Because Tina already serialises content as MD, integrating MD2HTML lets the same canonical HTML appear in the editor and in the production build pipeline.

### Potential contact (maintainer)
- **(@ncphillips)** — 2,402 commits.
  GitHub: https://github.com/ncphillips
- **Jeff See** (@jeffsee55) — 2,062 commits.
  GitHub: https://github.com/jeffsee55
- **(@logan-anderson)** — 1,611 commits.
  GitHub: https://github.com/logan-anderson

---

## 12. Decap CMS

- **Category:** Git-backed CMS (formerly Netlify CMS)
- **GitHub:** https://github.com/decaporg/decap-cms
- **Stars:** 19,286
- **Language:** JavaScript — **License:** MIT
- **Homepage:** https://decapcms.org (community-maintained)

### How they'd use MD2HTML
Decap is a git-based editor that writes markdown into repos and renders it in an in-browser preview. MD2HTML could replace/augment the **in-admin markdown preview renderer**, giving editors a faithful GFM render (instead of the lightweight in-Browser preview) via a single API call, and could be exposed as a custom Decap **markdown widget preview addon**. This is especially valuable because Decap's preview rendering historically lags the production site's renderer.

### Potential contact (maintainer)
- **Shawn Erquhart** (@erquhart) — 822 commits, lead.
  GitHub: https://github.com/erquhart
- **Erez Rokah** (@erezrokah) — 465 commits, former Netlify maintainer.
  GitHub: https://github.com/erezrokah · Blog: https://erezro.com

---

## 13. Logseq

- **Category:** Note-taking App (outliner, local-first)
- **GitHub:** https://github.com/logseq/logseq
- **Stars:** 44,362
- **Language:** ClojureScript — **License:** AGPL-3.0
- **Homepage:** https://logseq.com

### How they'd use MD2HTML
Logseq stores notes as markdown/org-mode files and renders them in an outliner UI. MD2HTML could be an **export renderer**: when users export a page/graph to HTML (for publishing, sharing, or static-site export), Logseq POSTs the assembled markdown to MD2HTML instead of using its internal markdown-to-HTML code, yielding consistent, share-ready HTML with full GFM support (tables, math, code highlight). Also suits a **publish-to-web** plugin that mirrors a Logseq page as a hosted HTML doc via the API.

### Potential contact (maintainer)
- **(@tiensonqin)** — 11,437 commits, creator.
  GitHub: https://github.com/tiensonqin
- **(@logseq-cldwalker)** — 2,921 commits (Cldwalker, core maintainer).
  GitHub: https://github.com/logseq-cldwalker
- **(@xyhp915)** — 2,572 commits.
  GitHub: https://github.com/xyhp915

---

## 14. SiYuan

- **Category:** Note-taking App (block-based, personal KB)
- **GitHub:** https://github.com/siyuan-note/siyuan
- **Stars:** 45,688
- **Language:** TypeScript — **License:** AGPL-3.0
- **Homepage:** https://b3log.org/siyuan/

### How they'd use MD2HTML
SiYuan is a block-based note app that imports/exports markdown and can publish notes to HTML. MD2HTML could be the **markdown export backend** for SiYuan's "Export → HTML" and "Publish to web" features — routing the assembled MD through the API to get rich, styled HTML (code highlight, math, diagrams) without SiYuan re-implementing all GFM extensions in TypeScript. SiYuan's b3blog team already runs hosted services, so an API-backed render path is a natural, low-overhead addition. Maintainer Vanessa219 runs the project full-time.

### Potential contact (maintainer)
- **(@Vanessa219)** — 12,127 commits, creator/lead. Blog: vanessa.b3log.org
  GitHub: https://github.com/Vanessa219
- **(@88250)** — 11,952 commits, co-founder. Blog: https://ld246.com/member/88250
  GitHub: https://github.com/88250
- **Jeffrey Chen** (@TCOTC) — 537 commits.
  GitHub: https://github.com/TCOTC

---

## 15. AFFiNE

- **Category:** Note-taking App (block-based + whiteboard, "Notion + Miro")
- **GitHub:** https://github.com/toeverything/AFFiNE
- **Stars:** 71,358
- **Language:** TypeScript — **License:** Other (TOEverything proprietary + AGPL components)
- **Homepage:** https://affine.pro

### How they'd use MD2HTML
AFFiNE stores content as a block document model and supports markdown import/export. MD2HTML could be the **markdown export rendering service** for AFFiNE docs (when a user "shares to web / export HTML"), and the **paste/import render backend** for converting external markdown into AFFiNE blocks — letting the API normalise GitHub-flavoured input (tables, math, diagrams, callouts) into HTML that AFFiNE's block parser ingests. The `toeverything` team operates cloud services already, making a server-side render integration idiomatic.

### Potential contact (maintainer)
- **DarkSky** (@darkskygit) — 1,260 commits. Company: @toeverything
  GitHub: https://github.com/darkskygit
- **Alex Yang** (@himself65) — 1,189 commits.
  GitHub: https://github.com/himself65
- **(@pengx17)** — 976 commits.
  GitHub: https://github.com/pengx17

---

## Methodology

- **Sources:** GitHub REST API (`/repos/{owner}/{repo}` and `/repos/.../contributors`) queried on 2026-08-09; unauthenticated requests.
- **Star counts:** live at time of fetch — these are the values exposed by `stargazers_count`.
- **Contacts:** for each repo the top 3 contributors by commit count (excluding bots) are listed as potential integration contacts. Where the GitHub user profile exposes a real name, it's included; otherwise the GitHub username (linked to the profile) is used. The single best contact per project is highlighted in the Summary Table.
- **Integration rationale:** derived from each project's official architecture (plugin/extension APIs, markdown pipeline, hooks) as documented in repos and homepages. Each rationale identifies the concrete injection point.

## Notes & Caveats

- **GitHub rate limits:** the unauthenticated API caps at 60 requests/hour/IP. A few user-profile lookups (real names for `parkr`, `spf13`, `squidfunk`, `slorber`, `oprypin`, `waylan`, `yyx990803`, `matthewp`, `zachleat`, `tiensonqin`, `soupette`, etc.) were blocked by rate-limit; those are cited by GitHub handle with direct profile link.
- **11ty rename:** the `11ty/eleventy` repo has been renamed/migrated; the canonical repo is now `11ty/buildawesome` (the popular `eleventy` name redirects there). Both names are used in the OSS community.
- **License diversity:** integrations in AGPL projects (Logseq, SiYuan) and enterprise-dual-licensed CMS (Strapi, AFFiNE, TinaCMS) may have additional compatibility/contract considerations for a hosted API plugin — confirm with maintainers.
- **HTTPS endpoint:** the MD2HTML API at https://147.15.103.217.sslip.io/md2html/ uses a valid Let's Encrypt certificate and is suitable for integrations that require TLS.
