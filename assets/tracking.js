/* מדידה: גוגל אדס, אנליטיקס ורישום לחיצות. הערכים מגיעים מ-tools/config.py דרך window.SITE */
(function(){
  var S = window.SITE || {};
  var LABELS = S.labels || {};
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function(){ dataLayer.push(arguments); };
  if (S.ads || S.ga4) {
    gtag('js', new Date());
    if (S.ads) gtag('config', S.ads, { allow_enhanced_conversions: true });
    if (S.ga4) gtag('config', S.ga4);
  }

  // זיהוי מבקר שהגיע ממודעה (נשמר לכל הביקור)
  try {
    if (/[?&](gclid|gbraid|wbraid)=|[?&]utm_medium=cpc/.test(location.search)) sessionStorage.setItem('from_ads', '1');
    window.fromAds = sessionStorage.getItem('from_ads') === '1';
  } catch(e) { window.fromAds = false; }

  var GA4_EVENTS = { form: 'generate_lead', call: 'click_call', whatsapp: 'click_whatsapp' };
  window.trackConversion = function(kind, cta){
    try {
      if (S.ads && LABELS[kind]) gtag('event', 'conversion', { send_to: S.ads + '/' + LABELS[kind] });
      if (S.ga4) gtag('event', GA4_EVENTS[kind] || kind, { page_path: location.pathname, cta: cta || '' });
    } catch(e) {}
  };

  function logClick(kind){
    if (!S.sheet) return;
    try {
      var data = new URLSearchParams({ type: 'click', kind: kind, page: location.pathname + (window.fromAds ? ' – גוגל אדס' : '') });
      if (navigator.sendBeacon) navigator.sendBeacon(S.sheet, data);
      else fetch(S.sheet, { method: 'POST', mode: 'no-cors', keepalive: true, body: data });
    } catch(e) {}
  }

  document.addEventListener('click', function(e){
    var a = e.target && e.target.closest ? e.target.closest('a') : null;
    if (!a) return;
    var href = a.getAttribute('href') || '';
    var kind = href.indexOf('tel:') === 0 ? 'call' : (href.indexOf('wa.me') > -1 ? 'whatsapp' : '');
    if (!kind) return;
    // בדף התודה הליד כבר נספר
    if (location.pathname.indexOf('thank-you') === -1) trackConversion(kind, a.getAttribute('data-cta'));
    logClick(kind);
  }, true);
})();
