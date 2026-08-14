// MD2HTML API examples: /convert and /slug endpoints (stdlib only)
package main
import ("bytes"; "encoding/json"; "fmt"; "io"; "net/http")
const baseURL = "https://147.15.103.217.sslip.io/md2html"
const apiKey = "YOUR_LTC_API_KEY" // LTC address used as API key

// post sends JSON {field: val, api_key} and returns the raw JSON string.
func post(ep, field, val string) (string, error) {
	body, _ := json.Marshal(map[string]string{field: val, "api_key": apiKey})
	resp, err := http.Post(baseURL+ep, "application/json", bytes.NewReader(body))
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	data, _ := io.ReadAll(resp.Body)
	return string(data), nil
}

func main() {
	conv, _ := post("/convert", "markdown", "# Hello\n\n**Bold** text.")
	fmt.Println("HTML:", conv) // /convert — Markdown to HTML
	slug, _ := post("/slug", "text", "Hello World! Test.")
	fmt.Println("Slug:", slug) // /slug — text to URL-safe slug
}
