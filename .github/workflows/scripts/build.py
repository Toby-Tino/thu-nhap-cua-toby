# -*- coding: utf-8 -*-
import json, os, shutil, datetime, html

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, '..'))
PUBLIC = os.path.join(ROOT, 'public')
CONTENT = os.path.join(ROOT, 'content')

def read_json(path, default=None):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return default

def clean_public():
    if os.path.exists(PUBLIC):
        shutil.rmtree(PUBLIC)
    os.makedirs(PUBLIC, exist_ok=True)

def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

def build():
    site = read_json(os.path.join(CONTENT, 'site.json'), {})
    base_url = site.get('base_url','').rstrip('/')
    name = site.get('name', 'Site')

    pages = read_json(os.path.join(CONTENT, 'pages.json'), [])

    clean_public()

    TEMPLATE = """<!doctype html><html lang="vi"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link rel="canonical" href="{canonical}">
<meta name="description" content="{meta}">
<style>
body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;line-height:1.6;margin:0;background:#fff;color:#111}}
.header, .footer{{padding:16px 24px;border-bottom:1px solid #eee}}
.footer{{border-top:1px solid #eee;border-bottom:none;margin-top:48px}}
main{{max-width:880px;margin:24px auto;padding:0 16px}}
.card{{border:1px solid #eee;border-radius:8px;padding:16px;margin:16px 0}}
label{{display:block;margin:8px 0 4px}}
input,select,button{{padding:8px 10px;border:1px solid #ccc;border-radius:6px}}
button{{cursor:pointer}}
.cta{{display:inline-block;margin-top:16px;padding:12px 16px;border-radius:8px;border:1px solid #0a0;text-decoration:none}}
.small{{font-size:13px;color:#555}}
a{{color:#0645AD;text-decoration:none}} a:hover{{text-decoration:underline}}
</style>
<script>
function fmt(n){{try{{return new Intl.NumberFormat('vi-VN').format(n)}}catch(e){{return n}}}}
function calc(){{{var_decls}
{js_calc}
}}
document.addEventListener('DOMContentLoaded', function(){{
  try {{ calc(); }} catch(e) {{ console.error(e); }}
}});
</script>
</head><body>
<header class="header"><strong>{site_name}</strong></header>
<main>
<h1>{h1}</h1>
<p class="small">{intro}</p>
<div class="card">
<form oninput="calc()">
{form_fields}
</form>
<div id="result" class="card"></div>
<a class="cta" rel="nofollow sponsored" target="_blank" href="{aff_url}">{aff_text}</a>
<p class="small">{disclaimer}</p>
</div>
<div class="card">
<h2>Giải thích & Câu hỏi thường gặp</h2>
{faq_html}
</div>
</main>
<footer class="footer"><span class="small">© {year} {site_name}</span></footer>
</body></html>
"""

    urls = []
    # Build calculator pages
    for p in pages:
        slug = p['slug']
        out = os.path.join(PUBLIC, f"{slug}.html")

        # Build form & vars
        fields = p.get('fields', [])
        fields_html = []
        var_decls = []
        for f in fields:
            fid = f['id']
            label = html.escape(f.get('label', fid))
            ftype = f.get('type','number')
            value = html.escape(str(f.get('value', '')))
            if ftype == 'select':
                opts = ""
                for o in f.get('options', []):
                    ov = html.escape(str(o.get('value','')))
                    ol = html.escape(str(o.get('label', ov)))
                    opts += f'<option value="{ov}">{ol}</option>'
                fields_html.append(f'<label for="{fid}">{label}</label><select id="{fid}">{opts}</select>')
            else:
                fields_html.append(f'<label for="{fid}">{label}</label><input id="{fid}" type="{ftype}" value="{value}">')
            var_decls.append(f"var {fid} = parseFloat(document.getElementById('{fid}').value||0);")

        form_fields = "\n".join(fields_html)
        var_decl_str = "\n".join(var_decls)

        html_out = TEMPLATE.format(
            title=html.escape(p['title']),
            canonical=f"{base_url}/{slug}.html",
            meta=html.escape(p.get('meta','')),
            site_name=html.escape(name),
            h1=html.escape(p.get('h1', p['title'])),
            intro=html.escape(p.get('intro','')),
            form_fields=form_fields,
            aff_url=p['affiliate']['url'],
            aff_text=html.escape(p['affiliate']['text']),
            disclaimer=html.escape(p.get('disclaimer','Kết quả chỉ mang tính tham khảo.')),
            faq_html=p.get('faq_html',''),
            js_calc=p['js_calc'],
            var_decls=var_decl_str,
            year=datetime.datetime.utcnow().year
        )
        write(out, html_out)
        urls.append(f"{base_url}/{slug}.html")

    # Index
    links = "\n".join([f'<li><a href="{u}">{html.escape(u.split("/")[-1].replace(".html","").replace("-"," ").title())}</a></li>' for u in urls])
    index_html = f"""<!doctype html><html lang="vi"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(name)}</title>
<meta name="description" content="Bộ công cụ tính nhanh — miễn phí">
<style>
body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;line-height:1.6;margin:0;background:#fff;color:#111}}
.header, .footer{{padding:16px 24px;border-bottom:1px solid #eee}}
.footer{{border-top:1px solid #eee;border-bottom:none;margin-top:48px}}
main{{max-width:880px;margin:24px auto;padding:0 16px}}
.card{{border:1px solid #eee;border-radius:8px;padding:16px;margin:16px 0}}
a{{color:#0645AD;text-decoration:none}} a:hover{{text-decoration:underline}}
.small{{font-size:13px;color:#555}}
</style>
</head><body>
<header class="header"><strong>{html.escape(name)}</strong></header>
<main>
<h1>Danh sách công cụ</h1>
<div class="card">
<ol>
{links}
</ol>
</div>
</main>
<footer class="footer"><span class="small">© {datetime.datetime.utcnow().year} {html.escape(name)}</span></footer>
</body></html>"""
    write(os.path.join(PUBLIC, "index.html"), index_html)

    # robots.txt
    robots = "User-agent: *\nAllow: /\nSitemap: {}/sitemap.xml\n".format(base_url)
    write(os.path.join(PUBLIC, "robots.txt"), robots)

    # sitemap.xml
    lastmod = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    urlset = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in [f"{base_url}/index.html"] + urls:
        urlset.append("<url>")
        urlset.append(f"<loc>{u}</loc>")
        urlset.append(f"<lastmod>{lastmod}</lastmod>")
        urlset.append("<changefreq>weekly</changefreq>")
        urlset.append("<priority>0.6</priority>")
        urlset.append("</url>")
    urlset.append("</urlset>")
    write(os.path.join(PUBLIC, "sitemap.xml"), "\n".join(urlset))

if __name__ == "__main__":
    build()
