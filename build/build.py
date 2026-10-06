#!/usr/bin/env python3
"""Static page generator for technicalrecruiters.biz inner pages.
Run: python3 build/build.py  (from the site root). Writes clean-URL folders."""
import json, html, os, datetime
from content import ROLES, ABOUT, PLACEMENTS_PAGE

SITE = "https://technicalrecruiters.biz"
BOOK = "https://calendar.google.com/calendar/appointments/schedules/AcZssZ1-F_s8aI-SgJgVVm9vL-GoWoNCXweWznThkTkxh9ZaDxmDvNqA6Y6GyefdulDhYhVtTOB82xdd"
TODAY = datetime.date.today().isoformat()

LOGO = '<svg class="mark" viewBox="256 315 494 545" aria-hidden="true"><path fill="currentColor" d="M508 315H750V557H628V436H508Z"/><path fill="#CE6F67" d="M332 436H508V557H256Z"/><path fill="#CE6F67" d="M508 557H628V793L508 860Z"/></svg>'

def esc(s): return html.escape(s, quote=True)

def head(title, desc, path, schema_blocks, og_type="article"):
    url = f"{SITE}{path}"
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>' for b in schema_blocks)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Technical Recruiters">
<meta property="og:image" content="{SITE}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
{ld}
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta name="theme-color" content="#F7F5F4">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=Schibsted+Grotesk:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="/styles.css">
</head>
<body>
<header>
  <nav class="wrap nav" aria-label="Main">
    <a class="brand" href="/">{LOGO}Technical Recruiters</a>
    <ul>
      <li><a href="/#candidates">Candidates</a></li>
      <li><a href="/hire/">Hire</a></li>
      <li><a href="/placements/">Placements</a></li>
      <li><a href="/about/">About</a></li>
    </ul>
    <a class="btn btn-primary" href="/#contact">Get in touch</a>
  </nav>
</header>
<main id="top">
'''

FOOT = f'''
</main>
<footer>
  <div class="wrap"><span>&copy; <span id="yr">2026</span> Technical Recruiters LLC</span><span>Top 5% talent for venture-backed startups &middot; <a href="https://www.linkedin.com/company/ustechnical-recruiters/" target="_blank" rel="noopener">LinkedIn</a></span></div>
</footer>
<script>document.getElementById("yr").textContent=new Date().getFullYear();</script>
</body>
</html>
'''

def crumbs(items):
    ld = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":n,"item":f"{SITE}{p}"} for i,(n,p) in enumerate(items)]}
    h = '<nav class="crumbs" aria-label="Breadcrumb">' + ' <span aria-hidden="true">/</span> '.join(
        f'<a href="{p}">{esc(n)}</a>' if i < len(items)-1 else f'<span>{esc(n)}</span>' for i,(n,p) in enumerate(items)) + '</nav>'
    return h, ld

def faq_block(faqs):
    ld = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}
    h = '<div class="faq">' + "".join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q,a in faqs) + '</div>'
    return h, ld

def prose(sections):
    out = []
    for s in sections:
        if s[0] == "h2": out.append(f'<h2>{esc(s[1])}</h2>')
        elif s[0] == "h3": out.append(f'<h3>{esc(s[1])}</h3>')
        elif s[0] == "p": out.append(f'<p>{s[1]}</p>')
        elif s[0] == "ul": out.append('<ul>' + "".join(f'<li>{x}</li>' for x in s[1]) + '</ul>')
        elif s[0] == "ol": out.append('<ol>' + "".join(f'<li>{x}</li>' for x in s[1]) + '</ol>')
        elif s[0] == "callout": out.append(f'<p class="callout">{s[1]}</p>')
    return "\n".join(out)

def role_side(current):
    items = "".join(f'<li class="{"now" if r["slug"]==current else ""}"><a href="/hire/{r["slug"]}/">{esc(r["nav"])}</a></li>' for r in ROLES)
    return f'''<aside class="side">
  <div class="card">
    <p class="eyebrow">Hiring this seat?</p>
    <h3>Book a 30 minute intake call</h3>
    <p>Weekdays 4 to 7pm ET on Google Meet. Bring the job description and target comp if you have them.</p>
    <a class="btn btn-primary" href="{BOOK}" target="_blank" rel="noopener">Grab a time</a>
    <p>Or email <a class="inline" href="mailto:sam@technicalrecruiters.biz">sam@technicalrecruiters.biz</a></p>
  </div>
  <div class="card">
    <p class="eyebrow">Roles we fill</p>
    <ul>{items}</ul>
  </div>
</aside>'''

def write(path, body):
    full = os.path.join(".", path.strip("/"), "index.html") if path != "/" else "index.html"
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(body)
    print("wrote", full)

def build_role(r):
    path = f"/hire/{r['slug']}/"
    c_html, c_ld = crumbs([("Home","/"),("Hire",f"/hire/"),(r["nav"],path)])
    f_html, f_ld = faq_block(r["faq"])
    article_ld = {"@context":"https://schema.org","@type":"Article","headline":r["h1_plain"],
        "description":r["desc"],"datePublished":"2026-10-06","dateModified":TODAY,
        "author":{"@type":"Person","name":"Sam Kwak","url":f"{SITE}/about/"},
        "publisher":{"@type":"Organization","name":"Technical Recruiters LLC","url":SITE,"logo":{"@type":"ImageObject","url":f"{SITE}/og-image.png"}},
        "mainEntityOfPage":f"{SITE}{path}"}
    service_ld = {"@context":"https://schema.org","@type":"Service","serviceType":r["service"],
        "provider":{"@type":"EmploymentAgency","name":"Technical Recruiters LLC","url":SITE},
        "areaServed":["San Francisco","New York","Seattle","Los Angeles","Austin"],"url":f"{SITE}{path}"}
    body = head(r["title"], r["desc"], path, [article_ld, service_ld, f_ld, c_ld])
    body += f'''
<div class="wrap page-hero">
  {c_html}
  <p class="eyebrow">{esc(r["eyebrow"])}</p>
  <h1>{r["h1"]}</h1>
  <p class="lede">{r["lede"]}</p>
  <div class="ctas" style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn btn-primary" href="{BOOK}" target="_blank" rel="noopener">Book an intake call</a><a class="btn btn-ghost" href="/#company-form">Send the role</a></div>
</div>
<section style="padding-top:0"><div class="wrap article">
  <article class="prose">
    {prose(r["body"])}
    <h2>Common questions</h2>
    {f_html}
    <p style="margin-top:24px;font-size:14px">Written by <a class="inline" href="/about/">Sam Kwak</a>, founder of Technical Recruiters. Last updated {TODAY}.</p>
  </article>
  {role_side(r["slug"])}
</div></section>
<section style="padding-top:0"><div class="wrap"><div class="cta-band">
  <div><h2>Need this seat filled?</h2><p>Tell us about the role and we will come back with a straight read on the market and a short list of people worth your time.</p></div>
  <a class="btn" href="/#company-form">Tell us about the role</a>
</div></div></section>
''' + FOOT
    write(path, body)

def build_hire_index():
    path = "/hire/"
    c_html, c_ld = crumbs([("Home","/"),("Hire",path)])
    cards = "".join(f'''<a class="path" href="/hire/{r["slug"]}/" style="text-decoration:none">
      <p class="eyebrow">{esc(r["eyebrow"])}</p><h3>{esc(r["nav"])}</h3><p style="color:var(--muted)">{esc(r["card"])}</p>
      <span class="inline" style="color:var(--accent);font-weight:600">Read the hiring guide</span></a>''' for r in ROLES)
    ld = {"@context":"https://schema.org","@type":"CollectionPage","name":"Hire with Technical Recruiters","url":f"{SITE}{path}",
          "hasPart":[{"@type":"WebPage","name":r["nav"],"url":f"{SITE}/hire/{r['slug']}/"} for r in ROLES]}
    body = head("Hire BizOps, Chief of Staff, Forward Deployed and GTM Talent | Technical Recruiters",
                "Hiring guides and recruiting for the seats AI startups struggle to fill: BizOps, Chief of Staff, forward deployed, implementation, GTM and engineering.", path, [ld, c_ld], "website")
    body += f'''
<div class="wrap page-hero">{c_html}<p class="eyebrow">For companies</p><h1>Hire the seats AI startups <em>struggle to fill.</em></h1>
<p class="lede">Each guide below covers what the role really is at a seed to Series C startup, what strong candidates look like on paper and in interviews, the mistakes that cost founders months, and how we run the search.</p>
<div style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn btn-primary" href="{BOOK}" target="_blank" rel="noopener">Book an intake call</a><a class="btn btn-ghost" href="/placements/">See placements</a></div></div>
<section style="padding-top:0"><div class="wrap grid3">{cards}</div></section>
''' + FOOT
    write(path, body)

def build_about():
    path = "/about/"
    c_html, c_ld = crumbs([("Home","/"),("About",path)])
    person = {"@context":"https://schema.org","@type":"Person","name":"Sam Kwak","jobTitle":"Founder and Recruiter",
              "worksFor":{"@type":"Organization","name":"Technical Recruiters LLC","url":SITE},"url":f"{SITE}/about/",
              "email":"sam@technicalrecruiters.biz","sameAs":["https://www.linkedin.com/in/samuelkwak/"]}
    org = {"@context":"https://schema.org","@type":"EmploymentAgency","name":"Technical Recruiters LLC","url":SITE,
           "founder":{"@type":"Person","name":"Sam Kwak"},"email":"sam@technicalrecruiters.biz",
           "sameAs":["https://www.linkedin.com/company/ustechnical-recruiters/"]}
    body = head(ABOUT["title"], ABOUT["desc"], path, [person, org, c_ld], "profile")
    body += f'''
<div class="wrap page-hero">{c_html}<p class="eyebrow">About</p><h1>{ABOUT["h1"]}</h1><p class="lede">{ABOUT["lede"]}</p></div>
<section style="padding-top:0"><div class="wrap article">
  <article class="prose">
    <div class="people"><div class="avatar" aria-hidden="true">SK</div><div style="display:grid;gap:12px">{prose(ABOUT["intro"])}</div></div>
    {prose(ABOUT["body"])}
  </article>
  <aside class="side"><div class="card"><p class="eyebrow">Work with Sam</p><h3>Companies</h3><p>30 minute intake call, weekdays 4 to 7pm ET.</p><a class="btn btn-primary" href="{BOOK}" target="_blank" rel="noopener">Grab a time</a><h3 style="margin-top:8px">Candidates</h3><p>Share your background and we will reply if there is a fit. Always free.</p><a class="btn btn-ghost" href="/#candidate-form">Share your background</a></div>
  <div class="card"><p class="eyebrow">Elsewhere</p><ul><li><a href="https://www.linkedin.com/in/samuelkwak/" target="_blank" rel="noopener">Sam on LinkedIn</a></li><li><a href="https://www.linkedin.com/company/ustechnical-recruiters/" target="_blank" rel="noopener">Technical Recruiters on LinkedIn</a></li><li><a href="mailto:sam@technicalrecruiters.biz">sam@technicalrecruiters.biz</a></li></ul></div></aside>
</div></section>
''' + FOOT
    write(path, body)

def time_html(p):
    return '<p class="time">'+esc(p["time"])+'</p>' if p.get("time") else ""

def build_placements():
    path = "/placements/"
    c_html, c_ld = crumbs([("Home","/"),("Placements",path)])
    data = json.load(open("placements.json"))
    stats = data["stats"]; items = data["placements"]
    stat_html = "".join(f'<div><b>{esc(str(s["value"]))}</b><span>{esc(s["label"])}</span></div>' for s in stats)
    cards = "".join(f'''<div class="placement"><div class="meta">{"".join("<span>"+esc(x)+"</span>" for x in [p.get("company",""),p["stage"],p.get("city",""),p.get("closed","")] if x)}</div>
      <h3>{esc(p["role"])}</h3><p>{esc(p["summary"])}</p>{time_html(p)}</div>''' for p in items)
    ld = {"@context":"https://schema.org","@type":"WebPage","name":"Placements","url":f"{SITE}{path}","description":PLACEMENTS_PAGE["desc"]}
    body = head(PLACEMENTS_PAGE["title"], PLACEMENTS_PAGE["desc"], path, [ld, c_ld], "website")
    body += f'''
<div class="wrap page-hero">{c_html}<p class="eyebrow">Proof</p><h1>{PLACEMENTS_PAGE["h1"]}</h1><p class="lede">{PLACEMENTS_PAGE["lede"]}</p></div>
<section style="padding-top:0"><div class="wrap" style="display:grid;gap:40px">
  <div class="stat-row">{stat_html}</div>
  <figure class="proof" style="margin:0"><div class="stat">24<small>Days to offer letter</small></div><div><blockquote>"Helped us hire strong talent with a few submissions and we ended up sending an offer letter in 24 days."</blockquote><cite>Hiring team, Series B YC-backed startup</cite></div></figure>
  <div><div class="sec-head"><p class="eyebrow">Record</p><h2>Recent placements</h2><p class="lede">Candidate names are never published. Company names appear only with the client's permission.</p></div>
  <div class="placements">{cards}</div></div>
  <div class="cta-band"><div><h2>Want your seat on this page?</h2><p>Book a 30 minute intake call and we will tell you plainly whether this is a search we can win for you.</p></div><a class="btn" href="{BOOK}" target="_blank" rel="noopener">Grab a time</a></div>
</div></section>
''' + FOOT
    write(path, body)

def build_sitemap():
    urls = ["/", "/hire/", "/placements/", "/about/"] + [f"/hire/{r['slug']}/" for r in ROLES]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        pri = "1.0" if u == "/" else ("0.9" if u.startswith("/hire/") and u != "/hire/" else "0.8")
        xml += f'  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>{pri}</priority></url>\n'
    xml += '</urlset>\n'
    open("sitemap.xml","w").write(xml); print("wrote sitemap.xml", len(urls), "urls")

if __name__ == "__main__":
    for r in ROLES: build_role(r)
    build_hire_index(); build_about(); build_placements(); build_sitemap()
