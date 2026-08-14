// MD2HTML API examples: /convert and /slug endpoints
// Cargo deps: reqwest = { version = "0.11", features = ["json"] }, serde_json = "1"
use serde_json::json;
use std::error::Error;

const BASE_URL: &str = "https://147.15.103.217.sslip.io/md2html";
const API_KEY: &str = "YOUR_LTC_API_KEY"; // LTC address used as API key

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let client = reqwest::Client::new();
    // /convert — send Markdown, receive rendered HTML
    let conv = client.post(format!("{BASE_URL}/convert"))
        .json(&json!({"markdown": "# Hello\n\n**Bold** text.", "api_key": API_KEY}))
        .send().await?.json::<serde_json::Value>().await?;
    println!("HTML: {}", conv["html"]);
    // /slug — send text, receive a URL-safe slug
    let slug = client.post(format!("{BASE_URL}/slug"))
        .json(&json!({"text": "Hello World! Test.", "api_key": API_KEY}))
        .send().await?.json::<serde_json::Value>().await?;
    println!("Slug: {}", slug["slug"]);
    Ok(())
}
