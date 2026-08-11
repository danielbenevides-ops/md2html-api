# MD2HTML Python SDK

Tiny, dependency-free client for the MD2HTML API.

## Install

```bash
pip install .
```

## Use

```python
from md2html_client import Md2HTMLClient

client = Md2HTMLClient()
client.register("you@example.com")

html = client.convert("# Hello **world**")
html_pages = client.batch(["# One", "# Two"])
pretty = client.prettify_json('{"b":2,"a":1}')
stats = client.text_stats("The quick brown fox")
usage = client.get_usage()
```

`register()` stores the returned API key for later requests. Pass
`base_url=` to use a self-hosted server. `convert()` returns HTML; `batch()`
returns a list of HTML strings. The client uses only Python’s standard library.

License: MIT.
