#!/usr/bin/env python3
"""Validate the public distribution surface without third-party dependencies.

Run from the repository root with::

    python verify_distribution.py

The local distribution files are checked deterministically. Live checks use
read-only HTTP GET requests and can be skipped with ``--skip-live`` when the
machine has no network access. A non-zero exit status means at least one check
failed.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree


URL_RE = re.compile(r"https?://[^\s<>\"')\]]+")
ROUTE_RE = re.compile(
    r"(?<![A-Za-z0-9_./-])/(?:[A-Za-z0-9._~{}:-]+)"
    r"(?:/[A-Za-z0-9._~{}:-]+)*"
)
OPENAPI_VERSION_RE = re.compile(r"^['\"]?3\.\d+\.\d+['\"]?(?:\s+#.*)?$")
YAML_KEY_RE = re.compile(r"^(?P<indent>\s*)(?P<key>[A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(?P<value>.*)$")
YAML_PATH_RE = re.compile(r"^\s{2,}(['\"]?)(/[^'\"]+)\1\s*:\s*(?:#.*)?$")

DEFAULT_TIMEOUT = 5.0
DEFAULT_USER_AGENT = "distribution-validator/1.0"


class Reporter:
    """Small, dependency-free result reporter used by all checks."""

    def __init__(self):
        self.failures = 0

    def passed(self, name, detail):
        print("[PASS] {}: {}".format(name, detail))

    def skipped(self, name, detail):
        print("[SKIP] {}: {}".format(name, detail))

    def failed(self, name, detail):
        self.failures += 1
        print("[FAIL] {}: {}".format(name, detail))


def _read_text(path):
    """Read UTF-8 text and let the caller turn errors into a check failure."""
    with path.open("r", encoding="utf-8") as stream:
        return stream.read()


def _local_name(tag):
    """Return an XML tag's local name, including for namespaced tags."""
    return tag.rsplit("}", 1)[-1]


def _http_url(value):
    """Return a parsed absolute HTTP(S) URL, or raise ValueError."""
    value = value.strip()
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("expected an absolute http:// or https:// URL")
    if parsed.username or parsed.password:
        raise ValueError("embedded credentials are not allowed")
    if not parsed.hostname:
        raise ValueError("URL has no host")
    return parsed


def _normalise_route(path):
    """Normalise a README route and accept the product's reverse-proxy prefix."""
    if not path or not path.startswith("/"):
        return None
    path = path.split("?", 1)[0].split("#", 1)[0]
    path = re.sub(r"/{2,}", "/", path)
    if len(path) > 1:
        path = path.rstrip("/")
    if path.startswith("/md2html/"):
        return path[len("/md2html"):]
    return path


def _extract_routes(text):
    """Extract endpoint-looking paths from Markdown, commands, and URLs."""
    routes = set()

    for match in URL_RE.finditer(text):
        candidate = match.group(0).rstrip(".,;:!?`")
        try:
            path = urlparse(candidate).path
        except ValueError:
            continue
        route = _normalise_route(path)
        if route:
            routes.add(route)

    for match in ROUTE_RE.finditer(text):
        # Do not mistake an HTML closing tag such as </p> for an API route.
        if match.start() and text[match.start() - 1] == "<":
            continue
        route = _normalise_route(match.group(0))
        if route:
            routes.add(route)

    return routes


def _extract_live_bases(text):
    """Find API base URLs in README text without probing unrelated hyperlinks."""
    bases = []
    seen = set()
    for match in URL_RE.finditer(text):
        candidate = match.group(0).rstrip(".,;:!?`")
        try:
            parsed = _http_url(candidate)
        except ValueError:
            continue
        host = (parsed.hostname or "").lower()
        path = parsed.path.rstrip("/")
        # The repository README identifies the public API with /md2html. Do
        # not turn badges, GitHub links, or arbitrary documentation links into
        # live service probes.
        marker_match = re.search(r"/md2html(?=/|$)", path, re.IGNORECASE)
        if (
            marker_match is None
            or "github.com" in host
            or "shields.io" in host
            or host in {"example.com", "example.org", "example.net"}
        ):
            continue
        marker_index = marker_match.start()
        marker = marker_match.group(0)
        base_path = path[:marker_index] + path[marker_index:marker_index + len(marker)]
        base = "{}://{}{}".format(parsed.scheme, parsed.netloc, base_path)
        if base not in seen:
            seen.add(base)
            bases.append(base)
    return bases


def _yaml_top_level_lines(text):
    """Return simple top-level YAML key/value records.

    This is deliberately not a general YAML parser. It provides enough
    structure to validate a conventional OpenAPI YAML document while keeping
    this script standard-library-only.
    """
    records = []
    for number, line in enumerate(text.splitlines(), 1):
        if "\t" in line[: len(line) - len(line.lstrip())]:
            raise ValueError("line {} uses a tab for indentation".format(number))
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped in ("---", "..."):
            continue
        match = YAML_KEY_RE.match(line)
        if match and len(match.group("indent")) == 0:
            records.append((number, match.group("key"), match.group("value")))
    return records


def _yaml_nested_key(text, parent_key):
    """Find whether a conventional YAML mapping contains a child key."""
    lines = text.splitlines()
    parent_indent = None
    parent_line = None
    for index, line in enumerate(lines):
        match = YAML_KEY_RE.match(line)
        if not match:
            continue
        if len(match.group("indent")) == 0 and match.group("key") == parent_key:
            parent_indent = 0
            parent_line = index
            break
    if parent_line is None:
        return set()

    children = set()
    for line in lines[parent_line + 1 :]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = YAML_KEY_RE.match(line)
        if match and len(match.group("indent")) == parent_indent:
            break
        if match and len(match.group("indent")) > parent_indent:
            children.add(match.group("key"))
    return children


def _yaml_paths(text):
    """Extract path keys nested below a top-level ``paths:`` mapping."""
    lines = text.splitlines()
    paths_line = None
    for index, line in enumerate(lines):
        match = YAML_KEY_RE.match(line)
        if match and len(match.group("indent")) == 0 and match.group("key") == "paths":
            paths_line = index
            break
    if paths_line is None:
        return set()

    paths = set()
    for line in lines[paths_line + 1 :]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        top_level = YAML_KEY_RE.match(line)
        if top_level and len(top_level.group("indent")) == 0:
            break
        match = YAML_PATH_RE.match(line)
        if match:
            route = match.group(2).strip()
            if route:
                paths.add(route)
    return paths


def _validate_openapi_json(data):
    if not isinstance(data, dict):
        raise ValueError("document root must be an object")
    version = data.get("openapi")
    if not isinstance(version, str) or not re.match(r"^3\.\d+\.\d+$", version):
        raise ValueError("openapi must be a 3.x.y version string")
    info = data.get("info")
    if not isinstance(info, dict) or not info.get("title") or not info.get("version"):
        raise ValueError("info.title and info.version are required")
    paths = data.get("paths")
    if not isinstance(paths, dict) or not paths:
        raise ValueError("paths must be a non-empty object")
    invalid = sorted(str(route) for route in paths if not isinstance(route, str) or not route.startswith("/"))
    if invalid:
        raise ValueError("invalid path key(s): {}".format(", ".join(invalid[:5])))
    return set(paths)


def check_openapi(path, reporter):
    """Validate openapi.yaml when it exists; absence is explicitly optional."""
    if not path.exists():
        reporter.skipped("openapi.yaml", "not present (optional)")
        return set()
    try:
        text = _read_text(path)
        if not text.strip():
            raise ValueError("file is empty")
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            top_level = {key: value for _, key, value in _yaml_top_level_lines(text)}
            required = {"openapi", "info", "paths"}
            missing = sorted(required - set(top_level))
            if missing:
                raise ValueError("missing top-level key(s): {}".format(", ".join(missing)))
            if not OPENAPI_VERSION_RE.match(top_level["openapi"]):
                raise ValueError("openapi must be a 3.x.y version string")
            info_keys = _yaml_nested_key(text, "info")
            if not {"title", "version"}.issubset(info_keys):
                raise ValueError("info.title and info.version are required")
            routes = _yaml_paths(text)
            if not routes:
                raise ValueError("paths must contain at least one /route key")
            invalid = sorted(route for route in routes if not route.startswith("/"))
            if invalid:
                raise ValueError("invalid path key(s): {}".format(", ".join(invalid[:5])))
        else:
            routes = _validate_openapi_json(data)
        reporter.passed("openapi.yaml", "valid structure with {} route(s)".format(len(routes)))
        return routes
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        reporter.failed("openapi.yaml", str(exc))
        return set()


def check_robots(path, reporter):
    """Validate robots directives and require a sitemap declaration."""
    if not path.exists():
        reporter.failed("robots.txt", "file is missing")
        return
    try:
        text = _read_text(path)
        if not text.strip():
            raise ValueError("file is empty")
        user_agents = []
        sitemaps = []
        malformed = []
        for number, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if ":" not in stripped:
                malformed.append(str(number))
                continue
            name, value = stripped.split(":", 1)
            name = name.strip().lower()
            value = value.strip()
            if name == "user-agent" and value:
                user_agents.append(value)
            elif name == "sitemap" and value:
                sitemaps.append(value)
            elif name not in {"allow", "disallow", "crawl-delay", "host", "user-agent", "sitemap"}:
                malformed.append(str(number))
        if malformed:
            raise ValueError("malformed or unsupported directive line(s): {}".format(", ".join(malformed)))
        if not user_agents:
            raise ValueError("at least one User-agent directive is required")
        if not sitemaps:
            raise ValueError("at least one Sitemap directive is required")
        for sitemap in sitemaps:
            parsed = _http_url(sitemap)
            if not parsed.path.lower().rstrip("/").endswith("/sitemap.xml"):
                raise ValueError("Sitemap URL does not point to sitemap.xml: {}".format(sitemap))
        reporter.passed("robots.txt", "valid directives and {} sitemap reference(s)".format(len(sitemaps)))
    except (OSError, UnicodeError, ValueError) as exc:
        reporter.failed("robots.txt", str(exc))


def check_sitemap(path, reporter):
    """Parse sitemap.xml and validate absolute HTTP(S) locations."""
    if not path.exists():
        reporter.failed("sitemap.xml", "file is missing")
        return
    try:
        tree = ElementTree.parse(str(path))
        root = tree.getroot()
        root_name = _local_name(root.tag)
        if root_name not in {"urlset", "sitemapindex"}:
            raise ValueError("root element must be <urlset> or <sitemapindex>")
        locations = []
        for element in root.iter():
            if _local_name(element.tag) == "loc":
                value = (element.text or "").strip()
                if not value:
                    raise ValueError("<loc> must not be empty")
                _http_url(value)
                locations.append(value)
        if not locations:
            raise ValueError("at least one absolute <loc> is required")
        reporter.passed("sitemap.xml", "valid {} with {} location(s)".format(root_name, len(locations)))
    except (OSError, ElementTree.ParseError, ValueError) as exc:
        reporter.failed("sitemap.xml", str(exc))


def check_readme(path, expected_routes, reporter):
    """Ensure README contains route-shaped API documentation."""
    if not path.exists():
        reporter.failed("README routes", "README.md is missing")
        return
    try:
        text = _read_text(path)
        if not text.strip():
            raise ValueError("README.md is empty")
        routes = _extract_routes(text)
        if not routes:
            raise ValueError("no API route mentions found")
        if "/health" not in routes:
            raise ValueError("README must mention the /health route")
        if expected_routes:
            missing = sorted(expected_routes - routes)
            if missing:
                raise ValueError("missing OpenAPI route mention(s): {}".format(", ".join(missing[:10])))
        reporter.passed("README routes", "found {} route mention(s)".format(len(routes)))
    except (OSError, UnicodeError, ValueError) as exc:
        reporter.failed("README routes", str(exc))


def _live_urls_from_args(readme_text, explicit_urls):
    if explicit_urls:
        return explicit_urls
    configured = os.environ.get("VERIFY_LIVE_URLS", "").strip()
    if configured:
        return [value.strip() for value in configured.split(",") if value.strip()]
    bases = _extract_live_bases(readme_text)
    urls = []
    for base in bases:
        urls.extend((base + "/health", base + "/swagger.json"))
    return urls


def check_live_urls(urls, timeout, reporter):
    """Perform read-only GET smoke checks against configured live endpoints."""
    if not urls:
        reporter.skipped("live URLs", "none discovered; use --live-url or VERIFY_LIVE_URLS")
        return
    for raw_url in urls:
        name = "live {}".format(raw_url)
        try:
            parsed = _http_url(raw_url)
            request = Request(raw_url, headers={"User-Agent": DEFAULT_USER_AGENT}, method="GET")
            with urlopen(request, timeout=timeout) as response:
                status = response.getcode()
                body = response.read(4096)
            if status < 200 or status >= 400:
                raise ValueError("HTTP {}".format(status))
            if not body.strip():
                raise ValueError("empty response body (HTTP {})".format(status))
            if parsed.path.rstrip("/").lower().endswith("/health"):
                try:
                    health = json.loads(body.decode("utf-8", errors="replace"))
                except (TypeError, ValueError):
                    raise ValueError("health response is not JSON (HTTP {})".format(status))
                if not isinstance(health, dict) or health.get("status") != "ok":
                    raise ValueError("health response does not report status=ok")
            reporter.passed(name, "HTTP {}".format(status))
        except HTTPError as exc:
            reporter.failed(name, "HTTP {}".format(exc.code))
        except (OSError, URLError, ValueError) as exc:
            reporter.failed(name, str(exc))


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="repository root to validate (default: directory containing this script)",
    )
    parser.add_argument(
        "--live-url",
        action="append",
        dest="live_urls",
        help="read-only live URL to GET; may be repeated (overrides discovery)",
    )
    parser.add_argument(
        "--skip-live",
        action="store_true",
        help="skip live HTTP checks (also useful for offline/local-only validation)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="live HTTP timeout in seconds (default: {})".format(DEFAULT_TIMEOUT),
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    reporter = Reporter()
    root = args.root.resolve()
    if not root.is_dir():
        reporter.failed("repository root", "directory does not exist: {}".format(root))
        return 1
    if args.timeout <= 0:
        reporter.failed("arguments", "--timeout must be greater than zero")
        return 1

    openapi_routes = check_openapi(root / "openapi.yaml", reporter)
    check_robots(root / "robots.txt", reporter)
    check_sitemap(root / "sitemap.xml", reporter)

    readme_path = root / "README.md"
    try:
        readme_text = _read_text(readme_path) if readme_path.exists() else ""
    except (OSError, UnicodeError):
        readme_text = ""
    check_readme(readme_path, openapi_routes, reporter)

    if args.skip_live:
        reporter.skipped("live URLs", "disabled by --skip-live")
    else:
        check_live_urls(_live_urls_from_args(readme_text, args.live_urls), args.timeout, reporter)

    if reporter.failures:
        print("\nDistribution validation failed: {} check(s) failed.".format(reporter.failures))
        return 1
    print("\nDistribution validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
