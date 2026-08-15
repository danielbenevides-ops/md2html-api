// Deterministic regression test for the landing-page escapeHtml fix.
// No network. Reads the real <script> block from index.html so the test
// exercises the actual shipped code (not a copy).
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const repo = path.resolve(__dirname, "..");
const html = fs.readFileSync(path.join(repo, "index.html"), "utf8");

// Grab the last <script>...</script> block (the demo logic).
const blocks = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
if (blocks.length === 0) throw new Error("no inline <script> found");
const code = blocks[blocks.length - 1][1];

// 1) Real syntax check: compile without executing (browser globals irrelevant).
new vm.Script(code, { filename: "index.html#inline-script" });

// 2) Extract escapeHtml and evaluate just that function in isolation.
const fnMatch = code.match(/function escapeHtml\(s\)\s*\{[\s\S]*?\n    \}/);
if (!fnMatch) throw new Error("escapeHtml not found in inline script");
const escapeHtml = new vm.Script(
  fnMatch[0] + "\n;escapeHtml"
).runInNewContext({});

function assertEq(actual, expected, label) {
  if (actual !== expected) {
    throw new Error(
      `FAIL ${label}: got ${JSON.stringify(actual)} expected ${JSON.stringify(expected)}`
    );
  }
  console.log(`ok  ${label}`);
}

assertEq(escapeHtml('a&b<c>d"e\'f'),
  "a&amp;b&lt;c&gt;d&quot;e&#39;f", "escapes all five special chars");
assertEq(escapeHtml("<script>alert(1)</script>"),
  "&lt;script&gt;alert(1)&lt;/script&gt;", "escapes tag-breaking input");
assertEq(escapeHtml("plain text"), "plain text", "passes plain text through");
assertEq(escapeHtml(123), "123", "coerces non-string input");

console.log("ALL escapeHtml regression checks passed");
