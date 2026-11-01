#!/usr/bin/env python3
"""data/quotes.json から index.html を作る（Vercelはこのindex.htmlをそのまま公開します）。

使い方:  python3 build.py
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
DATA = json.loads((ROOT / "data" / "quotes.json").read_text(encoding="utf-8"))
SITE = DATA.get("site", {})
QUOTES = DATA.get("quotes", [])

# ことばがこの件数に届くまでは、検索エンジンに載せない（中身が少ないページを載せないため）
MIN_QUOTES_TO_INDEX = 10

TR = {"official": "公式の訳", "own": "自分の訳", "auto": "自動翻訳・未確認"}
e = html.escape


def fmt_date(d):
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", d or "")
    return f"{m[1]}年{int(m[2])}月{int(m[3])}日" if m else (d or "")


def safe_url(u):
    return u if re.match(r"https?://", u or "", re.I) else None


def host_of(u):
    m = re.match(r"https?://(?:www\.)?([^/]+)", u or "")
    return m[1] if m else u


def entry(q):
    parts = [f'<p class="quote">{e(q.get("text", ""))}</p>']
    if q.get("en"):
        parts.append(f'<p class="en" lang="en">{e(q["en"])}</p>')
    if q.get("ko"):
        parts.append(f'<p class="ko" lang="ko">{e(q["ko"])}</p>')
    meta = []
    url = safe_url(q.get("url"))
    if q.get("source") or url:
        label = e(q.get("source") or host_of(url))
        link = f'<a href="{e(url)}" target="_blank" rel="noopener noreferrer">{label}</a>' if url else label
        meta.append(f"<span>出典 {link}</span>")
    if q.get("date"):
        meta.append(f"<span>{e(fmt_date(q['date']))}</span>")
    if q.get("tr") in TR:
        meta.append(f'<span class="badge {q["tr"]}">{TR[q["tr"]]}</span>')
    if meta:
        parts.append('<div class="meta">' + "".join(meta) + "</div>")
    if q.get("context"):
        parts.append(f'<p class="context">{e(q["context"])}</p>')
    tags = q.get("tags") or []
    if tags:
        btns = "".join(f'<button class="tag" type="button" data-tag="{e(t)}">#{e(t)}</button>' for t in tags)
        parts.append(f'<div class="tags">{btns}</div>')
    attr = e("|".join(tags))
    return f'<article class="entry" data-tags="{attr}">' + "".join(parts) + "</article>"


def tag_chips():
    counts = {}
    for q in QUOTES:
        for t in q.get("tags") or []:
            counts[t] = counts.get(t, 0) + 1
    if not counts:
        return ""
    chips = ['<button class="chip" type="button" data-tag="" aria-pressed="true">すべて</button>']
    for t, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        chips.append(f'<button class="chip" type="button" data-tag="{e(t)}" aria-pressed="false">#{e(t)} {n}</button>')
    return '<div class="filters" id="filters" role="group" aria-label="タグで絞り込み" hidden>' + "".join(chips) + "</div>"


def main():
    full_title = SITE.get("title") or "Wonyoung Quotes — in her own words"
    main_title, _, sub_title = full_title.partition(" — ")
    intro = SITE.get("intro") or ""
    description = (
        "IVE チャン・ウォニョン（장원영）さんのことばを、日本語・英語・韓国語で、出典つきでまとめています。"
        "Wonyoung quotes, with sources."
    )
    robots = "index,follow" if len(QUOTES) >= MIN_QUOTES_TO_INDEX else "noindex,follow"
    if QUOTES:
        body = "\n".join(entry(q) for q in QUOTES)
        count = f'<p class="count" id="count">{len(QUOTES)}件のことば</p>'
    else:
        body = '<div class="empty"><strong>準備中です</strong><p>ことばを集めています。もう少しお待ちください。</p></div>'
        count = ""
    sub_html = f'<span class="sub">{e(sub_title)}</span>' if sub_title else ""
    out = TEMPLATE
    for key, val in {
        "@@LANG_TITLE@@": e(full_title),
        "@@DESC@@": e(description),
        "@@ROBOTS@@": robots,
        "@@H1@@": e(main_title) + sub_html,
        "@@INTRO@@": f'<p class="intro">{e(intro)}</p>' if intro else "",
        "@@FILTERS@@": tag_chips(),
        "@@COUNT@@": count,
        "@@BODY@@": body,
    }.items():
        out = out.replace(key, val)
    (ROOT / "index.html").write_text(out, encoding="utf-8")
    print(f"index.html を作りました（{len(QUOTES)}件、robots={robots}）")


TEMPLATE = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>@@LANG_TITLE@@</title>
<meta name="description" content="@@DESC@@">
<meta name="robots" content="@@ROBOTS@@">
<meta property="og:type" content="website">
<meta property="og:title" content="@@LANG_TITLE@@">
<meta property="og:description" content="@@DESC@@">
<meta name="twitter:card" content="summary">
<meta name="color-scheme" content="light dark">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500&family=Shippori+Mincho+B1:wght@500;700&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap">
<style>
:root {
  --bg: #fcf4f7; --ink: #2b1d28; --muted: #74636f; --line: #ebd8e1;
  --accent: #b8336a; --soft: #f6e4ec; --lilac: #6a56b0; --ok: #2f7d5b; --warn: #8f6210;
  --font-display: "Shippori Mincho B1", "Hiragino Mincho ProN", "Yu Mincho", serif;
  --font-body: "Zen Kaku Gothic New", "Hiragino Sans", "Yu Gothic", system-ui, sans-serif;
  --font-ko: "Noto Sans KR", "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root { --bg: #1b1319; --ink: #f4e7ee; --muted: #b09ca8; --line: #3a2a35; --accent: #f08cb4; --soft: #2a1d26; --lilac: #b9abf2; --ok: #7bcba3; --warn: #e3b85f; }
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--ink);
  font-family: var(--font-body); font-size: 15px; line-height: 1.75;
  padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px));
  padding-block: 40px 56px;
}
.wrap { max-width: 700px; margin: 0 auto; }
button { font: inherit; color: inherit; cursor: pointer; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 3px; }
header { padding-bottom: 28px; border-bottom: 1px solid var(--line); }
.kicker { font-size: 12px; letter-spacing: .14em; color: var(--accent); font-weight: 700; margin: 0 0 10px; }
h1 { font-family: var(--font-display); font-weight: 700; font-size: clamp(30px, 7vw, 44px); line-height: 1.25; margin: 0 0 12px; text-wrap: balance; }
h1 .sub { display: block; margin-top: 6px; font-family: var(--font-body); font-size: 15px; font-weight: 500; letter-spacing: .04em; color: var(--muted); }
.intro { margin: 0; color: var(--muted); max-width: 34em; }
.filters { display: flex; flex-wrap: wrap; gap: 8px; margin: 22px 0 4px; }
.filters[hidden] { display: none; }
.chip { border: 1px solid var(--line); background: transparent; border-radius: 999px; padding: 2px 12px; font-size: 13px; color: var(--muted); min-height: 30px; }
.chip[aria-pressed="true"] { background: var(--soft); border-color: var(--accent); color: var(--ink); font-weight: 700; }
.count { color: var(--muted); font-size: 13px; margin: 18px 0 0; }
.entry { padding: 34px 0; border-bottom: 1px solid var(--line); }
.entry[hidden] { display: none; }
.quote { font-family: var(--font-display); font-weight: 500; font-size: clamp(20px, 4.6vw, 26px); line-height: 1.7; margin: 0; white-space: pre-wrap; overflow-wrap: anywhere; text-wrap: pretty; }
.quote::before { content: "「"; color: var(--accent); }
.quote::after { content: "」"; color: var(--accent); }
.en, .ko { font-size: 14px; color: var(--muted); margin: 12px 0 0; white-space: pre-wrap; overflow-wrap: anywhere; line-height: 1.7; }
.en + .ko { margin-top: 4px; }
.ko { font-family: var(--font-ko); }
.en::before, .ko::before { display: inline-block; min-width: 2.2em; margin-right: 6px; font-family: var(--font-body); font-size: 11px; letter-spacing: .08em; font-weight: 700; color: var(--accent); }
.en::before { content: "EN"; }
.ko::before { content: "KO"; }
.meta { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 14px; margin: 14px 0 0; font-size: 13px; color: var(--muted); }
.meta a { color: var(--lilac); text-underline-offset: 3px; overflow-wrap: anywhere; }
.badge { display: inline-flex; align-items: center; gap: 6px; }
.badge::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: currentColor; }
.badge.official, .badge.own { color: var(--ok); }
.badge.auto { color: var(--warn); }
.context { margin: 8px 0 0; font-size: 13px; color: var(--muted); overflow-wrap: anywhere; }
.tags { display: flex; flex-wrap: wrap; gap: 4px 12px; margin-top: 12px; }
.tag { border: 0; background: none; padding: 0; font-size: 13px; color: var(--lilac); }
.tag:hover { text-decoration: underline; text-underline-offset: 3px; }
.empty { padding: 56px 0; color: var(--muted); }
.empty strong { display: block; font-family: var(--font-display); font-size: 20px; color: var(--ink); margin-bottom: 8px; }
.empty p { margin: 0; }
footer { margin-top: 36px; font-size: 12px; color: var(--muted); max-width: 36em; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <p class="kicker">IVE ／ 장원영</p>
    <h1>@@H1@@</h1>
    @@INTRO@@
  </header>
  @@FILTERS@@
  @@COUNT@@
  <main id="list">
@@BODY@@
  </main>
  <footer>IVE・ウォニョン（장원영）さんの非公式ファンページです。ことばの権利は本人と各媒体に帰属します。引用には出典を添えています。</footer>
</div>
<script>
(function () {
  var f = document.getElementById("filters");
  if (!f) return;
  f.hidden = false;
  var chips = f.querySelectorAll(".chip");
  var items = document.querySelectorAll(".entry");
  var count = document.getElementById("count");
  var total = items.length;
  var current = "";
  function apply(tag) {
    current = tag;
    chips.forEach(function (c) { c.setAttribute("aria-pressed", String((c.dataset.tag || "") === tag)); });
    var shown = 0;
    items.forEach(function (a) {
      var ok = !tag || (a.dataset.tags || "").split("|").indexOf(tag) >= 0;
      a.hidden = !ok;
      if (ok) shown++;
    });
    if (count) count.textContent = tag ? "#" + tag + "　" + shown + "件" : total + "件のことば";
  }
  document.addEventListener("click", function (ev) {
    var b = ev.target.closest(".chip, .tag");
    if (!b) return;
    var t = b.dataset.tag || "";
    apply(t && t === current ? "" : t);
    if (b.classList.contains("tag")) window.scrollTo({ top: 0 });
  });
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
