<?php
// MD2HTML API examples: /convert and /slug endpoints
const BASE_URL = 'http://147.15.103.217/md2html';
const API_KEY = 'YOUR_LTC_API_KEY'; // LTC address used as API key

// Helper: POST JSON and return decoded response array
function api_post(string $endpoint, array $payload): array {
    $ch = curl_init(BASE_URL . $endpoint);
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_POSTFIELDS => json_encode($payload),
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 30,
    ]);
    $resp = curl_exec($ch);
    curl_close($ch);
    return json_decode($resp, true);
}

// /convert — Markdown to HTML
$conv = api_post('/convert', ['markdown' => "# Hello\n\n**Bold** text.", 'api_key' => API_KEY]);
echo "HTML: " . $conv['html'] . "\n";
// /slug — text to URL-safe slug
$slug = api_post('/slug', ['text' => 'Hello World! Test.', 'api_key' => API_KEY]);
echo "Slug: " . $slug['slug'] . "\n";
