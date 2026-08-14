// MD2HTML API examples: /convert and /slug endpoints
const BASE_URL = "https://147.15.103.217.sslip.io/md2html";
const API_KEY = "YOUR_LTC_API_KEY"; // LTC address used as API key

// Convert Markdown to HTML
// POST /convert — send markdown text, receive rendered HTML
const convertResp = await fetch(`${BASE_URL}/convert`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ markdown: "# Hello\n\n**Bold** text.", api_key: API_KEY }),
});
const convertData = await convertResp.json();
console.log("HTML:", convertData.html);

// Generate URL-safe slug from text
// POST /slug — send arbitrary text, receive a clean slug
const slugResp = await fetch(`${BASE_URL}/slug`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ text: "Hello World! This is a Test.", api_key: API_KEY }),
});
const slugData = await slugResp.json();
console.log("Slug:", slugData.slug);
