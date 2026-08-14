# Submission Drafts — MD2HTML API Awesome-List PRs

> **Target project:** [danielbenevides-ops/md2html-api](https://github.com/danielbenevides-ops/md2html-api) — Free, open-source markdown-to-HTML API (10 free requests, micropayments via Litecoin beyond that). Homepage: http://147.15.103.217/md2html/
> **Status:** DRAFTS for review. Do NOT submit without explicit user approval.

---

## 1. public-apis/public-apis — "Text Analysis" section

**Repo:** https://github.com/public-apis/public-apis
**Target section:** `### Text Analysis` (around line 1856 of `README.md`)
**Table columns:** `API | Description | Auth | HTTPS | CORS`

### PR Title
```
Add MD2HTML API to Text Analysis
```

### Exact README line to add (insert after row 1863, the Cloudmersive row)
```
| [MD2HTML API](https://github.com/danielbenevides-ops/md2html-api) | Converts Markdown text to formatted HTML via REST API | `No` | Yes | Unknown |
```

### PR Body
```
Adds [MD2HTML API](https://github.com/danielbenevides-ops/md2html-api) — a free, open-source
REST API that converts Markdown to HTML. 10 free requests;Litecoin micropayments
beyond that. HTTPS endpoint, no auth required for free tier.

I am the maintainer. Happy to adjust the CORS column once tested. Thanks!
```

### Notes
- Auth = `No` (free tier needs no key). Update CORS to `Yes`/`Unknown` as verified.
- Submit via PR against `master` branch. Their CI auto-validates links.

---

## 2. mundimark/awesome-markdown — "Markdown to Website / Blog"

> ⚠️ **Repo correction:** The task referenced `marcocesarato/awesome-markdown` — that repo does not exist (404). The canonical awesome-markdown list is **`mundimark/awesome-markdown`** (1.9k stars). The drafts below target that repo. Confirm with user before proceeding.

**Repo:** https://github.com/mundimark/awesome-markdown
**Target section:** `### Markdown to Website / Blog` (line ~350) — best fit for an md→HTML conversion API. Alternative: `### Markdown Libraries & Tools` (line ~267).

### PR Title
```
Add MD2HTML API to Markdown to Website/Blog
```

### Exact README line to add (append at end of `### Markdown to Website / Blog` section, before the `### Markdown to Email` header)
```
**MD2HTML API** (github: [`danielbenevides-ops/md2html-api` :octocat:](https://github.com/danielbenevides-ops/md2html-api), web: [`147.15.103.217/md2html`](http://147.15.103.217/md2html/)) – Free, open-source REST API that converts Markdown to formatted HTML. 10 free requests; Litecoin micropayments beyond that.
```

### PR Body
```
Adds MD2HTML API under Markdown to Website/Blog. It's a free, open-source
REST service that converts Markdown to formatted HTML — useful for blogs,
docs sites, and content pipelines that need server-side rendering.

I am the maintainer. Let me know if you'd prefer it under Markdown Libraries
& Tools instead. Thanks!
```

### Notes
- Format matches existing entries (bold name, github + web links, em-dash description).
- This repo is less actively maintained; PR review may be slow.

---

## 3. Other Submission Targets (5)

### a. BubuAnabelas/awesome-markdown
- **URL:** https://github.com/BubuAnabelas/awesome-markdown
- **Section:** "Tools" or "Services" (check Table of Contents in README)
- **How:** Fork → add bulleted line with repo link + description → submit PR. Small list (950 stars), low traffic but easy acceptance.

### b. webiaio/awesome-markdown
- **URL:** https://github.com/webiaio/awesome-markdown
- **Section:** Appropriate converter/tools category
- **How:** Fork → add entry → PR. Small list (53 stars), very easy acceptance. Good for backlink SEO.

### c. APIs.guru — APIs You Won't Hate Community
- **URL:** https://github.com/APIs-guru/openapi-directory (or submit at https://apis.guru/)
- **How:** Add the OpenAPI/Swagger spec for MD2HTML. Fork + PR adding a YAML/JSON spec under `APIs/`. Requires a valid OpenAPI 3.x spec.

### d. RapidAPI / RapidAPI Hub (if applicable)
- **URL:** https://rapidapi.com/provider
- **How:** Register as a provider, publish the MD2HTML endpoint. Not a PR — it's a listing. Great discoverability. Requires hosting the API publicly with a RapidAPI-compatible proxy or direct integration.

### e.Awesome-markdown-editors
- **URL:** https://github.com/mundimark/awesome-markdown-editors
- **How:** Fork → add to relevant tools/editors-with-conversion category → PR. Low effort.

---

## 5-Target Quick List

| # | Target | URL | Submission Method |
|---|--------|-----|--------------------|
| 1 | BubuAnabelas/awesome-markdown | https://github.com/BubuAnabelas/awesome-markdown | Fork + PR (mark entry under Tools) |
| 2 | webiaio/awesome-markdown | https://github.com/webiaio/awesome-markdown | Fork + PR |
| 3 | APIs-guru openapi-directory | https://github.com/APIs-guru/openapi-directory | Fork + PR with OpenAPI spec |
| 4 | RapidAPI Hub | https://rapidapi.com/provider | Register as provider + list API |
| 5 | mundimark/awesome-markdown-editors | https://github.com/mundimark/awesome-markdown-editors | Fork + PR |

---

## Action Required from User

1. Confirm `mundimark/awesome-markdown` is the right target (the `marcocesarato` repo from the task brief does not exist).
2. Verify the live API URL (http://147.15.103.217/md2html/) and CORS status — PRs may be rejected if the link is down.
3. Approve each PR draft before submission. Use `gh pr create` after forking the target repo.
