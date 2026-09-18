/**
 * CATS Pré-curso — verificador de persistência v1.3.
 * Objetivo: só confirmar conclusão quando a linha correspondente estiver
 * materializada na planilha oficial. Não retorna PII nem respostas clínicas.
 *
 * A notificação por e-mail é idempotente e pode ser acionada por duas rotas:
 * 1) pela própria verificação positiva solicitada pelo navegador;
 * 2) pelo gatilho instalável onFormSubmit da planilha, como redundância.
 *
 * Deploy: Web App | executar como proprietário | acesso: qualquer pessoa.
 */
const CATS = Object.freeze({
  protocol: 'cats-persistence-v1',
  runtimeVersion: '2026.09.18-r3-email-idempotent',
  formEditId: '1107fjdaiL42Zb0n2jNjKr0aiNNysyEADQCesdBTbD_E',
  sheetId: '1wQ0nc6TmCqqbu-ZqloIRLptO6iHqDhD00qrFLxP-fUk',
  sheetName: 'Respostas ao formulário 1',
  emailTo: 'ricmurtapsicologia@gmail.com',
  maxRowsToScan: 160,
});

function doGet() {
  return json_({
    protocol: CATS.protocol,
    status: 'ready',
    runtimeVersion: CATS.runtimeVersion,
    emailDeliveryMode: 'verification-plus-trigger-idempotent',
    formEditId: CATS.formEditId,
    sheetId: CATS.sheetId,
  });
}

function doPost(e) {
  let stage = 'parse-request';
  let fingerprint = '';
  try {
    const payload = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    fingerprint = String(payload && payload.fingerprint || '');
    stage = 'verify-request';
    return json_(verifyPersistence_(payload));
  } catch (err) {
    return json_({
      protocol: CATS.protocol,
      persisted: false,
      terminal: true,
      reason: 'backend-error',
      stage: stage,
      formEditId: CATS.formEditId,
      sheetId: CATS.sheetId,
      fingerprint: fingerprint,
    });
  }
}

function verifyPersistence_(payload) {
  if (!payload || payload.protocol !== CATS.protocol) return negative_('protocol-mismatch', true);
  if (payload.formEditId !== CATS.formEditId) return negative_('form-id-mismatch', true);
  if (payload.sheetId !== CATS.sheetId) return negative_('sheet-id-mismatch', true);
  if (!/^[a-f0-9]{64}$/i.test(String(payload.fingerprint || ''))) return negative_('invalid-fingerprint', true);

  let ss;
  try {
    ss = SpreadsheetApp.openById(CATS.sheetId);
  } catch (err) {
    return backendNegative_('open-sheet', payload.fingerprint);
  }

  let sheet;
  try {
    sheet = ss.getSheetByName(CATS.sheetName);
  } catch (err) {
    return backendNegative_('open-tab', payload.fingerprint);
  }
  if (!sheet) return negative_('sheet-tab-not-found', true, payload.fingerprint);

  let lastRow, lastCol, headers, rows;
  try {
    lastRow = sheet.getLastRow();
    lastCol = sheet.getLastColumn();
    if (lastRow < 2) return negative_('no-responses', false, payload.fingerprint);
    headers = sheet.getRange(1, 1, 1, lastCol).getDisplayValues()[0];
  } catch (err) {
    return backendNegative_('read-sheet-metadata', payload.fingerprint);
  }

  const idx = indexHeaders_(headers);
  const required = ['timestamp', 'date', 'email', 'cpf', 'name'];
  for (const key of required) {
    if (idx[key] < 0) return negative_('header-not-found:' + key, true, payload.fingerprint);
  }

  const startRow = Math.max(2, lastRow - CATS.maxRowsToScan + 1);
  try {
    rows = sheet.getRange(startRow, 1, lastRow - startRow + 1, lastCol).getValues();
  } catch (err) {
    return backendNegative_('read-response-rows', payload.fingerprint);
  }

  const tz = ss.getSpreadsheetTimeZone() || Session.getScriptTimeZone() || 'America/Sao_Paulo';
  const expectedFingerprint = String(payload.fingerprint).toLowerCase();

  // O relógio do dispositivo NÃO participa da exclusão de linhas. A busca é
  // limitada às respostas recentes e a identidade é validada pelo fingerprint.
  for (let i = rows.length - 1; i >= 0; i--) {
    const row = rows[i];
    const canonical = [
      canonicalText_(row[idx.name]).toUpperCase(),
      canonicalText_(row[idx.email]).toLowerCase(),
      canonicalText_(row[idx.cpf]).replace(/\D/g, ''),
      canonicalDate_(row[idx.date], tz),
    ].join('|');

    const fingerprint = sha256_(canonical);
    if (fingerprint === expectedFingerprint) {
      const absoluteRow = startRow + i;
      let notificationStatus = 'not-requested';
      if (payload.notifyEmail === true) {
        notificationStatus = notifyPersistedResponse_(sheet, absoluteRow, 'verification');
      }
      return {
        protocol: CATS.protocol,
        persisted: true,
        terminal: true,
        runtimeVersion: CATS.runtimeVersion,
        emailNotification: notificationStatus,
        formEditId: CATS.formEditId,
        sheetId: CATS.sheetId,
        fingerprint: fingerprint,
      };
    }
  }

  return negative_('row-not-yet-visible', false, payload.fingerprint);
}

/**
 * Executa UMA vez no editor do Apps Script para criar o gatilho redundante.
 * A rota principal de notificação é a confirmação positiva do verificador;
 * este gatilho garante notificação mesmo se o participante fechar a página.
 */
function installEmailTrigger() {
  const handler = 'emailSubmittedResponse';
  ScriptApp.getProjectTriggers()
    .filter(t => t.getHandlerFunction() === handler)
    .forEach(t => ScriptApp.deleteTrigger(t));

  ScriptApp.newTrigger(handler)
    .forSpreadsheet(CATS.sheetId)
    .onFormSubmit()
    .create();

  return 'Gatilho redundante de e-mail instalado para ' + CATS.emailTo;
}

/**
 * Handler do gatilho instalável. Compartilha a mesma chave idempotente usada
 * pela rota de verificação, portanto nunca deve duplicar uma notificação já enviada.
 */
function emailSubmittedResponse(e) {
  if (!e || !e.range) return;

  const sheet = e.range.getSheet();
  const ss = sheet.getParent();
  if (ss.getId() !== CATS.sheetId || sheet.getName() !== CATS.sheetName) return;

  const row = e.range.getRow();
  if (row < 2) return;
  notifyPersistedResponse_(sheet, row, 'sheet-trigger');
}

/**
 * Envia uma única cópia integral da linha persistida.
 * Retorna somente estado técnico; não expõe PII ao cliente do Web App.
 */
function notifyPersistedResponse_(sheet, row, source) {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(10000)) return 'busy';

  try {
    const lastCol = sheet.getLastColumn();
    const headers = sheet.getRange(1, 1, 1, lastCol).getDisplayValues()[0];
    const values = sheet.getRange(row, 1, 1, lastCol).getDisplayValues()[0];
    const idx = indexHeaders_(headers);
    const timestamp = idx.timestamp >= 0 ? String(values[idx.timestamp] || '') : '';
    const key = 'cats-email:' + sha256_([
      CATS.sheetId,
      sheet.getSheetId(),
      row,
      timestamp,
    ].join('|'));

    const props = PropertiesService.getScriptProperties();
    if (props.getProperty(key)) return 'already-sent';

    const name = idx.name >= 0 ? values[idx.name] : 'Respondente';
    const pairs = headers
      .map((header, i) => ({ header: String(header || '').trim(), value: String(values[i] || '').trim() }))
      .filter(item => item.header || item.value);

    const textBody = [
      'CATS — nova resposta do pré-curso confirmada na planilha oficial',
      '',
      'Respondente: ' + name,
      'Registro: ' + timestamp,
      'Linha: ' + row,
      'Origem da notificação: ' + source,
      '',
      ...pairs.map(item => item.header + ': ' + item.value),
      '',
      'Planilha oficial: https://docs.google.com/spreadsheets/d/' + CATS.sheetId + '/edit'
    ].join('\n');

    const rowsHtml = pairs.map(item =>
      '<tr><th style="text-align:left;vertical-align:top;padding:6px 10px;border-bottom:1px solid #ddd;background:#f7f7f7">' +
      htmlEscape_(item.header) +
      '</th><td style="vertical-align:top;padding:6px 10px;border-bottom:1px solid #ddd">' +
      htmlEscape_(item.value).replace(/\n/g, '<br>') +
      '</td></tr>'
    ).join('');

    const htmlBody = [
      '<div style="font-family:Arial,sans-serif;color:#1f2937">',
      '<h2 style="margin:0 0 12px">CATS — nova resposta do pré-curso</h2>',
      '<p><strong>Persistência confirmada na planilha oficial.</strong></p>',
      '<p><strong>Respondente:</strong> ' + htmlEscape_(name) + '<br>',
      '<strong>Registro:</strong> ' + htmlEscape_(timestamp) + '<br>',
      '<strong>Linha:</strong> ' + row + '</p>',
      '<table style="border-collapse:collapse;width:100%;max-width:900px">' + rowsHtml + '</table>',
      '<p style="margin-top:16px"><a href="https://docs.google.com/spreadsheets/d/' + CATS.sheetId + '/edit">Abrir planilha oficial</a></p>',
      '</div>'
    ].join('');

    MailApp.sendEmail({
      to: CATS.emailTo,
      subject: 'CATS Pré-curso | resposta confirmada | ' + name,
      body: textBody,
      htmlBody: htmlBody,
      name: 'CATS Pré-curso'
    });

    // Só grava o marcador depois de MailApp aceitar o envio. Se houver exceção,
    // uma próxima verificação ou o gatilho poderá tentar novamente.
    props.setProperty(key, new Date().toISOString());
    return 'sent';
  } catch (err) {
    console.error('[CATS email] ' + String(err && err.message || err));
    return 'error';
  } finally {
    lock.releaseLock();
  }
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

function sha256_(value) {
  const digest = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, value, Utilities.Charset.UTF_8);
  return digest.map(b => ((b < 0 ? b + 256 : b).toString(16).padStart(2, '0'))).join('');
}

function htmlEscape_(value) {
  return String(value == null ? '' : value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function backendNegative_(stage, fingerprint) {
  return {
    protocol: CATS.protocol,
    persisted: false,
    terminal: true,
    reason: 'backend-error',
    stage: stage,
    runtimeVersion: CATS.runtimeVersion,
    formEditId: CATS.formEditId,
    sheetId: CATS.sheetId,
    fingerprint: fingerprint || '',
  };
}

function negative_(reason, terminal, fingerprint) {
  return {
    protocol: CATS.protocol,
    persisted: false,
    terminal: !!terminal,
    reason: reason,
    runtimeVersion: CATS.runtimeVersion,
    formEditId: CATS.formEditId,
    sheetId: CATS.sheetId,
    fingerprint: fingerprint || '',
  };
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
