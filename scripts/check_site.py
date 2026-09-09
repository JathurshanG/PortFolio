#!/usr/bin/env python3
"""Dependency-free checks for local links, metadata and the static sitemap.

This is a regression check, not a complete HTML5 or accessibility audit.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from urllib.robotparser import RobotFileParser

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://jathurshang.github.io/PortFolio/"
VERIFY = "google2152c437bb871421.html"
VOID = set("area base br col embed hr img input link meta param source track wbr".split())


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.nodes = []
        self.stack = []
        self.feed(path.read_text(encoding="utf-8"))
        self.close()
        require(not self.stack, f"{path.name}: unclosed HTML tags")
        self.ids = [n["attrs"]["id"] for n in self.nodes if "id" in n["attrs"]]

    def handle_starttag(self, tag, attrs):
        require(len(attrs) == len(dict(attrs)), f"{self.path.name}: duplicate attributes")
        node = {"tag": tag, "attrs": dict(attrs), "text": ""}
        self.nodes.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        require(self.stack and self.stack[-1]["tag"] == tag,
                f"{self.path.name}: unexpected closing tag </{tag}>")
        self.stack.pop()

    def handle_data(self, data):
        for node in self.stack:
            node["text"] += data

    def select(self, tag, **attrs):
        return [n for n in self.nodes if n["tag"] == tag
                and all(n["attrs"].get(k) == v for k, v in attrs.items())]

    def one(self, tag, **attrs):
        nodes = self.select(tag, **attrs)
        require(len(nodes) == 1, f"{self.path.name}: expected one {tag} {attrs}")
        return nodes[0]

    def meta(self, key, value):
        node = self.one("meta", **{key: value})
        content = node["attrs"].get("content", "")
        require(content.strip(), f"{self.path.name}: empty metadata {value}")
        return content


def local_target(value, source):
    absolute = urlsplit(urljoin(SITE + source.path.name, value))
    site = urlsplit(SITE)
    if absolute.scheme not in ("http", "https") or absolute.netloc != site.netloc:
        return None
    require(absolute.path.startswith(site.path), f"Link outside /PortFolio/: {value}")
    relative = unquote(absolute.path[len(site.path):])
    path = (ROOT / relative).resolve()
    require(path.is_relative_to(ROOT), f"Link escapes repository: {value}")
    if path.is_dir():
        path = path / "index.html"
    require(path.is_file(), f"{source.path.name}: missing local target {value}")
    return path, unquote(absolute.fragment)


def validate():
    pages = {p.resolve(): Page(p) for p in ROOT.glob("*.html") if p.name != VERIFY}
    require(ROOT / "index.html" in pages and ROOT / "projects.html" in pages,
            "Missing portfolio entrypoints")
    canonicals = []
    checked_links = 0
    works = []
    for path, page in pages.items():
        require(path.read_text(encoding="utf-8").lower().startswith("<!doctype html>"),
                f"{path.name}: missing HTML5 doctype")
        require(page.one("html")["attrs"].get("lang") == "fr", f"{path.name}: wrong language")
        page.one("meta", charset="UTF-8")
        viewport = page.meta("name", "viewport")
        require("width=device-width" in viewport and "user-scalable=no" not in viewport
                and "maximum-scale" not in viewport, f"{path.name}: viewport restricts zoom")
        title = page.one("title")["text"].strip()
        require(title and page.meta("name", "description"), f"{path.name}: missing SEO text")
        page.one("h1")
        page.one("main")
        require(all(count == 1 for count in Counter(page.ids).values()),
                f"{path.name}: duplicate IDs")
        levels = [int(n["tag"][1]) for n in page.nodes if re.fullmatch(r"h[1-6]", n["tag"])]
        require(levels[0] == 1 and all(b <= a + 1 for a, b in zip(levels, levels[1:])),
                f"{path.name}: skipped heading level")
        canonical = page.one("link", rel="canonical")["attrs"]["href"]
        expected = SITE if path.name == "index.html" else SITE + path.name
        require(canonical == expected, f"{path.name}: incorrect canonical")
        canonicals.append(canonical)
        require(page.meta("property", "og:url") == canonical, f"{path.name}: inconsistent og:url")
        require(page.meta("property", "og:title") == title, f"{path.name}: inconsistent og:title")
        for key in ("og:type", "og:locale", "og:site_name", "og:description"):
            page.meta("property", key)
        require(page.meta("name", "twitter:title") == title, f"{path.name}: inconsistent X title")
        page.meta("name", "twitter:card")
        page.meta("name", "twitter:description")
        require(page.select("a", href="#main-content"), f"{path.name}: missing skip link")
        require(page.one("main")["attrs"].get("tabindex") == "-1",
                f"{path.name}: main cannot receive skip-link focus")
        for node in page.nodes:
            attrs = node["attrs"]
            require(not any(key.startswith("on") for key in attrs), f"{path.name}: inline JS handler")
            for key in ("aria-labelledby", "aria-describedby"):
                require(all(ref in page.ids for ref in attrs.get(key, "").split()),
                        f"{path.name}: broken {key}")
            if node["tag"] == "nav":
                require(attrs.get("aria-label") or attrs.get("aria-labelledby"),
                        f"{path.name}: unlabelled navigation")
            if node["tag"] == "a":
                require(node["text"].strip() or attrs.get("aria-label"),
                        f"{path.name}: unnamed link")
            if node["tag"] == "img":
                require("alt" in attrs and "width" in attrs and "height" in attrs,
                        f"{path.name}: image lacks alt text or stable dimensions")
            for key in ("href", "src"):
                if key not in attrs:
                    continue
                value = attrs[key]
                require(value and not value.lower().startswith("javascript:"),
                        f"{path.name}: invalid link")
                target = local_target(value, page)
                if target:
                    target_path, fragment = target
                    if fragment:
                        require(target_path in pages and fragment in pages[target_path].ids,
                                f"{path.name}: broken fragment {value}")
                    checked_links += 1
            if node["tag"] == "script":
                require(attrs.get("type") == "application/ld+json",
                        f"{path.name}: unexpected executable JavaScript")
                data = json.loads(node["text"])
                require(data.get("@context") == "https://schema.org", "Invalid JSON-LD context")
                graph = data.get("@graph", [])
                require(any(n.get("@type") == "Person" for n in graph), "Missing Person")
                works.extend(n for n in graph if n.get("@type") == "CreativeWork")
        require(page.select("script", type="application/ld+json"), f"{path.name}: missing JSON-LD")
        require(not page.select("meta", name="robots", content="noindex"),
                f"{path.name}: accidental noindex")

    projects = pages[ROOT / "projects.html"]
    articles = projects.select("article")
    require(len(works) == len(articles), "JSON-LD and visible project count differ")
    for work in works:
        target = local_target(work["url"], projects)
        require(target and target[0] == projects.path and target[1] in projects.ids,
                "CreativeWork points to a missing project")
        article = projects.one("article", id=target[1])
        heading = next(n for n in projects.nodes
                       if n["attrs"].get("id") == article["attrs"]["aria-labelledby"])
        require(heading["text"] == work["name"], "CreativeWork title differs from visible title")
    for legacy in ("project-1", "project-2", "project-3"):
        require(legacy in projects.ids, f"Broken legacy bookmark #{legacy}")
    require(all(not re.fullmatch(r"project-\d+", a["attrs"]["id"]) for a in articles),
            "Projects need semantic article IDs")

    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    tree = ET.parse(ROOT / "sitemap.xml").getroot()
    require(tree.tag == ns + "urlset", "Incorrect sitemap namespace")
    locations = [node.text for node in tree.findall(f"{ns}url/{ns}loc")]
    require(len(locations) == len(set(locations)) and set(locations) == set(canonicals),
            "Sitemap must contain exactly the canonical content pages")
    require(not (ROOT / "robot.txt").exists(), "Misspelled robot.txt still exists")
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    require("Sitemap: Sitemap:" not in robots, "Duplicated Sitemap directive")
    parser = RobotFileParser()
    parser.parse(robots.splitlines())
    require(parser.site_maps() == [SITE + "sitemap.xml"], "Incorrect robots sitemap URL")
    require(all(parser.can_fetch("Googlebot", url) for url in canonicals), "Googlebot disallowed")
    require((ROOT / VERIFY).read_bytes() == f"google-site-verification: {VERIFY}".encode(),
            "Google verification file has changed")
    print(f"PASS: {len(pages)} pages, {checked_links} local references, {len(works)} projects; "
          "headings, metadata, JSON-LD, robots, sitemap and Google verification.")


if __name__ == "__main__":
    try:
        validate()
    except (ValueError, OSError, KeyError, ET.ParseError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
