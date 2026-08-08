import server

# /sanitize flow
raw = '# Hi <script>alert(1)</script> **bold**'
clean = server.sanitize_markdown(raw)
print('Sanitized markdown:', repr(clean))
html = server.md_to_html(clean, already_escaped=True)
print('Sanitized HTML   :', repr(html))

# Verify: output HTML must NOT contain a live <script> tag.
# We check for the raw bytes '<script' (lt then s-c-r-i-p-t).
assert '<script' not in html, \
    'FAIL: live <script> tag in output (XSS)'
print('PASS: no live <script> tag in /sanitize output')

# Verify: output must show the tag as escaped text (e.g. <script>)
assert 'lt;script' in html, \
    'FAIL: escaped script form not found'
print('PASS: script tag is escaped in /sanitize output')

# Plain /convert flow (already_escaped=False default)
html2 = server.md_to_html(raw)
print('Plain /convert HTML:', repr(html2))
assert '<script' not in html2, 'FAIL: plain convert leaked live script tag'
print('PASS: no live <script> tag in /convert output')

# Batch flow
items = ['# Title', '**bold**', '<b>not md</b>']
results = [server.md_to_html(i) for i in items]
print('Batch results:')
for r in results:
    print('  ', repr(r))
assert '<b>' not in results[2], 'FAIL: batch leaked live <b> tag'
print('PASS: batch escapes raw HTML in items')

print()
print('All unit checks passed.')
