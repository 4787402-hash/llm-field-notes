# -*- coding: utf-8 -*-
"""Static site generator. Run: python build.py"""
import html
import os
import shutil

import data

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
SITE_NAME = data.SITE["name"]

CSS = """
:root{--bg:#fff;--fg:#101114;--muted:#5c6270;--line:#e4e6eb;--card:#f7f8fa;--accent:#2f6f4f;--code:#f2f3f5}
@media (prefers-color-scheme:dark){
:root{--bg:#0d0f12;--fg:#e8eaee;--muted:#9aa2b1;--line:#22262d;--card:#14181d;--accent:#5ac08a;--code:#171b21}
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);
 font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,
 "PingFang SC","Microsoft YaHei",sans-serif;}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:760px;margin:0 auto;padding:0 20px}
header.site{border-bottom:1px solid var(--line);padding:18px 0;margin-bottom:40px}
header.site .wrap{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap}
header.site b{font-size:17px;letter-spacing:-.01em}
header.site span{color:var(--muted);font-size:13px}
h1{font-size:30px;line-height:1.25;letter-spacing:-.02em;margin:0 0 10px}
h2{font-size:20px;letter-spacing:-.01em;margin:38px 0 12px}
p{margin:0 0 14px}
.lede{color:var(--muted);font-size:17px;margin-bottom:34px}
code{background:var(--code);padding:2px 5px;border-radius:4px;font-size:13.5px;
 font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;word-break:break-word}
pre{background:var(--code);padding:14px 16px;border-radius:8px;overflow-x:auto;margin:0 0 16px}
pre code{background:none;padding:0;font-size:13px;line-height:1.55}
ol,ul{margin:0 0 16px;padding-left:22px}
li{margin-bottom:8px}
.errbox{border-left:3px solid #d9534f;background:var(--card);padding:12px 16px;border-radius:0 8px 8px 0;
 margin:0 0 22px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
 font-size:13px;line-height:1.5;overflow-x:auto;white-space:pre-wrap;word-break:break-word}
.meta{color:var(--muted);font-size:13px;margin:0 0 22px}
.meta b{color:var(--fg);font-weight:600}
ul.list{list-style:none;padding:0;margin:0}
ul.list li{border-top:1px solid var(--line);padding:14px 0;margin:0}
ul.list li:last-child{border-bottom:1px solid var(--line)}
ul.list a{font-weight:600;font-size:16px}
ul.list .sub{color:var(--muted);font-size:13.5px;margin-top:3px;display:block;
 font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
table{width:100%;border-collapse:collapse;margin:0 0 18px;font-size:14.5px}
th,td{text-align:left;padding:9px 0;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--muted);font-weight:600;font-size:13px;text-transform:uppercase;letter-spacing:.04em}
td:last-child{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.tag{display:inline-block;font-size:12px;color:var(--muted);border:1px solid var(--line);
 border-radius:999px;padding:1px 9px;margin:0 6px 6px 0}
footer.site{border-top:1px solid var(--line);margin-top:60px;padding:26px 0 50px;
 color:var(--muted);font-size:13px}
footer.site a{color:var(--muted);text-decoration:underline}
.verified{background:var(--card);border-radius:8px;padding:14px 16px;font-size:14px;
 color:var(--muted);margin:0 0 8px}
@media(max-width:600px){h1{font-size:25px}.wrap{padding:0 16px}}
"""


def esc(s):
    return html.escape(s, quote=False)


def page(title, desc, body, canonical, root=""):
    ld = (
        '{"@context":"https://schema.org","@type":"TechArticle",'
        f'"headline":{json_str(title)},"description":{json_str(desc)}}}'
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="article">
<style>{CSS}</style>
<script type="application/ld+json">{ld}</script>
</head>
<body>
<header class="site"><div class="wrap">
<a href="{root}index.html"><b>{esc(SITE_NAME)}</b></a>
<span>{esc(data.SITE["tagline"])}</span>
</div></header>
<main class="wrap">
{body}
</main>
<footer class="site"><div class="wrap">
<p>Every fix on this site was reproduced on real hardware before publication.
Corrections welcome.</p>
<p><a href="{root}index.html">All notes</a> · <a href="{root}benchmarks.html">Benchmarks</a></p>
</div></footer>
</body>
</html>"""


def json_str(s):
    import json
    return json.dumps(s)


def build_index():
    items = []
    for e in data.ERRORS:
        items.append(
            f'<li><a href="errors/{e["slug"]}.html">{esc(e["title"])}</a>'
            f'<span class="sub">{esc(e["err"][:110])}</span></li>'
        )
    notes = []
    for n in data.NOTES:
        notes.append(f'<li><a href="notes/{n["slug"]}.html">{esc(n["title"])}</a></li>')

    body = f"""<h1>Local AI, debugged on real hardware</h1>
<p class="lede">Exact error strings, why they happen, and the fix that worked - each one
reproduced before it was written down. No padding, no "have you tried reinstalling".</p>

<h2>Errors and fixes</h2>
<ul class="list">
{''.join(items)}
</ul>

<h2>Measured, not guessed</h2>
<p>The benchmark numbers behind these notes come from a single machine: AMD RX 6700 XT 12&nbsp;GB,
Ryzen 5 5600G, 16&nbsp;GB RAM, llama.cpp Vulkan backend, Qwen2.5 7B at Q4_K_M.</p>
<ul class="list">
<li><a href="benchmarks.html">Full benchmark table</a>
<span class="sub">prefill, generation, KV quantization, context growth</span></li>
{''.join(notes)}
</ul>
"""
    return page(
        "Local AI Field Notes - errors, fixes and real benchmarks",
        "Exact error messages from llama.cpp, LiteLLM, Codex, mihomo, OpenClash and Python on Windows, each with the root cause and a fix verified on real hardware.",
        body,
        f"{data.SITE['base']}/index.html",
    )


def build_error(e):
    fix = "".join(f"<li>{f}</li>" for f in e["fix"])
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in e["tags"])
    body = f"""<p class="meta"><a href="../index.html">&larr; All notes</a></p>
<h1>{esc(e["title"])}</h1>
<div class="errbox">{esc(e["err"])}</div>
<p class="meta"><b>Where:</b> {esc(e["stack"])}</p>

<h2>What you see</h2>
<p>{e["symptom"]}</p>

<h2>Why it happens</h2>
<p>{e["cause"]}</p>

<h2>Fix</h2>
<ol>{fix}</ol>

<h2>Verification</h2>
<div class="verified">{e["verify"]}</div>
<p>{tags}</p>
"""
    return page(
        e["title"],
        f"{e['err'][:150]} - cause and verified fix.",
        body,
        f"{data.SITE['base']}/errors/{e['slug']}.html",
        root="../",
    )


def build_note(n):
    paras = "".join(f"<p>{p}</p>" for p in n["body"])
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in n["tags"])
    body = f"""<p class="meta"><a href="../index.html">&larr; All notes</a></p>
<h1>{esc(n["title"])}</h1>
{paras}
<p>{tags}</p>
"""
    return page(n["title"], n["body"][0][:155], body,
                f"{data.SITE['base']}/notes/{n['slug']}.html", root="../")


def build_bench():
    parts = ["<h1>Benchmarks</h1>",
             '<p class="lede">One machine, measured repeatedly. Numbers are what the tools '
             'reported, not estimates.</p>',
             "<p><b>Test rig:</b> AMD RX 6700 XT 12 GB (Vulkan), Ryzen 5 5600G, 16 GB RAM, "
             "Windows 11. Model: Qwen2.5-7B-Instruct / Qwen2.5-Coder-7B-Instruct, "
             "GGUF Q4_K_M. Server: llama.cpp 0.8.0-dev.</p>"]
    for title, rows in data.BENCH_NOTES:
        parts.append(f"<h2>{esc(title)}</h2><table><tbody>")
        for k, v in rows:
            parts.append(f"<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>")
        parts.append("</tbody></table>")
    parts.append(
        "<h2>Reading these numbers</h2>"
        "<p>Prefill and generation are different bottlenecks. Generation is memory-bandwidth "
        "bound and scales with quantisation; prefill is compute bound and scales with batch "
        "size until attention starts to dominate. A single tok/s figure without saying which "
        "one is being measured is not useful.</p>"
    )
    return page("Benchmarks - local LLM on an RX 6700 XT",
                "Measured prefill and generation throughput for a 7B Q4_K_M model on an RX 6700 XT using llama.cpp's Vulkan backend, including KV quantization and context-length effects.",
                "".join(parts), f"{data.SITE['base']}/benchmarks.html")


def build_sitemap(slugs):
    urls = []
    for path in slugs:
        urls.append(f"<url><loc>{data.SITE['base']}/{path}</loc></url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + "".join(urls) + "</urlset>")


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "errors"))
    os.makedirs(os.path.join(OUT, "notes"))

    slug_list = ["index.html", "benchmarks.html"]

    write(os.path.join(OUT, "index.html"), build_index())
    write(os.path.join(OUT, "benchmarks.html"), build_bench())
    slug_list.append("benchmarks.html")

    for e in data.ERRORS:
        write(os.path.join(OUT, "errors", e["slug"] + ".html"), build_error(e))
        slug_list.append("errors/" + e["slug"] + ".html")
    for n in data.NOTES:
        write(os.path.join(OUT, "notes", n["slug"] + ".html"), build_note(n))
        slug_list.append("notes/" + n["slug"] + ".html")

    write(os.path.join(OUT, "sitemap.xml"), build_sitemap(sorted(set(slug_list))))
    write(os.path.join(OUT, "robots.txt"),
          "User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % data.SITE["base"])
    write(os.path.join(OUT, ".nojekyll"), "")

    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    if os.path.isdir(static_dir):
        for name in os.listdir(static_dir):
            src = os.path.join(static_dir, name)
            if os.path.isfile(src):
                shutil.copyfile(src, os.path.join(OUT, name))

    print(f"built {len(slug_list)} pages -> {OUT}")


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


if __name__ == "__main__":
    main()
