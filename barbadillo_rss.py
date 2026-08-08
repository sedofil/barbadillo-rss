#!/usr/bin/env python3
import html
import re
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from urllib.parse import urljoin, urlparse
from xml.etree.ElementTree import Element, SubElement, ElementTree

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

SITE = "https://www.barbadillo.it/"
OUTPUT = "feed.xml"
MAX_ITEMS = 50

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; BarbadilloRSS/1.0; +https://github.com/)"
}

SKIP_PATH_PARTS = (
    "/category/", "/tag/", "/author/", "/blog/", "/privacy", "/contatti",
    "/il-clan", "/wp-content/", "/wp-json/", "/feed", "/comments/"
)

def clean(text):
    return re.sub(r"\s+", " ", (text or "")).strip()

def same_site_article(url):
    p = urlparse(url)
    if p.netloc not in ("www.barbadillo.it", "barbadillo.it"):
        return False
    path = p.path.rstrip("/") + "/"
    if path in ("//", "/"):
        return False
    if any(part in path.lower() for part in SKIP_PATH_PARTS):
        return False
    return True

def parse_date(value):
    if not value:
        return None
    value = clean(value)
    # ISO / RFC-like values first
    try:
        dt = dateparser.parse(value, dayfirst=True)
        if dt:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
    except Exception:
        pass
    return None

def meta(soup, *keys):
    for key in keys:
        tag = soup.find("meta", attrs={"property": key}) or soup.find("meta", attrs={"name": key})
        if tag and tag.get("content"):
            return clean(tag["content"])
    return ""

def article_details(session, url, fallback_title):
    try:
        r = session.get(url, headers=HEADERS, timeout=25)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        title = meta(soup, "og:title", "twitter:title") or fallback_title
        description = meta(soup, "og:description", "description", "twitter:description")
        author = meta(soup, "author", "article:author")
        published_raw = meta(
            soup, "article:published_time", "datePublished", "date", "parsely-pub-date"
        )

        if not published_raw:
            time_tag = soup.find("time")
            if time_tag:
                published_raw = time_tag.get("datetime") or time_tag.get_text(" ", strip=True)

        if not author:
            # Common WordPress/theme author classes.
            a = soup.select_one(".author-name, .post-author, .entry-author, [rel='author']")
            if a:
                author = clean(a.get_text(" ", strip=True))

        return {
            "title": clean(title),
            "url": url,
            "description": clean(description),
            "author": clean(author),
            "published": parse_date(published_raw),
        }
    except Exception as exc:
        print(f"ATTENZIONE: non riesco a leggere {url}: {exc}", file=sys.stderr)
        return {
            "title": clean(fallback_title),
            "url": url,
            "description": "",
            "author": "",
            "published": None,
        }

def discover_articles(session):
    r = session.get(SITE, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    candidates = []
    seen = set()

    # Barbadillo currently places article titles mainly in H3 elements.
    selectors = ["h3 a[href]", "h2 a[href]", "article a[href]"]
    for selector in selectors:
        for a in soup.select(selector):
            title = clean(a.get_text(" ", strip=True))
            url = urljoin(SITE, a.get("href", ""))
            if len(title) < 18 or not same_site_article(url):
                continue
            url = url.split("#", 1)[0]
            if url in seen:
                continue
            seen.add(url)
            candidates.append((title, url))
            if len(candidates) >= MAX_ITEMS:
                return candidates
    return candidates

def build_feed(items):
    rss = Element("rss", {"version": "2.0"})
    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = "Barbadillo.it – Tutti gli articoli"
    SubElement(channel, "link").text = SITE
    SubElement(channel, "description").text = (
        "Feed RSS non ufficiale degli ultimi articoli pubblicati su Barbadillo.it"
    )
    SubElement(channel, "language").text = "it-IT"
    SubElement(channel, "lastBuildDate").text = format_datetime(datetime.now(timezone.utc))

    for it in items:
        node = SubElement(channel, "item")
        SubElement(node, "title").text = it["title"]
        SubElement(node, "link").text = it["url"]
        guid = SubElement(node, "guid", {"isPermaLink": "true"})
        guid.text = it["url"]

        if it.get("description"):
            SubElement(node, "description").text = it["description"]
        if it.get("author"):
            SubElement(node, "author").text = it["author"]
        if it.get("published"):
            SubElement(node, "pubDate").text = format_datetime(it["published"])

    tree = ElementTree(rss)
    tree.write(OUTPUT, encoding="utf-8", xml_declaration=True)

def main():
    with requests.Session() as session:
        found = discover_articles(session)
        if not found:
            raise RuntimeError("Nessun articolo trovato nella homepage di Barbadillo.")
        print(f"Trovati {len(found)} possibili articoli.")
        items = [article_details(session, url, title) for title, url in found]

    # Newest first when publication dates are available; otherwise retain homepage order.
    indexed = list(enumerate(items))
    indexed.sort(
        key=lambda pair: (
            pair[1]["published"] is not None,
            pair[1]["published"] or datetime.min.replace(tzinfo=timezone.utc),
            -pair[0],
        ),
        reverse=True,
    )
    items = [x[1] for x in indexed]
    build_feed(items)
    print(f"Creato {OUTPUT} con {len(items)} articoli.")

if __name__ == "__main__":
    main()
