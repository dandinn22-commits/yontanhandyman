#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""בונה את כל האתר מ-tools/config.py, tools/cities.py ו-tools/guides.py.
מריצים מתיקיית האתר: python3 tools/build.py
לא עורכים ישירות את קובצי ה-HTML. הם נוצרים מחדש בכל בנייה."""
import hashlib, html, json, os, re, sys
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import config as C
from cities import CITIES
from cities_extra import EXTRA
from guides import GUIDES
from landing import LANDINGS

D = C.DOMAIN
BIZ_ID = D + '/#business'
TEL = 'tel:' + C.PHONE_INTL
WA_NUM = C.PHONE_INTL.lstrip('+')
FONT = 'https://fonts.googleapis.com/css2?family=Assistant:wght@400;600;700;800&family=Secular+One&display=swap'
HAS_ART = all(os.path.exists(os.path.join(ROOT, 'img/art/%s.webp' % n)) for n in ('kit', 'screwdriver', 'drill'))
PRICE = {k: '%d ₪' % p for k, _, p, _ in C.PRICES}
GUIDE = {g['slug']: g for g in GUIDES}
CITY = {c['slug']: c for c in CITIES}

ICON_PHONE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1l-2.3 2.2z"/></svg>'
ICON_WA = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm5.3 14.2c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .2-3.3-.7a11.6 11.6 0 0 1-4.5-4c-.4-.5-1-1.5-1-2.5s.6-1.6.8-1.8c.2-.3.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 2c.1.2.1.4 0 .5l-.3.5-.4.4c-.1.2-.3.3-.1.6.2.3.8 1.3 1.6 2 1.1 1 2 1.3 2.3 1.4.3.2.5.1.6-.1l.9-1.1c.2-.3.4-.2.7-.1l1.9.9c.3.1.5.2.5.3.1.2.1.7-.1 1.3z"/></svg>'

# איורים לכרטיסי השירות. מוצגים כשאין תמונה בתיקיית img
_N, _O = '#06306B', '#F27A1C'
_S = 'fill="none" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"'
ART = {
 'shelves': f'<g {_S} stroke="{_N}"><path d="M28 34h64M28 62h64"/><path d="M36 34v6M84 34v6M36 62v6M84 62v6" stroke="{_O}"/><path d="M42 34V20h8v14M54 34V16h7v18M72 62V48h12v14"/></g>',
 'tv': f'<g {_S} stroke="{_N}"><rect x="26" y="16" width="68" height="42" rx="3"/><path d="M60 58v8" stroke="{_O}"/><path d="M46 72h28" stroke="{_O}"/></g>',
 'furniture': f'<g {_S} stroke="{_N}"><rect x="34" y="14" width="52" height="60" rx="2"/><path d="M60 14v60M34 74v4M86 74v4"/><path d="M53 42v6M67 42v6" stroke="{_O}"/></g>',
 'doors': f'<g {_S} stroke="{_N}"><path d="M38 78V14h44v64M28 78h64"/><path d="M72 44h-8" stroke="{_O}"/><circle cx="72" cy="44" r="3" stroke="{_O}"/></g>',
 'curtains': f'<g {_S} stroke="{_N}"><path d="M22 16h76"/><path d="M28 16c0 22 4 42 12 60M46 16c0 22-2 42-6 60M92 16c0 22-4 42-12 60M74 16c0 22 2 42 6 60"/><circle cx="22" cy="16" r="2.5" stroke="{_O}"/><circle cx="98" cy="16" r="2.5" stroke="{_O}"/></g>',
 'walls': f'<g {_S} stroke="{_N}"><path d="M24 22h72M24 44h72M24 66h72M46 22v22M74 22v22M34 44v22M62 44v22M86 44v22"/><path d="M58 72l24-24 8 8-24 24H58z" stroke="{_O}" fill="#E9EEF7"/></g>',
 'bathroom': f'<g {_S} stroke="{_N}"><ellipse cx="60" cy="34" rx="20" ry="22"/><path d="M34 70h52M42 70v8M78 70v8"/><path d="M54 26l10 10" stroke="{_O}"/></g>',
 'moving': f'<g {_S} stroke="{_N}"><path d="M26 38l34-14 34 14v32l-34 12-34-12z"/><path d="M26 38l34 12 34-12M60 50v32"/><path d="M42 31l34 13" stroke="{_O}"/></g>',
}


def esc(s):
    return html.escape(s, quote=True)


def fill(t):
    def rep(m):
        k = m.group(1)
        if k == 'PRICE_TABLE':
            return price_table()
        return PRICE[k]
    return re.sub(r'\{\{(\w+)\}\}', rep, t)


def plain(t):
    return html.unescape(re.sub(r'<[^>]+>', '', fill(t)))


def hours(t):
    return re.sub(r'(\d\d:\d\d–\d\d:\d\d)', r'<span class="hrs">\1</span>', t)


def wa_link(text='היי יונתן, אני צריך הנדימן'):
    return 'https://wa.me/%s?text=%s' % (WA_NUM, quote(text))


def write(rel, text):
    path = os.path.join(ROOT, rel)
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def ld(obj):
    return '<script type="application/ld+json">%s</script>' % json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def graph(*nodes):
    return ld({'@context': 'https://schema.org', '@graph': list(nodes)})


def business(full=False):
    b = {'@type': 'HomeAndConstructionBusiness', '@id': BIZ_ID, 'name': C.BRAND,
         'alternateName': ['Yonatan Handyman', 'יונתן ההנדימן'],
         'description': 'הנדימן לבית ולמשרד במרכז ובשרון: תליית מדפים וטלוויזיות, הרכבת רהיטים, תיקוני דלתות ותיקונים קטנים, במחיר סגור מראש.',
         'url': D + '/', 'telephone': '+972-54-456-0552', 'email': C.EMAIL,
         'logo': D + '/logo.png', 'image': D + '/og-image.jpg', 'priceRange': '₪₪', 'currenciesAccepted': 'ILS',
         'address': {'@type': 'PostalAddress', 'addressRegion': 'המרכז והשרון', 'addressCountry': 'IL'},
         'openingHoursSpecification': [
             {'@type': 'OpeningHoursSpecification', 'dayOfWeek': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday'], 'opens': '08:00', 'closes': '19:00'},
             {'@type': 'OpeningHoursSpecification', 'dayOfWeek': 'Friday', 'opens': '08:00', 'closes': '13:00'}],
         'areaServed': [{'@type': 'City', 'name': c['name'], 'url': '%s/%s/' % (D, c['slug'])} for c in CITIES]}
    if C.SAME_AS:
        b['sameAs'] = C.SAME_AS
    if C.RATING and C.RATING_COUNT:
        b['aggregateRating'] = {'@type': 'AggregateRating', 'ratingValue': C.RATING, 'reviewCount': C.RATING_COUNT, 'bestRating': '5'}
    if full:
        b['founder'] = {'@type': 'Person', 'name': 'יונתן', 'jobTitle': 'הנדימן'}
        b['contactPoint'] = {'@type': 'ContactPoint', 'telephone': '+972-54-456-0552', 'email': C.EMAIL, 'contactType': 'customer service', 'availableLanguage': ['he']}
        b['hasOfferCatalog'] = {'@type': 'OfferCatalog', 'name': 'שירותי הנדימן', 'itemListElement':
            [{'@type': 'Offer', 'itemOffered': {'@type': 'Service', 'name': s[1], 'description': s[2]}} for s in C.SERVICES] +
            [{'@type': 'Offer', 'itemOffered': {'@type': 'Service', 'name': n},
              'priceSpecification': {'@type': 'PriceSpecification', 'minPrice': p, 'priceCurrency': 'ILS', 'valueAddedTaxIncluded': True}} for _, n, p, _ in C.PRICES]}
    return b


def website():
    return {'@type': 'WebSite', '@id': D + '/#website', 'url': D + '/', 'name': C.BRAND, 'inLanguage': 'he-IL', 'publisher': {'@id': BIZ_ID}}


def webpage(path, title, desc, speak=None):
    p = {'@type': 'WebPage', '@id': D + path + '#webpage', 'url': D + path, 'name': title, 'description': desc, 'inLanguage': 'he-IL',
         'isPartOf': {'@id': D + '/#website'}, 'about': {'@id': BIZ_ID}, 'dateModified': C.LAST_UPDATED}
    if speak:
        p['speakable'] = {'@type': 'SpeakableSpecification', 'cssSelector': speak}
    return p


def faq_node(items, path):
    return {'@type': 'FAQPage', '@id': D + path + '#faq', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in items]}


def crumbs_node(items):
    return {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': D + u} for i, (n, u) in enumerate(items)]}


def css_version():
    with open(os.path.join(ROOT, 'assets/site.css'), 'rb') as f:
        a = f.read()
    with open(os.path.join(ROOT, 'assets/site.js'), 'rb') as f:
        a += f.read()
    return hashlib.md5(a).hexdigest()[:8]


def head(title, desc, path, extra='', robots='index, follow, max-image-preview:large, max-snippet:-1', og='website'):
    url = D + path
    site = {'leadEmail': C.LEAD_EMAIL, 'leadCc': C.LEAD_CC, 'sheet': C.SHEET_ENDPOINT, 'ads': C.ADS_ID, 'ga4': C.GA4_ID,
            'labels': C.ADS_LABELS, 'phone': C.PHONE, 'tel': C.PHONE_INTL, 'wa': WA_NUM}
    gtm = ""
    if getattr(C, 'GTM_ID', ''):
        gtm = ("<!-- Google Tag Manager -->\n<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':\n"
               "new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],\n"
               "j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=\n"
               "'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);\n"
               "})(window,document,'script','dataLayer','%s');</script>\n<!-- End Google Tag Manager -->\n") % C.GTM_ID
    gid = C.ADS_ID or C.GA4_ID
    gtag = '<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>\n' % gid if gid else ''
    v = css_version()
    t, d = esc(title), esc(desc)
    return f'''<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
{gtm}<script>window.SITE={json.dumps(site, ensure_ascii=False)};</script>
{gtag}<script src="/assets/tracking.js?v={v}"></script>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{t}</title>
<meta name="description" content="{d}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="he-IL" href="{url}">
<meta name="theme-color" content="#F1F6FA">
<meta name="geo.region" content="IL">
<meta name="geo.placename" content="המרכז והשרון">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="{og}">
<meta property="og:locale" content="he_IL">
<meta property="og:site_name" content="{C.BRAND}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{D}/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="הלוגו של {C.BRAND}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{D}/og-image.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONT}">
<link rel="stylesheet" href="/assets/site.css?v={v}">
{extra}
</head>'''


def gtm_body():
    if not getattr(C, 'GTM_ID', ''):
        return ''
    return ('<!-- Google Tag Manager (noscript) -->\n<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=%s" '
            'height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>\n<!-- End Google Tag Manager (noscript) -->\n') % C.GTM_ID


def header():
    return f'''<header class="top" id="top">
  <div class="wrap top-in">
    <a class="brand" href="/" aria-label="{C.BRAND} – לעמוד הבית">
      <img src="/logo.webp" alt="לוגו {C.BRAND} – מברג כתום וכחול" width="113" height="48" fetchpriority="high">
    </a>
    <nav class="nav" aria-label="ניווט ראשי">
      <a href="/#services">שירותים</a>
      <a href="/#prices">מחירון</a>
      <a href="/#gallery">עבודות</a>
      <a href="/#areas">אזורי שירות</a>
      <a href="/guides/">מדריכים</a>
      <a href="/#faq">שאלות נפוצות</a>
      <a href="/#contact">צור קשר</a>
    </nav>
    <a class="btn btn-call top-call" data-cta="call-top" href="{TEL}" aria-label="התקשרו ל{C.BRAND} {C.PHONE}">{ICON_PHONE}<span class="num">{C.PHONE}</span></a>
  </div>
</header>'''


def footer():
    cities = ''.join('<li><a href="/%s/">הנדימן %s</a></li>' % (c['slug'], c['in']) for c in CITIES)
    guides = ''.join('<li><a href="/guides/%s/">%s</a></li>' % (g['slug'], g['short']) for g in GUIDES)
    return f'''<footer class="foot">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <strong>{C.BRAND}</strong>הנדימן במרכז ובשרון<br>
        טלפון: <a class="num" data-cta="call-footer" href="{TEL}">{C.PHONE}</a><br>
        מייל: <a class="mail" href="mailto:{C.EMAIL}">{C.EMAIL}</a><br>
        {hours(C.HOURS_HE)}
      </div>
      <nav aria-label="אזורי שירות"><strong>אזורי שירות</strong><ul class="foot-cities">{cities}</ul></nav>
      <nav aria-label="מדריכים"><strong>מדריכים</strong><ul>{guides}<li><a href="/guides/">כל המדריכים</a></li></ul></nav>
      <nav aria-label="מידע"><strong>שירותים</strong><ul>{''.join('<li><a href="/%s/">%s</a></li>' % (l['slug'], l['card']) for l in LANDINGS)}</ul><strong style="margin-top:14px">מידע</strong><ul><li><a href="/accessibility.html">הצהרת נגישות</a></li><li><a href="/privacy.html">מדיניות פרטיות</a></li></ul></nav>
    </div>
    <p class="foot-copy">© 2026 {C.BRAND} · עודכן לאחרונה: <time datetime="{C.LAST_UPDATED}">{C.LAST_UPDATED_HE}</time></p>
  </div>
</footer>'''


def float_bits(wa_text=None):
    wa = wa_link(wa_text) if wa_text else wa_link()
    return f'''<a class="float-wa" data-cta="wa-float" href="{wa}" target="_blank" rel="noopener" aria-label="שליחת הודעת וואטסאפ ל{C.BRAND}">{ICON_WA}</a>
<div class="mbar">
  <a class="mbar-call" data-cta="call-sticky" href="{TEL}">{ICON_PHONE}חייגו עכשיו</a>
  <a class="mbar-wa" data-cta="wa-sticky" href="{wa}" target="_blank" rel="noopener">{ICON_WA}וואטסאפ</a>
</div>
<button type="button" class="access-toggle" id="accessToggle" aria-label="תפריט נגישות" aria-expanded="false" aria-controls="accessPanel">
<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="10.5" stroke="currentColor" stroke-width="1.6"/><circle cx="12" cy="7.3" r="1.4" fill="currentColor"/><path d="M6.5 9.8c3.6 1.1 7.4 1.1 11 0M12 9.8V14l-2.3 5.4M12 14l2.3 5.4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
</button>
<div class="access-panel" id="accessPanel">
<p>אפשרויות נגישות</p>
<button type="button" data-action="font-up">הגדלת תצוגה</button>
<button type="button" data-action="font-down">הקטנת תצוגה</button>
<button type="button" data-action="contrast">ניגודיות גבוהה</button>
<button type="button" data-action="links">הדגשת קישורים</button>
<button type="button" data-action="reset">איפוס</button>
<a href="/accessibility.html">הצהרת נגישות</a>
</div>'''


def page(title, desc, path, content, extra='', robots=None, og='website', wa_text=None, art=False, bg=False):
    kw = {'robots': robots} if robots else {}
    scripts = '<script src="/assets/site.js?v=%s"></script>' % css_version()
    tools = ''
    if bg and HAS_ART:
        tools = '<div class="tools-bg" id="tools-bg" aria-hidden="true"></div>\n'
        scripts += '\n<script src="/assets/tools-bg.js?v=%s"></script>' % css_version()
    return head(title, desc, path, extra, og=og, **kw) + f'''
<body>
{gtm_body()}<div class="page">
{tools}<a class="skip" href="#main">דילוג לתוכן הראשי</a>
{header()}
<main id="main">
{content}
</main>
{footer()}
</div>
{float_bits(wa_text)}
{scripts}
<script src="/lead-alerts.js?v=1" data-brand="יונתן הנדימן" defer></script>
</body>
</html>
'''


def ticket(fid, source, city='', job='', sub='השאירו שם וטלפון, ויונתן יחזור אליכם עם מחיר.', title='קבלו מחיר לעבודה', hid='', page_id=False):
    ph = '' if job else ' selected'
    jobs = '<option value=""%s>בחרו סוג עבודה</option>' % ph + ''.join('<option%s>%s</option>' % (' selected' if o == job else '', o) for o in C.JOB_OPTIONS)
    city_in = '<input type="hidden" name="city" value="%s">' % esc(city) if city else ''
    t_id = fid + '-title'
    return f'''<form class="ticket lead-form" id="{fid}" data-source="{source}" aria-labelledby="{t_id}" novalidate>
  <div class="ticket-head">
    <h2 id="{t_id}" class="ticket-title">{title}</h2>
    <span class="ticket-no">חוזרים אליכם עם מחיר</span>
  </div>
  <p class="ticket-sub">{sub}</p>
  <label for="{fid}-name">שם</label>
  <input id="{fid}-name" name="name" type="text" placeholder="השם שלכם" autocomplete="given-name" maxlength="60" required aria-describedby="{fid}-e-name">
  <span class="err field-err err-name" id="{fid}-e-name" hidden>נא למלא שם</span>
  <label for="{fid}-phone">טלפון</label>
  <input id="{fid}-phone" name="phone" type="tel" inputmode="tel" placeholder="050-0000000" autocomplete="tel" maxlength="20" required aria-describedby="{fid}-e-phone" dir="ltr">
  <span class="err field-err err-phone" id="{fid}-e-phone" hidden>נא למלא מספר טלפון תקין, לדוגמה 050-1234567</span>
  <label for="{fid}-job">סוג העבודה <span class="opt">(לא חובה)</span></label>
  <select id="{fid}-job" name="job">{jobs}</select>
  {city_in}
  <input type="text" name="_honey" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
  <div class="form-error" role="alert" hidden></div>
  <button type="submit" class="btn btn-call wide" data-cta="form-{fid}">שלחו לי מחיר</button>
  <p class="ticket-foot">מעדיפים לדבר? <a href="{TEL}" class="num" data-cta="call-form">{C.PHONE}</a></p>
  <p class="ticket-note">הפרטים משמשים רק כדי לחזור אליכם. <a href="/privacy.html">מדיניות פרטיות</a></p>
</form>'''


def cta_buttons(prefix, wa_text=None, big=True):
    b = ' big' if big else ''
    return f'''<div class="cta-row">
  <a class="btn btn-call{b}" data-cta="call-{prefix}" href="{TEL}">{ICON_PHONE}התקשרו: <span class="num">{C.PHONE}</span></a>
  <a class="btn btn-wa{b}" data-cta="wa-{prefix}" href="{wa_link(wa_text) if wa_text else wa_link()}" target="_blank" rel="noopener">{ICON_WA}הודעה בוואטסאפ</a>
</div>'''


def chips():
    return '''<ul class="chips" aria-label="למה יונתן הנדימן">
  <li>מגיע עם כל הכלים</li><li>מחיר סגור לפני העבודה</li><li>ניקיון בסיום</li><li>כמה עבודות בביקור אחד</li>
</ul>'''


def service_cards(texts=None):
    texts = texts or {}
    out = []
    items = [x for x in C.SERVICES if x[0] in texts] + [x for x in C.SERVICES if x[0] not in texts]
    for key, name, text, alt, job, guide in items:
        text = texts.get(key, text)
        if os.path.exists(os.path.join(ROOT, 'img/%s.webp' % key)):
            art = '<img class="svc-img" src="/img/%s.webp" alt="%s" width="640" height="480" loading="lazy" decoding="async">' % (key, alt)
        else:
            art = '<svg class="svc-art" viewBox="0 0 120 90" aria-hidden="true">%s</svg>' % ART[key]
        g = GUIDE[guide]
        out.append(f'''<article class="svc">
  {art}
  <h3>{next(('<a href="/%s/" style="color:inherit">%s</a>' % (l['slug'], name) for l in LANDINGS if l['svc'] == key and l.get('main')), name)}</h3>
  <p>{text}</p>
  <div class="svc-links"><a href="#quote" data-job="{esc(job)}" data-cta="svc-{key}">קבלו מחיר</a>{''.join('<a href="/%s/">%s</a>' % (l['slug'], l['card']) for l in LANDINGS if l['svc'] == key)}<a href="/guides/{guide}/">{g['short']}</a></div>
</article>''')
    return '<div class="services">%s</div>' % ''.join(out)


def price_table():
    rows = ''.join('<tr><td>%s</td><td class="num">%d ₪</td><td>%s</td></tr>' % (n, p, t) for _, n, p, t in C.PRICES)
    return f'''<div class="table-wrap">
<table class="prices">
<caption>מחירון התחלתי (כולל מע״מ, לא כולל חומרים מיוחדים)</caption>
<thead><tr><th scope="col">עבודה</th><th scope="col">מחיר החל מ־</th><th scope="col">זמן עבודה משוער</th></tr></thead>
<tbody>{rows}</tbody>
</table>
</div>'''


def price_fine():
    return '<p class="fine">המחירים מעודכנים ל<time datetime="2026-11">%s</time>. המחיר הסופי תלוי בסוג הקיר, בגובה העבודה ובכמות. שלחו תמונה בוואטסאפ ותקבלו מחיר מדויק.</p>' % C.PRICES_MONTH_HE


def cta_strip(text, prefix, wa_text=None):
    return f'<div class="cta-strip"><p>{text}</p>{cta_buttons(prefix, wa_text, big=False)}</div>'


def faq_html(items, open_first=True):
    out = []
    for i, (q, a) in enumerate(items):
        o = ' open' if open_first and i == 0 else ''
        out.append('<details%s><summary><h3>%s</h3></summary><p>%s</p></details>' % (o, q, fill(a)))
    return '<div class="faq">%s</div>' % ''.join(out)


def area_lists():
    li = lambda cs: ''.join('<li><a href="/%s/">הנדימן %s</a></li>' % (c['slug'], c['in']) for c in cs)
    return f'''<h3 class="areas-h">ערים עיקריות</h3>
<ul class="areas areas-main">{li([c for c in CITIES if c['main']])}</ul>
<h3 class="areas-h">ערים נוספות</h3>
<ul class="areas">{li([c for c in CITIES if not c['main']])}</ul>'''


def guide_cards(items=None):
    out = ''.join(f'''<a class="guide-card" href="/guides/{g['slug']}/"><h3>{g['short']}</h3><p>{g['desc']}</p><span>לקריאת המדריך ←</span></a>''' for g in (items or GUIDES))
    return '<div class="guide-cards">%s</div>' % out


def quote_band(title, text, source, city='', job='', wa_text=None, section_id='quote', head_id='qb-h'):
    return f'''<section class="quote-band" id="contact" aria-labelledby="{head_id}">
  <div class="wrap"><div class="quote-in">
    <div class="quote-copy">
      <h2 id="{head_id}">{title}</h2>
      <p>{text}</p>
      {cta_buttons('band', wa_text)}
      <p>אפשר גם במייל: <a class="mail mail-link" href="mailto:{C.EMAIL}">{C.EMAIL}</a></p>
    </div>
    {ticket(section_id, source, city, job, sub='השאירו שם וטלפון, ויונתן יחזור אליכם עם מחיר ומועד.', title='קבלו מחיר לעבודה')}
  </div></div>
</section>'''


def gallery_section():
    items = getattr(C, 'GALLERY', [])
    if not items:
        return ''
    cards = ''.join('<figure class="gal-item"><img src="/img/gallery/%s" alt="%s" width="900" height="1200" loading="lazy" decoding="async"><figcaption>%s</figcaption></figure>' % (f, alt, cap) for f, cap, alt in items)
    return f'''<section class="section alt" id="gallery" aria-labelledby="gallery-h">
  <div class="wrap">
    <h2 id="gallery-h">גלריית עבודות</h2>
    <p class="section-lead">כמה מהעבודות שיונתן ביצע לאחרונה אצל לקוחות.</p>
    <div class="gallery">{cards}</div>
    {cta_strip('רוצים שגם אצלכם זה ייראה ככה?', 'gallery')}
  </div>
</section>
'''


def reviews_section():
    if not C.REVIEWS:
        return ''
    items = ''.join('<figure class="review"><blockquote style="margin:0">%s</blockquote><figcaption>%s · %s · %s</figcaption></figure>' % (r['quote'], r['name'], r['place'], r['job']) for r in C.REVIEWS)
    rate = '<p class="section-lead">דירוג %s בגוגל, מתוך %s ביקורות.</p>' % (C.RATING, C.RATING_COUNT) if C.RATING and C.RATING_COUNT else ''
    return f'<section class="section" id="reviews" aria-labelledby="reviews-h"><div class="wrap"><h2 id="reviews-h">מה לקוחות אומרים</h2>{rate}<div class="review-grid">{items}</div></div></section>'


def build_home():
    title = '%s | הנדימן במרכז ובשרון – תלייה, הרכבה ותיקונים' % C.BRAND
    desc = '%s: תליית מדפים וטלוויזיות, הרכבת רהיטים ותיקוני דלתות במרכז ובשרון. מגיע עם כל הכלים, מחיר סגור מראש. התקשרו %s.' % (C.BRAND, C.PHONE)
    years = ' עם %s שנות ניסיון' % C.YEARS if C.YEARS else ''
    content = f'''<section class="hero" aria-labelledby="h1">
  <div class="wrap hero-in">
    <div class="hero-copy">
      <p class="eyebrow">הנדימן במרכז ובשרון · תיקונים, תלייה והרכבה</p>
      <h1 id="h1">{C.BRAND} – כל העבודות הקטנות בבית, בביקור אחד</h1>
      <p class="lead speak-lead">{C.BRAND} הוא הנדימן לבית ולמשרד במרכז ובשרון. במקום לחפש בעל מקצוע נפרד לכל עבודה, אתם מכינים רשימה ויונתן מגיע עם כל הכלים: תליית מדפים ותמונות, התקנת טלוויזיה על הקיר, הרכבת רהיטים, תיקון דלתות ותיקונים קטנים. המחיר נסגר מראש, לפני שמתחילים.</p>
      {cta_buttons('hero')}
      {chips()}
    </div>
    {ticket('hero-form', 'טופס עליון')}
  </div>
</section>

<section class="band" id="what" aria-labelledby="what-h">
  <div class="wrap narrow"><div class="panel panel-navy">
    <h2 id="what-h">מה עושה הנדימן?</h2>
    <p class="answer">הנדימן הוא בעל מקצוע כללי לתיקונים ועבודות קטנות בבית: תלייה, הרכבה, התקנה ותיקון. ההבדל מבעל מקצוע מתמחה הוא שהנדימן מטפל בכמה עבודות שונות באותו ביקור. כך אפשר לסגור רשימה שלמה של משימות עם אדם אחד, תיאום אחד ומחיר אחד. <a style="color:#fff" href="/guides/handyman-or-licensed-pro/">למי לקרוא לאיזו עבודה?</a></p>
  </div></div>
</section>

<section class="section" id="services" aria-labelledby="services-h">
  <div class="wrap">
    <h2 id="services-h">שירותי הנדימן של יונתן</h2>
    <p class="section-lead">אלה העבודות שיונתן מבצע הכי הרבה. לא מצאתם את שלכם? שלחו הודעה ותקבלו תשובה.</p>
    {service_cards()}
  </div>
</section>

<section class="section alt" id="prices" aria-labelledby="prices-h">
  <div class="wrap">
    <h2 id="prices-h">כמה עולה הנדימן?</h2>
    <p class="answer narrow-text">מחיר הנדימן נקבע לפי סוג העבודה, סוג הקיר וכמות העבודות בביקור. אצל {C.BRAND} מחיר ביקור עם עבודה קטנה מתחיל ב־{PRICE['small']}, וכמה עבודות באותו ביקור יוצאות זולות יותר מהזמנה נפרדת לכל אחת. המחיר הסופי נסגר איתכם לפני שמתחילים. <a href="/guides/how-much-handyman/">המדריך המלא למחירים</a></p>
    {price_table()}
    {price_fine()}
    {cta_strip('רוצים מחיר סגור לרשימה שלכם?', 'prices')}
  </div>
</section>
{reviews_section()}
{gallery_section()}<section class="section" id="areas" aria-labelledby="areas-h">
  <div class="wrap">
    <h2 id="areas-h">באילו ערים {C.BRAND} עובד?</h2>
    <p class="answer narrow-text">{C.BRAND} נותן שירות בערי המרכז והשרון. הנה הערים העיקריות. גרים ביישוב סמוך? שלחו הודעה ובדרך כלל זה מסתדר.</p>
    {area_lists()}
  </div>
</section>

<section class="section alt" id="about" aria-labelledby="about-h">
  <div class="wrap about">
    <div class="about-copy">
      <h2 id="about-h">מי זה יונתן?</h2>
      <p>יונתן הוא ההנדימן שמאחורי העסק{years}, והוא זה שמגיע אליכם הביתה. אין מוקד ואין קבלני משנה: מי שעונה לטלפון הוא מי שמבצע את העבודה ואחראי עליה.</p>
      <p>העבודה של יונתן בנויה על שלושה כללים פשוטים: לבדוק את הקיר לפני שקודחים, לסגור מחיר לפני שמתחילים, ולהשאיר את הבית נקי כמו שהיה.</p>
      <p>יונתן לא מבצע עבודות שדורשות רישיון חשמלאי או אינסטלטור מוסמך. במקרים כאלה הוא יגיד לכם את זה מראש.</p>
    </div>
    <dl class="facts">
      <div><dt>שם העסק</dt><dd>{C.BRAND}</dd></div>
      <div><dt>טלפון</dt><dd><a class="num" data-cta="call-facts" href="{TEL}">{C.PHONE}</a></dd></div>
      <div><dt>מייל</dt><dd><a class="mail" href="mailto:{C.EMAIL}">{C.EMAIL}</a></dd></div>
      <div><dt>אזור שירות</dt><dd>המרכז והשרון</dd></div>
      <div><dt>שעות פעילות</dt><dd>{hours('א׳–ה׳ 08:00–19:00')}<br>{hours('ו׳ 08:00–13:00')}</dd></div>
    </dl>
  </div>
</section>

<section class="section" id="how" aria-labelledby="how-h">
  <div class="wrap">
    <h2 id="how-h">איך מזמינים הנדימן?</h2>
    <p class="section-lead">ארבעה שלבים, מהרשימה ועד שהכל תלוי ועובד.</p>
    <ol class="steps">
      <li><h3>שולחים רשימה ותמונות</h3><p>כתבו בוואטסאפ מה צריך לעשות, וצרפו תמונה של הקיר או של הרהיט. ככה מקבלים מחיר בלי ביקור מקדים.</p></li>
      <li><h3>סוגרים מחיר ומועד</h3><p>יונתן חוזר עם מחיר לכל הרשימה ומציע מועד הגעה. אין הפתעות בסוף.</p></li>
      <li><h3>יונתן מגיע עם הכלים</h3><p>מקדחה, פלס לייזר, דיבלים וברגים לכל סוגי הקירות. אתם רק מראים איפה.</p></li>
      <li><h3>בודקים יחד ומנקים</h3><p>בסוף העבודה עוברים יחד על הרשימה, ויונתן שואב את האבק מהקידוחים לפני שהוא יוצא.</p></li>
    </ol>
    {cta_strip('הרשימה מוכנה? שלחו אותה עכשיו.', 'how')}
  </div>
</section>

<section class="section alt" id="guides" aria-labelledby="guides-h">
  <div class="wrap">
    <h2 id="guides-h">מדריכים לפני שמזמינים</h2>
    <p class="section-lead">תשובות קצרות וברורות לשאלות שעולות לפני עבודה בבית.</p>
    {guide_cards(GUIDES[:4])}
    <p><a href="/guides/" style="font-weight:700">לכל המדריכים ←</a></p>
  </div>
</section>

<section class="section" id="faq" aria-labelledby="faq-h">
  <div class="wrap narrow">
    <h2 id="faq-h">שאלות נפוצות על הנדימן</h2>
    {faq_html(C.FAQ)}
  </div>
</section>

{quote_band('צריכים הנדימן? דברו עם יונתן', 'התקשרו או שלחו הודעה עם רשימת העבודות ותמונה. תקבלו מחיר ומועד הגעה.', 'טופס תחתון')}'''
    extra = graph(business(full=True), website(), webpage('/', title, desc, ['.speak-lead', '#what .answer', '#prices .answer']), faq_node(C.FAQ, '/'))
    write('index.html', page(title, desc, '/', content, extra, bg=True))


def build_cities():
    general = [C.FAQ[2]]
    for c in CITIES:
        x = EXTRA[c['slug']]
        path = '/%s/' % c['slug']
        title = 'הנדימן %s – תלייה, הרכבה ותיקונים | %s' % (c['in'], C.BRAND)
        desc = c['desc']
        wa_text = 'היי יונתן, אני %s ואני צריך הנדימן' % c['in']
        hoods = '<p class="hoods">מגיעים בין היתר ל: %s, ולשאר חלקי העיר.</p>' % ', '.join(c['hoods']) if c['hoods'] else ''
        local = ''.join('<div class="local-card"><h3>%s</h3><p>%s</p></div>' % x for x in c['local'])
        near = ''.join('<li><a href="/%s/">הנדימן %s</a></li>' % (s, CITY[s]['in']) for s in c['near'])
        faqs = c['faq'] + x['faq'] + general
        about = ''.join('<p>%s</p>' % fill(t) for t in x['about'])
        content = f'''<div class="wrap"><nav class="breadcrumb" aria-label="מיקום באתר"><a href="/">דף הבית</a> / <span>הנדימן {c['in']}</span></nav></div>
<section class="hero city-hero" aria-labelledby="h1">
  <div class="wrap hero-in">
    <div class="hero-copy">
      <p class="eyebrow">{C.BRAND} · {c['name']}</p>
      <h1 id="h1">הנדימן {c['in']}: כל העבודות הקטנות בבית, בביקור אחד</h1>
      <p class="lead speak-lead">{c['lead']}</p>
      {cta_buttons('hero', wa_text)}
      {chips()}
      {hoods}
    </div>
    {ticket('hero-form', 'טופס עליון – ' + c['name'], city=c['name'], sub='השאירו פרטים, ויונתן יחזור אליכם עם מחיר ומועד הגעה ל%s.' % c['name'])}
  </div>
</section>

<section class="section" id="about-city" aria-labelledby="about-city-h">
  <div class="wrap narrow">
    <h2 id="about-city-h">הנדימן {c['in']}: מה חשוב לדעת</h2>
    <div class="city-about">{about}</div>
    <p class="city-tip"><strong>טיפ לתושבי {c['name']}:</strong> {x['tip']}</p>
  </div>
</section>

<section class="section alt" id="local" aria-labelledby="local-h">
  <div class="wrap">
    <h2 id="local-h">{c['local_title']}</h2>
    <div class="local-grid">{local}</div>
    {cta_strip('יש לכם רשימה? שלחו אותה ליונתן.', 'local', wa_text)}
  </div>
</section>

<section class="section" id="services" aria-labelledby="services-h">
  <div class="wrap">
    <h2 id="services-h">שירותי הנדימן {c['in']}</h2>
    {service_cards(x['top'])}
  </div>
</section>

<section class="section alt" id="prices" aria-labelledby="prices-h">
  <div class="wrap">
    <h2 id="prices-h">כמה עולה הנדימן {c['in']}?</h2>
    <p class="answer narrow-text">ביקור עם עבודה קטנה {c['in']} מתחיל ב־{PRICE['small']}, ושעת עבודה לרשימת משימות מתחילה ב־{PRICE['hour']}. כמה עבודות באותו ביקור יוצאות זולות יותר, והמחיר נסגר לפני שמתחילים.</p>
    {price_table()}
    {price_fine()}
  </div>
</section>

<section class="section" id="faq" aria-labelledby="faq-h">
  <div class="wrap narrow">
    <h2 id="faq-h">שאלות נפוצות על הנדימן {c['in']}</h2>
    {faq_html(faqs)}
    <div class="related">
      <p>ערים קרובות</p>
      <ul class="link-list">{near}<li><a href="/#areas">כל אזורי השירות</a></li></ul>
      <p>מדריכים שיעזרו לכם</p>
      <ul class="link-list"><li><a href="/ikea-assembly/">הרכבת רהיטים מאיקאה</a></li><li><a href="/guides/how-much-handyman/">כמה עולה הנדימן?</a></li><li><a href="/guides/wall-types-drilling/">איך מזהים את סוג הקיר</a></li><li><a href="/guides/handyman-visit-checklist/">איך מתכוננים לביקור הנדימן</a></li></ul>
    </div>
  </div>
</section>

{quote_band('צריכים הנדימן %s?' % c['in'], 'התקשרו או שלחו הודעה עם רשימת העבודות ותמונה. תקבלו מחיר ומועד הגעה.', 'טופס תחתון – ' + c['name'], city=c['name'], wa_text=wa_text)}'''
        svc = {'@type': 'Service', '@id': D + path + '#service', 'name': 'הנדימן ' + c['in'], 'serviceType': 'שירותי הנדימן', 'provider': {'@id': BIZ_ID},
               'areaServed': {'@type': 'City', 'name': c['name']}, 'url': D + path, 'description': desc,
               'offers': {'@type': 'AggregateOffer', 'priceCurrency': 'ILS', 'lowPrice': min(p[2] for p in C.PRICES), 'highPrice': max(p[2] for p in C.PRICES), 'offerCount': len(C.PRICES)}}
        extra = graph(business(), svc, webpage(path, title, desc, ['.speak-lead', '#prices .answer']), faq_node(faqs, path),
                      crumbs_node([('דף הבית', '/'), ('הנדימן ' + c['in'], path)]))
        write(c['slug'] + '/index.html', page(title, desc, path, content, extra, wa_text=wa_text, bg=True))


def wrap_tables(t):
    return re.sub(r'(<table class="simple">.*?</table>)', r'<div class="table-wrap">\1</div>', t, flags=re.S)


def build_guides():
    # דף כל המדריכים
    title = 'מדריכים לבית: תלייה, הרכבה ותיקונים | %s' % C.BRAND
    desc = 'מדריכים קצרים של %s: כמה עולה הנדימן, התקנת טלוויזיה, סוגי קירות, הרכבת רהיטים, דלתות, תיקונים לפני מסירת דירה ועוד.' % C.BRAND
    content = f'''<div class="wrap"><nav class="breadcrumb" aria-label="מיקום באתר"><a href="/">דף הבית</a> / <span>מדריכים</span></nav></div>
<section class="section" style="padding-top:20px" aria-labelledby="h1">
  <div class="wrap">
    <h1 id="h1">מדריכים לפני שמזמינים הנדימן</h1>
    <p class="section-lead">תשובות ברורות לשאלות שעולות לפני עבודה בבית: מה אפשר לעשות לבד, מה זה עולה, ומתי צריך בעל מקצוע.</p>
    {guide_cards()}
  </div>
</section>
{quote_band('מעדיפים שיונתן יטפל בזה?', 'שלחו רשימה ותמונה, ותקבלו מחיר סגור ומועד הגעה.', 'טופס בעמוד המדריכים')}'''
    coll = {'@type': 'CollectionPage', '@id': D + '/guides/#webpage', 'url': D + '/guides/', 'name': title, 'description': desc, 'inLanguage': 'he-IL',
            'isPartOf': {'@id': D + '/#website'}, 'hasPart': [{'@type': 'Article', 'headline': g['title'], 'url': '%s/guides/%s/' % (D, g['slug'])} for g in GUIDES]}
    write('guides/index.html', page(title, desc, '/guides/', content, graph(business(), coll, crumbs_node([('דף הבית', '/'), ('מדריכים', '/guides/')]))))

    # מדריך בודד
    for g in GUIDES:
        path = '/guides/%s/' % g['slug']
        toc = ''.join('<li><a href="#%s">%s</a></li>' % (i, t) for i, t, _ in g['sections'])
        secs = []
        for n, (i, t, h) in enumerate(g['sections']):
            secs.append('<h2 id="%s">%s</h2>\n%s' % (i, t, wrap_tables(fill(h))))
            if n == 1:
                secs.append(cta_strip(g['cta'], 'guide'))
        others = ''.join('<li><a href="/guides/%s/">%s</a></li>' % (o['slug'], o['short']) for o in GUIDES if o is not g)
        near = ''.join('<li><a href="/%s/">הנדימן %s</a></li>' % (s, CITY[s]['in']) for s in g['related_cities'])
        content = f'''<div class="wrap narrow"><nav class="breadcrumb" aria-label="מיקום באתר"><a href="/">דף הבית</a> / <a href="/guides/">מדריכים</a> / <span>{g['short']}</span></nav></div>
<article class="article wrap narrow">
<h1>{g['title']}</h1>
<p class="article-meta">מאת {C.BRAND} · עודכן ב־<time datetime="{C.LAST_UPDATED}">{C.LAST_UPDATED_HE}</time></p>
<p class="lead speak-lead">{fill(g['lead'])}</p>
<nav class="toc" aria-label="תוכן המדריך"><p>במדריך:</p><ol>{toc}<li><a href="#faq">שאלות נפוצות</a></li></ol></nav>
{chr(10).join(secs)}
<h2 id="faq">שאלות נפוצות</h2>
{faq_html(g['faq'])}
<div class="related">
  <p>מדריכים נוספים</p>
  <ul class="link-list">{others}</ul>
  <p>הנדימן באזור שלכם</p>
  <ul class="link-list">{near}<li><a href="/#areas">כל אזורי השירות</a></li></ul>
</div>
</article>
{quote_band(g['cta'], 'שלחו רשימה ותמונה, ותקבלו מחיר סגור ומועד הגעה. יונתן עובד במרכז ובשרון.', 'טופס במדריך', job=g['job'])}'''
        art = {'@type': 'Article', '@id': D + path + '#article', 'headline': g['title'], 'description': g['desc'], 'datePublished': C.LAST_UPDATED, 'dateModified': C.LAST_UPDATED,
               'inLanguage': 'he-IL', 'image': D + '/og-image.jpg', 'mainEntityOfPage': D + path, 'author': {'@id': BIZ_ID}, 'publisher': {'@id': BIZ_ID},
               'speakable': {'@type': 'SpeakableSpecification', 'cssSelector': ['.speak-lead']}}
        extra = graph(business(), art, faq_node(g['faq'], path), crumbs_node([('דף הבית', '/'), ('מדריכים', '/guides/'), (g['short'], path)]))
        write('guides/%s/index.html' % g['slug'], page(g['title'] + ' | ' + C.BRAND, g['desc'], path, content, extra, og='article'))


def build_landings():
    for L in LANDINGS:
        path = '/%s/' % L['slug']
        title = '%s | %s' % (L['title'], C.BRAND)
        desc = L['desc']
        wa = L['wa']
        pr = {k: (n, p, t) for k, n, p, t in C.PRICES}
        rows = ''.join('<tr><td>%s</td><td class="num">%d ₪</td><td>%s</td></tr>' % pr[k] for k in L['prices'])
        what = ''.join('<div class="local-card"><h3>%s</h3><p>%s</p></div>' % x for x in L['what'])
        why = ''.join('<div class="local-card"><h3>%s</h3><p>%s</p></div>' % x for x in L['why'])
        steps = ''.join('<li><h3>%s</h3><p>%s</p></li>' % x for x in L['steps'])
        prep = ''.join('<li>%s</li>' % x for x in L['prep'])
        cities = ''.join('<li><a href="/%s/">הנדימן %s</a></li>' % (c, CITY[c]['in']) for c in L['cities'])
        g = GUIDE[L['guide']]
        content = f"""<div class="wrap"><nav class="breadcrumb" aria-label="מיקום באתר"><a href="/">דף הבית</a> / <a href="/#services">שירותים</a> / <span>{L['nav']}</span></nav></div>
<section class="hero city-hero" aria-labelledby="h1">
  <div class="wrap hero-in">
    <div class="hero-copy">
      <p class="eyebrow">{L['eyebrow']}</p>
      <h1 id="h1">{L['h1']}</h1>
      <p class="lead speak-lead">{fill(L['lead'])}</p>
      {cta_buttons('hero', wa)}
      {chips()}
    </div>
    {ticket('hero-form', 'טופס עליון – ' + L['nav'], job=L['job'], sub=L['form_sub'])}
  </div>
</section>

<section class="section" id="what" aria-labelledby="what-h">
  <div class="wrap">
    <h2 id="what-h">{L['what_title']}</h2>
    <div class="local-grid">{what}</div>
  </div>
</section>

<section class="section alt" id="prices" aria-labelledby="prices-h">
  <div class="wrap">
    <h2 id="prices-h">כמה עולה {L['nav']}?</h2>
    <p class="answer narrow-text">{fill(L['faq'][0][1])}</p>
    <div class="table-wrap"><table class="prices"><caption>מחירון התחלתי (כולל מע״מ)</caption><thead><tr><th scope="col">עבודה</th><th scope="col">מחיר החל מ־</th><th scope="col">זמן עבודה משוער</th></tr></thead><tbody>{rows}</tbody></table></div>
    <p class="fine">{L['price_note']}</p>
    {cta_strip(L['strip'], 'prices', wa)}
  </div>
</section>

<section class="section" id="why" aria-labelledby="why-h">
  <div class="wrap">
    <h2 id="why-h">{L['why_title']}</h2>
    <div class="local-grid">{why}</div>
  </div>
</section>

<section class="section alt" id="how" aria-labelledby="how-h">
  <div class="wrap">
    <h2 id="how-h">{L['steps_title']}</h2>
    <ol class="steps">{steps}</ol>
    <h3 style="margin-top:20px">{L['prep_title']}</h3>
    <ul class="checks narrow-text" style="margin:0;display:flex;flex-direction:column;gap:8px">{prep}</ul>
    <p>רוצים לדעת מתי אפשר להרכיב לבד? קראו את <a href="/guides/{g['slug']}/" style="font-weight:700">{g['short']}: המדריך המלא</a>.</p>
  </div>
</section>

<section class="section" id="faq" aria-labelledby="faq-h">
  <div class="wrap narrow">
    <h2 id="faq-h">שאלות נפוצות על {L['nav']}</h2>
    {faq_html(L['faq'])}
    <div class="related">
      <p>{L['nav']} לפי עיר</p>
      <ul class="link-list">{cities}<li><a href="/#areas">כל אזורי השירות</a></li></ul>
    </div>
    {'<p class="fine">%s</p>' % L['disclaimer'] if L.get('disclaimer') else ''}
  </div>
</section>

{quote_band(L['band'][0], L['band'][1], 'טופס תחתון – ' + L['nav'], job=L['job'], wa_text=wa)}"""
        pr_all = [pr[k] for k in L['prices']]
        svc = {'@type': 'Service', '@id': D + path + '#service', 'name': L['nav'], 'serviceType': L['type'], 'provider': {'@id': BIZ_ID},
               'areaServed': [{'@type': 'City', 'name': c['name']} for c in CITIES], 'url': D + path, 'description': desc,
               'offers': [{'@type': 'Offer', 'name': n, 'priceCurrency': 'ILS', 'price': p,
                           'priceSpecification': {'@type': 'PriceSpecification', 'minPrice': p, 'priceCurrency': 'ILS', 'valueAddedTaxIncluded': True}} for n, p, _ in pr_all]}
        extra = graph(business(), svc, webpage(path, title, desc, ['.speak-lead', '#prices .answer']), faq_node(L['faq'], path),
                      crumbs_node([('דף הבית', '/'), ('שירותים', '/#services'), (L['nav'], path)]))
        write(L['slug'] + '/index.html', page(title, desc, path, content, extra, wa_text=wa, bg=True))


def contact_line(prefix):
    return f'{prefix} טלפון <a href="{TEL}" dir="ltr">{C.PHONE}</a> או מייל <a href="mailto:{C.EMAIL}">{C.EMAIL}</a>.'


def build_static():
    who = 'לרכז הנגישות שלנו, %s' % C.ACCESS_COORDINATOR if C.ACCESS_COORDINATOR else 'אלינו'
    acc = f'''<article class="article wrap narrow" style="padding-top:28px">
<h1>הצהרת נגישות</h1>
<p>{C.BRAND} פועל כדי שהאתר יהיה נוח ונגיש לכל אדם, בהתאם לתקנות שוויון זכויות לאנשים עם מוגבלות (התאמות נגישות לשירות), התשע"ג-2013, ולתקן הישראלי ת"י 5568 ברמת AA, המבוסס על הנחיות WCAG.</p>
<h2>מה יש באתר</h2>
<ul><li>תפריט נגישות צף: הגדלה והקטנה של התצוגה, ניגודיות גבוהה והדגשת קישורים.</li><li>אפשר לנווט במקלדת, ויש קישור לדילוג לתוכן הראשי.</li><li>מבנה כותרות מסודר, תוויות לשדות הטפסים וטקסט חלופי לתמונות.</li><li>האנימציות נעצרות אצל מי שהגדיר במכשיר הפחתת תנועה.</li></ul>
<h2>נתקלתם בבעיה?</h2>
<p>אם משהו באתר לא נגיש לכם, או שיש לכם הצעה לשיפור, נשמח שתפנו {who}. {contact_line('אפשר ליצור קשר ב')}</p>
<p>ההצהרה עודכנה לאחרונה ב־{C.LAST_UPDATED_HE}.</p>
</article>'''
    write('accessibility.html', page('הצהרת נגישות | ' + C.BRAND, 'הצהרת הנגישות של %s: ההתאמות באתר ופרטי הקשר לפניות בנושא נגישות.' % C.BRAND, '/accessibility.html', acc))

    pri = f'''<article class="article wrap narrow" style="padding-top:28px">
<h1>מדיניות פרטיות</h1>
<p>{C.BRAND} הוא עסק לשירותי הנדימן. אנחנו מכבדים את הפרטיות שלכם ומשתמשים במידע רק כדי לתת לכם שירות. בדף הזה מוסבר איזה מידע נאסף באתר ומה אנחנו עושים איתו.</p>
<h2>איזה מידע נאסף</h2>
<p><strong>מידע שאתם מוסרים:</strong> השם, מספר הטלפון, סוג העבודה והעיר שאתם משאירים בטופס, וגם העמוד שממנו שלחתם את הפנייה.</p>
<p><strong>מידע טכני:</strong> האתר עשוי להשתמש בכלים של גוגל למדידת ביקורים ופרסום. הכלים האלה יכולים לאסוף מידע כמו סוג הדפדפן והמכשיר, העמודים שבהם ביקרתם, ואם הגעתם מתוך מודעה. לשם כך הם משתמשים בעוגיות (קבצים קטנים שנשמרים בדפדפן). בנוסף, האתר רושם לחיצות על כפתורי החיוג והוואטסאפ, כדי למדוד אילו עמודים מביאים פניות.</p>
<h2>למה אנחנו משתמשים במידע</h2>
<p>כדי לחזור אליכם, לתת לכם הצעת מחיר ולתאם את העבודה. בנוסף, כדי למדוד אילו מודעות מביאות פניות ולשפר את האתר.</p>
<p>כשמופעלת מדידת המרות, מספר הטלפון שנשלח בטופס עובר לגוגל אחרי הצפנה, כדי להתאים בין הפנייה למודעה שהובילה אליה.</p>
<h2>עם מי המידע משותף</h2>
<p>אנחנו לא מוכרים את המידע שלכם. הפרטים מהטופס מגיעים אלינו בדואר אלקטרוני דרך שירות חיצוני לשליחת טפסים (FormSubmit), ונשמרים אצלנו בגיליון לידים בחשבון גוגל. מידע המדידה עובר לגוגל, לפי מדיניות הפרטיות של גוגל.</p>
<h2>כמה זמן שומרים את המידע</h2>
<p>כל עוד הוא נחוץ לטיפול בפנייה, לביצוע העבודה ולניהול העסק.</p>
<h2>הזכויות שלכם</h2>
<p>אתם יכולים לבקש לעיין במידע שלכם, לתקן אותו או למחוק אותו. אפשר גם לחסום עוגיות בהגדרות הדפדפן, ולשנות את העדפות הפרסום בגוגל בכתובת <a href="https://adssettings.google.com" target="_blank" rel="noopener">adssettings.google.com</a>.</p>
<p>{contact_line('לכל שאלה או בקשה בנושא פרטיות:')}</p>
<p>המדיניות עודכנה לאחרונה ב־{C.LAST_UPDATED_HE}.</p>
</article>'''
    write('privacy.html', page('מדיניות פרטיות | ' + C.BRAND, 'מדיניות הפרטיות של %s: איזה מידע נאסף באתר, למה משתמשים בו ומה הזכויות שלכם.' % C.BRAND, '/privacy.html', pri))

    art = '<div class="thanks-art" aria-hidden="true"><img src="/img/art/kit.webp" alt="" width="582" height="414"></div>' if HAS_ART else ''
    grid = ' style="grid-template-columns:minmax(0,720px);justify-content:center"' if not HAS_ART else ''
    ty = f'''<section class="thanks"><div class="wrap thanks-in"{grid}>
  <div class="thanks-card">
    <div class="check" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></div>
    <h1 id="t-title">תודה! הפנייה התקבלה</h1>
    <p class="lead">יונתן יחזור אליכם בהקדם עם מחיר ומועד הגעה. פניות שמגיעות מחוץ לשעות הפעילות מקבלות מענה ביום העבודה הבא.</p>
    <p class="fine">שעות פעילות: {hours(C.HOURS_HE)}</p>
    <p><strong>רוצים לזרז?</strong> שלחו תמונה של העבודה בוואטסאפ, או התקשרו:</p>
    {cta_buttons('thanks', 'היי יונתן, השארתי פרטים באתר. הנה תמונה של העבודה:')}
    <a style="font-weight:700" href="/">חזרה לעמוד הבית</a>
  </div>
  {art}
</div></section>
<script>
(function(){{
  try {{
    var name = sessionStorage.getItem('lead_name') || '';
    // ההמרה נספרת רק אחרי שליחת טופס אמיתית, ופעם אחת בלבד
    if (sessionStorage.getItem('lead_sent')) {{
      var phone = sessionStorage.getItem('lead_phone') || '';
      sessionStorage.removeItem('lead_sent');
      sessionStorage.removeItem('lead_phone');
      if (phone && window.SITE.ads) gtag('set', 'user_data', {{ phone_number: '+972' + phone.replace(/^0/, '') }});
      if (window.trackConversion) trackConversion('form');
    }}
    if (name) document.getElementById('t-title').textContent = 'תודה, ' + name + '! הפנייה התקבלה';
  }} catch(e) {{}}
}})();
</script>'''
    write('thank-you.html', page('תודה | ' + C.BRAND, 'קיבלנו את הפרטים שלכם.', '/thank-you.html', ty, robots='noindex, follow'))

    nf = f'''<section class="notice"><div class="wrap"><div class="thanks-card">
  <h1>העמוד הזה לא קיים</h1>
  <p class="lead">אולי הקישור השתנה. אפשר לחזור לדף הבית או לדבר ישירות עם יונתן.</p>
  {cta_buttons('404')}
  <a style="font-weight:700" href="/">חזרה לעמוד הבית</a>
</div></div></section>'''
    write('404.html', page('העמוד לא נמצא | ' + C.BRAND, 'העמוד לא נמצא.', '/404.html', nf, robots='noindex'))


def build_seo():
    urls = [('/', '1.0')] + [('/%s/' % l['slug'], '0.9') for l in LANDINGS] + [('/%s/' % c['slug'], '0.9' if c['main'] else '0.7') for c in CITIES] + [('/guides/', '0.7')] + \
           [('/guides/%s/' % g['slug'], '0.6') for g in GUIDES] + [('/accessibility.html', '0.2'), ('/privacy.html', '0.2')]
    rows = ''.join('  <url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n' % (D, u, C.LAST_UPDATED, p) for u, p in urls)
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % rows)
    bots = ['*', 'GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'Google-Extended', 'PerplexityBot', 'ClaudeBot', 'Claude-SearchBot', 'Bingbot']
    robots = '# מנועי חיפוש ומנועים מבוססי בינה מלאכותית: מותר במפורש\n' + ''.join('User-agent: %s\n' % b for b in bots) + \
             'Allow: /\nDisallow: /thank-you.html\nDisallow: /tools/\n\nSitemap: %s/sitemap.xml\n' % D
    write('robots.txt', robots)
    write('CNAME', D.split('//')[1] + '\n')
    write('.nojekyll', '')
    write('.htaccess', '''ErrorDocument 404 /404.html
RedirectMatch 404 ^/tools(/|$)
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
</IfModule>
<IfModule mod_expires.c>
ExpiresActive On
ExpiresByType image/webp "access plus 1 year"
ExpiresByType image/png "access plus 1 year"
ExpiresByType image/jpeg "access plus 1 year"
ExpiresByType text/css "access plus 1 year"
ExpiresByType application/javascript "access plus 1 year"
</IfModule>
''')
    L = ['# ' + C.BRAND, '',
         '> %s: תליית מדפים וטלוויזיות, הרכבת רהיטים ותיקוני דלתות במרכז ובשרון. מגיע עם כל הכלים, מחיר סגור מראש. התקשרו %s.' % (C.BRAND, C.PHONE), '',
         '- טלפון: ' + C.PHONE, '- וואטסאפ: https://wa.me/' + WA_NUM, '- מייל: ' + C.EMAIL,
         '- אזור שירות: המרכז והשרון – ' + ', '.join(c['name'] for c in CITIES),
         '- שעות פעילות: ' + C.HOURS_HE, '- אתר: %s/' % D, '', '## שירותים']
    L += ['- %s: %s' % (s[1], s[2]) for s in C.SERVICES]
    L += ['', '## מחירון התחלתי (כולל מע״מ, %s)' % C.PRICES_MONTH_HE]
    L += ['- %s: החל מ־%d ₪ (%s)' % (n, p, t) for _, n, p, t in C.PRICES]
    L += ['', '## שאלות נפוצות']
    for q, a in C.FAQ:
        L += ['### ' + q, plain(a), '']
    L += ['## דפי שירות']
    L += ['- [%s](%s/%s/): %s' % (l['title'], D, l['slug'], plain(l['lead'])) for l in LANDINGS]
    L += ['']
    L += ['## מדריכים']
    L += ['- [%s](%s/guides/%s/): %s' % (g['title'], D, g['slug'], plain(g['lead'])) for g in GUIDES]
    L += ['', '## עמודי ערים']
    L += ['- [הנדימן %s](%s/%s/)' % (c['in'], D, c['slug']) for c in CITIES]
    write('llms.txt', '\n'.join(L) + '\n')


def build_css():
    with open(os.path.join(HERE, 'base.css'), encoding='utf-8') as f:
        base = f.read()
    with open(os.path.join(HERE, 'extra.css'), encoding='utf-8') as f:
        write('assets/site.css', base + f.read())


def check_links():
    """בדיקה אחרי הבנייה: כל קישור פנימי מוביל לקובץ קיים, ואין מפתחות מחיר שלא מולאו."""
    bad = []
    for dp, dn, fn in os.walk(ROOT):
        if '/tools' in dp or '/.git' in dp:
            continue
        for n in fn:
            if not n.endswith('.html'):
                continue
            p = os.path.join(dp, n)
            with open(p, encoding='utf-8') as f:
                t = f.read()
            if '{{' in t:
                bad.append(p + ': מפתח שלא מולא')
            for u in re.findall(r'(?:href|src)="(/[^"#?]*)', t):
                target = os.path.join(ROOT, u.lstrip('/'))
                if u.endswith('/'):
                    target = os.path.join(target, 'index.html')
                if not os.path.exists(target) and u != '/':
                    bad.append('%s: %s' % (os.path.relpath(p, ROOT), u))
    return bad


if __name__ == '__main__':
    build_css()
    build_home(); build_landings(); build_cities(); build_guides(); build_static(); build_seo()
    bad = check_links()
    if bad:
        print('קישורים שבורים:'); print('\n'.join(bad)); sys.exit(1)
    print('נבנה בהצלחה: %d ערים, %d מדריכים' % (len(CITIES), len(GUIDES)))
