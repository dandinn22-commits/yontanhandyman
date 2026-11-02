/**
 * יונתן הנדימן – גיבוי לידים ולחיצות לגיליון
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

function doGet() { return ContentService.createTextOutput('ok'); }

function doPost(e) {
  const p = (e && e.parameter) || {};
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const ss = SpreadsheetApp.openById(SHEET_ID);
    const now = new Date();
    const date = Utilities.formatDate(now, TZ, 'dd/MM/yyyy');
    const time = Utilities.formatDate(now, TZ, 'HH:mm');
    if (p.type === 'click') {
      ss.getSheetByName('לחיצות').appendRow([date, time, clean_(p.kind, 20), clean_(p.page, 150)]);
    } else {
      const phone = clean_(p.phone, 20).replace(/[^\d+\-\s]/g, '');
      if (phone.replace(/\D/g, '').length < 9) return ContentService.createTextOutput('bad');
      ss.getSheetByName('לידים').appendRow([date, time, clean_(p.name, 80), "'" + phone,
        clean_(p.job, 60), clean_(p.city, 40), clean_(p.source, 60), clean_(p.page, 150), 'חדש', '']);
    }
    return ContentService.createTextOutput('ok');
  } finally {
    lock.releaseLock();
  }
}
