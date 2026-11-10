/**
 * יונתן הנדימן – קבלת לידים מהאתר לגיליון "לידים - יונתן הנדימן"
 * כל פנייה מהטפסים נכנסת ללשונית "לידים", וכל לחיצה על חיוג או וואטסאפ נכנסת ללשונית "לחיצות".
 * (המייל על כל ליד נשלח כבר מהאתר עצמו, ולכן הסקריפט לא שולח מייל נוסף.)
 *
 * הגדרה (פעם אחת):
 * 1. בגיליון "לידים - יונתן הנדימן": תוספים > Apps Script.
 * 2. מוחקים את מה שיש בעורך, מדביקים את כל הקובץ ושומרים.
 * 3. פריסה > פריסה חדשה > אפליקציית אינטרנט. הרצה בתור: אני. גישה: כל אחד.
 * 4. מאשרים הרשאות ומעתיקים את הכתובת שמסתיימת ב-/exec
 *    אל SHEET_ENDPOINT בקובץ tools/config.py, ואז מריצים את tools/build.py.
 */
const SHEET_ID = '1gq_dhiiHqiaI1YAjI8DTyTHehL8vj33Q1HTfsZ-iEPw';
const TZ = 'Asia/Jerusalem';

function clean_(v, max) {
  v = String(v == null ? '' : v).replace(/[\u0000-\u001f]/g, ' ').trim();
  if (/^[=+\-@]/.test(v)) v = "'" + v;   // מונע הזרקת נוסחאות לגיליון
  return v.slice(0, max || 200);
}

function today_() {
  return '=DATE(' + Utilities.formatDate(new Date(), TZ, 'yyyy,M,d') + ')';
}

function doGet() { return ContentService.createTextOutput('ok'); }

function doPost(e) {
  const p = (e && e.parameter) || {};
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const ss = SpreadsheetApp.openById(SHEET_ID);
    const time = Utilities.formatDate(new Date(), TZ, 'HH:mm');

    // לחיצה על חיוג או וואטסאפ
    if (p.type === 'click') {
      ss.getSheetByName('לחיצות').appendRow([
        today_(), time,
        p.kind === 'call' ? 'שיחת טלפון' : 'וואטסאפ',
        clean_(p.page, 150)
      ]);
      return ContentService.createTextOutput('ok');
    }

    // ליד מטופס
    const name = clean_(p.name, 80);
    const phone = clean_(p.phone, 20).replace(/[^\d+\-\s]/g, '');
    if (!name || phone.replace(/\D/g, '').length < 9) return ContentService.createTextOutput('bad');

    const form = clean_(p.source, 80);
    const source = form.indexOf('גוגל אדס') > -1 ? 'גוגל אדס' : 'טופס באתר';
    const notes = 'טופס: ' + form.replace(/\s*–\s*גוגל אדס/, '') + ' | עמוד: ' + clean_(p.page, 150);

    const sh = ss.getSheetByName('לידים');
    const id = sh.getLastRow();            // שורה 1 היא הכותרות
    // מס' ליד, תאריך, שעה, שם, טלפון, עיר, סוג עבודה, פירוט, מקור, סטטוס,
    // זמן מענה, תאריך הצעה, סכום הצעה, סכום סגירה, מטפל, פעולה הבאה, תאריך פעולה, הערות
    sh.appendRow([
      id, today_(), time, name, "'" + phone,
      clean_(p.city, 40), clean_(p.job, 60), '',
      source, 'חדש', '', '', '', '', '',
      'לחזור ללקוח', today_(), notes
    ]);
    return ContentService.createTextOutput('ok');
  } finally {
    lock.releaseLock();
  }
}
