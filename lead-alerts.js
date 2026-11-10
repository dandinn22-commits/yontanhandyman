/*!
 * התראות לידים לטלגרם — קובץ אחד לכל המותגים.
 * מזהה: לחיצה על חיוג, לחיצה על וואטסאפ, לחיצה על מייל, שליחת טופס (+ אירועים נוספים לפי data-lead-event).
 * לכל אירוע מצורף המקור המדויק: ADS (ממומן), SEO (אורגני), GEO (בינה מלאכותית), רשתות, הפניה או ישיר.
 * שימוש: <script src="/lead-alerts.js" data-brand="שם המותג" defer></script>
 */
(function () {
  'use strict';

  var ENDPOINT = 'https://script.google.com/macros/s/AKfycbyIGN2dnsNvnpGs83Y22nb0IU_9q-40mpJHin9s4uHVgUDkTxabPs5Q20W1IrRFzy89Sg/exec';

  var script = document.currentScript || document.querySelector('script[data-brand]');
  var BRAND = (script && script.getAttribute('data-brand')) || location.hostname;
  if (!ENDPOINT || ENDPOINT.indexOf('__') === 0) return;
  if (/^(localhost|127\.|0\.0\.0\.0)/.test(location.hostname) && !/[?&]lt_test=1/.test(location.search)) return;

  /* ---------- אחסון בטוח ---------- */
  function store(kind) {
    try { var s = window[kind]; var k = '__lt'; s.setItem(k, '1'); s.removeItem(k); return s; } catch (e) { return null; }
  }
  var LS = store('localStorage'), SS = store('sessionStorage');
  function getJSON(s, k) { try { return s ? JSON.parse(s.getItem(k) || 'null') : null; } catch (e) { return null; } }
  function setJSON(s, k, v) { try { if (s) s.setItem(k, JSON.stringify(v)); } catch (e) {} }

  /* ---------- זיהוי מקור ---------- */
  var AI = [
    [/(^|\.)chatgpt\.com$|(^|\.)chat\.openai\.com$|(^|\.)openai\.com$/, 'ChatGPT'],
    [/(^|\.)perplexity\.ai$/, 'Perplexity'],
    [/(^|\.)gemini\.google\.com$|(^|\.)bard\.google\.com$/, 'Gemini'],
    [/(^|\.)copilot\.microsoft\.com$|(^|\.)copilot\.cloud\.microsoft$/, 'Copilot'],
    [/(^|\.)claude\.ai$/, 'Claude'],
    [/(^|\.)grok\.com$|(^|\.)x\.ai$/, 'Grok'],
    [/(^|\.)chat\.deepseek\.com$|(^|\.)deepseek\.com$/, 'DeepSeek'],
    [/(^|\.)meta\.ai$/, 'Meta AI'],
    [/(^|\.)chat\.mistral\.ai$/, 'Mistral'],
    [/(^|\.)you\.com$/, 'You.com'],
    [/(^|\.)phind\.com$/, 'Phind']
  ];
  var AI_UTM = /chatgpt|openai|perplexity|gemini|copilot|claude|grok|deepseek|meta\.?ai|mistral/i;
  var SEARCH = [
    [/(^|\.)google\.[a-z.]+$/, 'Google'],
    [/(^|\.)bing\.com$/, 'Bing'],
    [/(^|\.)duckduckgo\.com$/, 'DuckDuckGo'],
    [/(^|\.)yahoo\.[a-z.]+$/, 'Yahoo'],
    [/(^|\.)yandex\.[a-z.]+$/, 'Yandex'],
    [/(^|\.)ecosia\.org$/, 'Ecosia'],
    [/(^|\.)baidu\.com$/, 'Baidu'],
    [/(^|\.)brave\.com$/, 'Brave']
  ];
  var SOCIAL = [
    [/(^|\.)facebook\.com$|(^|\.)fb\.com$|^l\.facebook\.com$|^lm\.facebook\.com$/, 'פייסבוק'],
    [/(^|\.)instagram\.com$/, 'אינסטגרם'],
    [/(^|\.)tiktok\.com$/, 'טיקטוק'],
    [/(^|\.)youtube\.com$|(^|\.)youtu\.be$/, 'יוטיוב'],
    [/(^|\.)linkedin\.com$|^lnkd\.in$/, 'לינקדאין'],
    [/^t\.co$|(^|\.)twitter\.com$|(^|\.)x\.com$/, 'X / טוויטר'],
    [/(^|\.)whatsapp\.com$|^wa\.me$/, 'וואטסאפ'],
    [/(^|\.)t\.me$|(^|\.)telegram\.org$/, 'טלגרם'],
    [/(^|\.)pinterest\.[a-z.]+$/, 'פינטרסט'],
    [/(^|\.)reddit\.com$/, 'רדיט']
  ];
  function match(list, host) {
    for (var i = 0; i < list.length; i++) if (list[i][0].test(host)) return list[i][1];
    return null;
  }
  function hostOf(url) { try { return new URL(url).hostname.toLowerCase(); } catch (e) { return ''; } }
  function sameSite(h) {
    var a = h.replace(/^www\./, ''), b = location.hostname.toLowerCase().replace(/^www\./, '');
    return a === b;
  }

  function detect() {
    var q = new URLSearchParams(location.search);
    var p = function (k) { return (q.get(k) || '').trim(); };
    var ref = document.referrer || '';
    var rh = hostOf(ref);
    var utmSource = p('utm_source'), utmMedium = p('utm_medium').toLowerCase();
    var src = {
      landing: location.pathname + (location.search ? location.search.slice(0, 300) : ''),
      referrer: ref ? ref.slice(0, 200) : '',
      campaign: p('utm_campaign'),
      term: p('utm_term') || p('keyword'),
      content: p('utm_content'),
      matchtype: p('matchtype'),
      at: Date.now()
    };

    // 1. ממומן בגוגל
    if (p('gclid') || p('gbraid') || p('wbraid') || p('gad_source') || p('gad_campaignid') ||
        (/google/i.test(utmSource) && /^(cpc|ppc|paid|paidsearch|paid_search|sem)$/.test(utmMedium))) {
      src.kind = 'ADS'; src.channel = 'גוגל ממומן';
      src.network = p('network'); src.device_ads = p('device');
      src.clickid = p('gclid') ? 'gclid' : (p('gbraid') ? 'gbraid' : (p('wbraid') ? 'wbraid' : ''));
      return src;
    }
    // 2. ממומן במיקרוסופט / פייסבוק / טיקטוק / אחר
    if (p('msclkid')) { src.kind = 'ADS'; src.channel = 'Bing ממומן'; return src; }
    if (/^(cpc|ppc|paid|paid_social|paidsocial|ads?)$/.test(utmMedium) || p('ttclid')) {
      var who = utmSource || (p('ttclid') ? 'tiktok' : 'לא ידוע');
      src.kind = 'ADS'; src.channel = 'ממומן – ' + who; return src;
    }
    if (p('fbclid') && /^(fb|facebook|ig|instagram|meta)$/i.test(utmSource)) {
      src.kind = 'ADS'; src.channel = 'ממומן – מטא (' + utmSource + ')'; return src;
    }
    // 3. בינה מלאכותית (GEO)
    var ai = rh ? match(AI, rh) : null;
    if (!ai && utmSource && AI_UTM.test(utmSource)) ai = utmSource;
    if (ai) { src.kind = 'GEO'; src.channel = ai; return src; }
    // 4. חיפוש אורגני (SEO)
    var se = rh ? match(SEARCH, rh) : null;
    if (se) { src.kind = 'SEO'; src.channel = se; return src; }
    if (/^organic$/.test(utmMedium)) { src.kind = 'SEO'; src.channel = utmSource || 'אורגני'; return src; }
    // 5. רשתות חברתיות
    var so = rh ? match(SOCIAL, rh) : null;
    if (so || p('fbclid')) { src.kind = 'SOCIAL'; src.channel = so || 'פייסבוק/אינסטגרם'; return src; }
    if (utmSource) { src.kind = 'UTM'; src.channel = utmSource + (utmMedium ? ' / ' + utmMedium : ''); return src; }
    // 6. הפניה מאתר אחר
    if (rh && !sameSite(rh)) { src.kind = 'REFERRAL'; src.channel = rh.replace(/^www\./, ''); return src; }
    // 7. ישיר / מעבר פנימי
    if (rh && sameSite(rh)) return null; // ניווט בתוך האתר — לא כניסה חדשה
    src.kind = 'DIRECT'; src.channel = 'ישיר';
    return src;
  }

  var now = detect();
  var session = getJSON(SS, 'lt_session');
  var first = getJSON(LS, 'lt_first');
  var lastPaid = getJSON(LS, 'lt_last_nondirect');
  var MAX_AGE = 90 * 24 * 3600 * 1000;
  if (first && Date.now() - first.at > MAX_AGE) first = null;
  if (lastPaid && Date.now() - lastPaid.at > MAX_AGE) lastPaid = null;

  if (now) {
    // כניסה חדשה לאתר. כניסה ישירה באמצע ביקור לא דורסת מקור קיים.
    if (!(now.kind === 'DIRECT' && session)) { session = now; setJSON(SS, 'lt_session', session); }
    if (!first) { first = now; setJSON(LS, 'lt_first', first); }
    if (now.kind !== 'DIRECT') { lastPaid = now; setJSON(LS, 'lt_last_nondirect', now); }
  }
  if (!session) { session = { kind: 'DIRECT', channel: 'ישיר (לא זוהה)', landing: location.pathname, at: Date.now() }; setJSON(SS, 'lt_session', session); }

  var visits = 1;
  try {
    if (LS) {
      if (!SS || !SS.getItem('lt_counted')) {
        visits = (parseInt(LS.getItem('lt_visits') || '0', 10) || 0) + 1;
        LS.setItem('lt_visits', String(visits));
        if (SS) SS.setItem('lt_counted', '1');
      } else visits = parseInt(LS.getItem('lt_visits') || '1', 10) || 1;
    }
  } catch (e) {}

  /* ---------- שליחה ---------- */
  var recent = {};
  function send(event, extra, dedupe) {
    var key = event + '|' + (dedupe || '');
    var t = Date.now();
    if (recent[key] && t - recent[key] < 4000) return;
    recent[key] = t;

    var body = {
      v: 1,
      brand: BRAND,
      site: location.hostname.replace(/^www\./, ''),
      event: event,
      page: location.pathname,
      title: (document.title || '').slice(0, 120),
      source: session,
      first: (first && first.at !== session.at) ? first : null,
      prev: (session.kind === 'DIRECT' && lastPaid && lastPaid.at !== session.at) ? lastPaid : null,
      visits: visits,
      device: /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent) ? 'נייד' : 'מחשב',
      lang: navigator.language || '',
      extra: extra || {}
    };
    var data = JSON.stringify(body);
    try {
      if (navigator.sendBeacon && navigator.sendBeacon(ENDPOINT, new Blob([data], { type: 'text/plain;charset=UTF-8' }))) return;
    } catch (e) {}
    try {
      fetch(ENDPOINT, { method: 'POST', mode: 'no-cors', keepalive: true, headers: { 'Content-Type': 'text/plain;charset=UTF-8' }, body: data });
    } catch (e) {}
  }
  window.leadAlert = send; // לשימוש ידני: leadAlert('purchase', {...})

  /* ---------- לחיצות ---------- */
  function labelOf(el) {
    var txt = (el.getAttribute('aria-label') || el.textContent || '').replace(/\s+/g, ' ').trim();
    return txt.slice(0, 60);
  }
  function placeOf(el) {
    var sec = el.parentElement && el.parentElement.closest('header,nav,footer,[class*="float"],[class*="sticky"],[class*="fab"],section,[id]');
    if (!sec) return '';
    var tag = sec.tagName.toLowerCase();
    var cls = (typeof sec.className === 'string' ? sec.className : '').split(/\s+/)[0] || '';
    if (tag === 'header' || tag === 'nav') return 'תפריט עליון';
    if (tag === 'footer') return 'תחתית';
    if (/float|sticky|fab/i.test(cls)) return 'כפתור צף';
    if (/hero|^hx|banner|top/i.test(cls + ' ' + sec.id)) return 'אזור הפתיחה';
    if (/cta|contact|quote|lead/i.test(cls + ' ' + sec.id)) return 'אזור יצירת קשר';
    if (/bar|mobile/i.test(cls)) return 'פס תחתון בנייד';
    return sec.id ? ('#' + sec.id) : (cls ? '.' + cls : tag);
  }

  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href],[data-lead-event]') : null;
    if (!a) return;
    var custom = a.getAttribute('data-lead-event');
    if (custom) { send(custom, { label: labelOf(a), place: placeOf(a) }, custom); return; }
    var href = a.getAttribute('href') || '';
    if (/^tel:/i.test(href)) {
      send('call', { number: href.replace(/^tel:/i, ''), label: labelOf(a), place: placeOf(a) }, href);
    } else if (/^(https?:\/\/)?(wa\.me|api\.whatsapp\.com|web\.whatsapp\.com|chat\.whatsapp\.com)\b|^whatsapp:/i.test(href)) {
      send('whatsapp', { label: labelOf(a), place: placeOf(a) }, href.split('?')[0]);
    } else if (/^mailto:/i.test(href)) {
      send('email', { to: href.replace(/^mailto:/i, '').split('?')[0], label: labelOf(a), place: placeOf(a) }, href);
    }
  }, true);

  /* ---------- טפסים ---------- */
  var SKIP = /^(_|g-recaptcha|cf-turnstile|csrf|token|nonce|website$|url$|honeypot|hp_)/i;
  function fieldValue(f) {
    if (f.tagName === 'SELECT') {
      var o = f.options[f.selectedIndex];
      return o && o.value !== '' ? (o.text || o.value) : '';
    }
    if (f.type === 'checkbox') return f.checked ? 'כן' : 'לא';
    return (f.value || '').trim();
  }
  function honeypotFilled(form) {
    var hp = form.querySelectorAll('input[name="_honey"],input[name="website"],input[name="honeypot"],input[name^="hp_"]');
    for (var i = 0; i < hp.length; i++) if (hp[i].value) return true;
    return false;
  }
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form || form.tagName !== 'FORM' || form.hasAttribute('data-lead-ignore')) return;
    if (/search/i.test(form.getAttribute('role') || '') || form.querySelector('input[type="search"]')) return;
    if (honeypotFilled(form)) return;
    var fields = {}, phoneOk = false, emailOk = false, any = false;
    var els = form.elements;
    for (var i = 0; i < els.length; i++) {
      var f = els[i];
      if (!f.name || SKIP.test(f.name) || f.disabled) continue;
      if (/^(submit|button|reset|password|file)$/.test(f.type)) continue;
      if (f.type === 'radio' && !f.checked) continue;
      var v = fieldValue(f);
      if (v === '') continue;
      v = v.slice(0, 500);
      fields[f.name] = fields[f.name] && f.type !== 'radio' ? fields[f.name] + ', ' + v : v;
      any = true;
      if (f.type === 'tel' || /phone|tel|mobile|טלפון|נייד/i.test(f.name)) { if (v.replace(/\D/g, '').length >= 9) phoneOk = true; }
      if (f.type === 'email' || /mail/i.test(f.name)) { if (/.+@.+\..+/.test(v)) emailOk = true; }
    }
    if (!any) return;
    var hasPhoneField = !!form.querySelector('input[type="tel"],[name*="phone" i],[name*="tel" i]');
    var hasEmailField = !!form.querySelector('input[type="email"],[name*="mail" i]');
    // טופס עם novalidate שנשלח ריק/שגוי — לא שולחים התראה
    if ((hasPhoneField || hasEmailField) && !phoneOk && !emailOk) return;
    var formName = form.getAttribute('data-source') || form.getAttribute('aria-label') || form.getAttribute('name') || form.id || '';
    send('form', { form: formName, fields: fields }, JSON.stringify(fields));
  }, true);
})();
