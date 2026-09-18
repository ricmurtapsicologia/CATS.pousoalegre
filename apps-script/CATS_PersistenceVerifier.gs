/**
 * CATS Pré-curso — verificador de persistência v1.
 * Deploy como Web App (doGet não é necessário). Retorna somente status e hashes;
 * nunca retorna dados pessoais ou respostas clínicas.
 */
const CATS = Object.freeze({
  protocol: 'cats-persistence-v1',
  formEditId: '1107fjdaiL42Zb0n2jNjKr0aiNNysyEADQCesdBTbD_E',
  sheetId: '1wQ0nc6TmCqqbu-ZqloIRLptO6iHqDhD00qrFLxP-fUk',
  sheetName: 'Respostas ao formulário 1',
  maxRowsToScan: 120,
  clockSkewMs: 2 * 60 * 1000,
});

function doPost(e) {
  try {
    const payload = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    return json_(verifyPersistence_(payload));
  } catch (err) {
    return json_({
      protocol: CATS.protocol,
      persisted: false,
      terminal: true,
      reason: 'invalid-request',
    });
  }
}

function verifyPersistence_(payload) {
  if (!payload || payload.protocol !== CATS.protocol) return negative_('protocol-mismatch', true);
  if (payload.formEditId !== CATS.formEditId) return negative_('form-id-mismatch', true);
  if (payload.sheetId !== CATS.sheetId) return negative_('sheet-id-mismatch', true);
  if (!/^[a-f0-9]{64}$/i.test(String(payload.fingerprint || ''))) return negative_('invalid-fingerprint', true);

  // Pinagem do Google Form exato informado pelo coordenador e do destino dele.
  const form = FormApp.openById(CATS.formEditId);
  const destinationId = String(form.getDestinationId() || '');
  if (destinationId !== CATS.sheetId) return negative_('form-destination-mismatch', true);

  const ss = SpreadsheetApp.openById(CATS.sheetId);
  const sheet = ss.getSheetByName(CATS.sheetName);
  if (!sheet) return negative_('sheet-tab-not-found', true);

  const lastRow = sheet.getLastRow();
  const lastCol = sheet.getLastColumn();
  if (lastRow < 2) return negative_('no-responses', false);

  const headers = sheet.getRange(1, 1, 1, lastCol).getDisplayValues()[0];
  const idx = indexHeaders_(headers);
  const required = ['timestamp', 'date', 'email', 'cpf', 'name'];
  for (const key of required) {
    if (idx[key] < 0) return negative_('header-not-found:' + key, true);
  }

  const startRow = Math.max(2, lastRow - CATS.maxRowsToScan + 1);
  const rows = sheet.getRange(startRow, 1, lastRow - startRow + 1, lastCol).getValues();
  const submittedAt = Number(payload.submittedAtEpochMs || 0);
  const lowerBound = submittedAt > 0 ? submittedAt - CATS.clockSkewMs : 0;
  const tz = ss.getSpreadsheetTimeZone() || Session.getScriptTimeZone() || 'America/Sao_Paulo';

  for (let i = rows.length - 1; i >= 0; i--) {
    const row = rows[i];
    const ts = timestampMs_(row[idx.timestamp], tz);
    if (lowerBound && ts && ts < lowerBound) break;

    const canonical = [
      canonicalText_(row[idx.name]).toUpperCase(),
      canonicalText_(row[idx.email]).toLowerCase(),
      canonicalText_(row[idx.cpf]).replace(/\D/g, ''),
      canonicalDate_(row[idx.date], tz),
    ].join('|');

    const fingerprint = sha256_(canonical);
    if (fingerprint === String(payload.fingerprint).toLowerCase()) {
      return {
        protocol: CATS.protocol,
        persisted: true,
        terminal: true,
        formEditId: CATS.formEditId,
        sheetId: CATS.sheetId,
        fingerprint: fingerprint,
      };
    }
  }

  return negative_('row-not-yet-visible', false, payload.fingerprint);
}

function indexHeaders_(headers) {
  const normalized = headers.map(normalizeHeader_);
  const find = (...needles) => normalized.findIndex(h => needles.some(n => h === n || h.indexOf(n) >= 0));
  return {
    timestamp: find('carimbo de data/hora'),
    date: find('data de preenchimento'),
    email: find('melhor e-mail'),
    cpf: find('cpf'),
    name: find('nome completo em caixa alta'),
  };
}

function normalizeHeader_(value) {
  return String(value || '')
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .toLowerCase().trim().replace(/\s+/g, ' ');
}

function canonicalText_(value) {
  return String(value == null ? '' : value).trim().replace(/\s+/g, ' ');
}

function canonicalDate_(value, tz) {
  if (Object.prototype.toString.call(value) === '[object Date]' && !isNaN(value.getTime())) {
    return Utilities.formatDate(value, tz, 'yyyy-MM-dd');
  }
  const s = canonicalText_(value);
  let m = s.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (m) return s;
  m = s.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
  if (m) return `${m[3]}-${m[2]}-${m[1]}`;
  return s;
}

function timestampMs_(value, tz) {
  if (Object.prototype.toString.call(value) === '[object Date]' && !isNaN(value.getTime())) return value.getTime();
  const s = canonicalText_(value);
  const m = s.match(/^(\d{2})\/(\d{2})\/(\d{4})\s+(\d{2}):(\d{2})(?::(\d{2}))?$/);
  if (!m) return 0;
  // Utilities.parseDate exists in Apps Script and respects spreadsheet timezone.
  try {
    return Utilities.parseDate(s, tz, 'dd/MM/yyyy HH:mm:ss').getTime();
  } catch (err) {
    return 0;
  }
}

function sha256_(value) {
  const digest = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, value, Utilities.Charset.UTF_8);
  return digest.map(b => ((b < 0 ? b + 256 : b).toString(16).padStart(2, '0'))).join('');
}

function negative_(reason, terminal, fingerprint) {
  return {
    protocol: CATS.protocol,
    persisted: false,
    terminal: !!terminal,
    reason: reason,
    formEditId: CATS.formEditId,
    sheetId: CATS.sheetId,
    fingerprint: fingerprint || '',
  };
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
