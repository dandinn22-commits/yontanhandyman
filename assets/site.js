/* טפסים, בחירת עבודה מכרטיס שירות ותפריט נגישות */
(function(){
  var S = window.SITE || {};
  var LEAD_ENDPOINT = 'https://formsubmit.co/ajax/' + S.leadEmail;

  // מחזיר מספר ישראלי תקין בפורמט 05XXXXXXXX, או מחרוזת ריקה
  function normalizePhone(raw){
    var d = String(raw || '').replace(/[^\d+]/g, '');
    if (d.indexOf('+972') === 0) d = '0' + d.slice(4);
    else if (d.indexOf('972') === 0 && d.length >= 11) d = '0' + d.slice(3);
    d = d.replace(/\D/g, '');
    if (d.length === 9 && d.charAt(0) !== '0') d = '0' + d;
    return /^0(?:5\d{8}|7\d{8}|[23489]\d{7})$/.test(d) ? d : '';
  }

  function handleForm(form){
    var btn = form.querySelector('button[type=submit]');
    var nameEl = form.querySelector('[name=name]');
    var phoneEl = form.querySelector('[name=phone]');
    var jobEl = form.querySelector('[name=job]');
    var cityEl = form.querySelector('[name=city]');
    var hp = form.querySelector('[name=_honey]');
    var errBox = form.querySelector('.form-error');
    var nameErr = form.querySelector('.err-name');
    var phoneErr = form.querySelector('.err-phone');
    var source = form.getAttribute('data-source') || 'טופס';
    var btnText = btn.textContent;

    function mark(el, err, on){
      err.hidden = !on;
      if (on) el.setAttribute('aria-invalid', 'true'); else el.removeAttribute('aria-invalid');
    }
    nameEl.addEventListener('input', function(){ mark(nameEl, nameErr, false); });
    phoneEl.addEventListener('input', function(){ mark(phoneEl, phoneErr, false); });

    form.addEventListener('submit', function(e){
      e.preventDefault();
      if (btn.disabled) return;
      errBox.hidden = true;
      var name = nameEl.value.trim();
      var phone = normalizePhone(phoneEl.value);
      var job = jobEl ? jobEl.value : '';
      var city = cityEl ? cityEl.value : '';
      mark(nameEl, nameErr, name.length < 2);
      mark(phoneEl, phoneErr, !phone);
      if (name.length < 2){ nameEl.focus(); return; }
      if (!phone){ phoneEl.focus(); return; }

      // שדה נסתר שרק רובוטים ממלאים: לא שולחים ולא סופרים המרה
      if (hp && hp.value){ location.href = '/thank-you.html'; return; }

      btn.disabled = true;
      btn.textContent = 'שולח...';
      var finished = false;
      var src = source + (window.fromAds ? ' – גוגל אדס' : '');

      function success(){
        if (finished) return; finished = true;
        try {
          sessionStorage.setItem('lead_name', name);
          sessionStorage.setItem('lead_phone', phone);
          sessionStorage.setItem('lead_sent', '1');
        } catch(err) {}
        location.href = '/thank-you.html';
      }
      function failure(){
        if (finished) return; finished = true;
        btn.disabled = false;
        btn.textContent = btnText;
        errBox.textContent = '';
        errBox.appendChild(document.createTextNode('השליחה לא עברה. '));
        var msg = 'היי יונתן, אני ' + name + ' (' + phone + ')' + (city ? ' מ' + city : '') + '. אני צריך הנדימן' + (job ? ': ' + job : '') + '.';
        var wa = document.createElement('a');
        wa.href = 'https://wa.me/' + S.wa + '?text=' + encodeURIComponent(msg);
        wa.target = '_blank'; wa.rel = 'noopener';
        wa.textContent = 'שלחו את הפרטים בוואטסאפ';
        var tel = document.createElement('a');
        tel.href = 'tel:' + S.tel; tel.dir = 'ltr'; tel.textContent = S.phone;
        errBox.appendChild(wa);
        errBox.appendChild(document.createTextNode(' או התקשרו ל־'));
        errBox.appendChild(tel);
        errBox.hidden = false;
      }
      var timer = setTimeout(failure, 12000);

      if (S.sheet) {
        try {
          fetch(S.sheet, { method: 'POST', mode: 'no-cors', keepalive: true,
            body: new URLSearchParams({ name: name, phone: phone, job: job, city: city, source: src, page: location.pathname }) });
        } catch(err) {}
      }

      var body = new URLSearchParams({
        'שם': name, 'טלפון': phone, 'עבודה': job, 'עיר': city, 'טופס': source,
        'מקור': window.fromAds ? 'גוגל אדס' : 'אתר / חיפוש רגיל',
        'עמוד': location.pathname,
        _subject: 'ליד חדש – יונתן הנדימן – ' + name + ' ' + phone + (city ? ' – ' + city : ''),
        _cc: S.leadCc || '',
        _template: 'table', _captcha: 'false', _honey: ''
      });
      try {
        fetch(LEAD_ENDPOINT, { method: 'POST', keepalive: true, headers: {'Accept': 'application/json'}, body: body })
          .then(function(r){ return r.json(); })
          .then(function(res){
            clearTimeout(timer);
            if (res && (res.success === true || res.success === 'true')) success(); else failure();
          }, function(){ clearTimeout(timer); failure(); });
      } catch(err) { clearTimeout(timer); failure(); }
    });
  }
  document.querySelectorAll('form.lead-form').forEach(handleForm);

  // לחיצה על "קבלו מחיר" בכרטיס שירות בוחרת את סוג העבודה בטופס
  document.querySelectorAll('a[data-job]').forEach(function(a){
    a.addEventListener('click', function(){
      var sel = document.querySelector('#quote [name=job]');
      if (sel) sel.value = a.getAttribute('data-job');
      var nm = document.querySelector('#quote [name=name]');
      if (nm) setTimeout(function(){ nm.focus({ preventScroll: true }); }, 500);
    });
  });

  // תפריט נגישות
  var toggle = document.getElementById('accessToggle');
  var panel = document.getElementById('accessPanel');
  if (toggle && panel) {
    var step = 0, root = document.querySelector('.page') || document.body;
    function apply(){ root.style.zoom = step ? String(1 + step * 0.12) : ''; }
    toggle.addEventListener('click', function(){
      var open = panel.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function(e){
      if (e.key === 'Escape' && panel.classList.contains('open')) {
        panel.classList.remove('open'); toggle.setAttribute('aria-expanded', 'false'); toggle.focus();
      }
    });
    panel.addEventListener('click', function(e){
      var action = e.target.getAttribute('data-action');
      if (!action) return;
      if (action === 'font-up' && step < 3) step++;
      if (action === 'font-down' && step > -2) step--;
      if (action === 'contrast') document.documentElement.classList.toggle('high-contrast');
      if (action === 'links') document.documentElement.classList.toggle('mark-links');
      if (action === 'reset') {
        step = 0;
        document.documentElement.classList.remove('high-contrast', 'mark-links');
      }
      apply();
    });
  }
})();
