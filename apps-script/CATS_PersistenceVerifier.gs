/**
 * CATS Pré-curso — verificador de persistência v1.4.
 * Objetivo: só confirmar conclusão quando a linha correspondente estiver
 * materializada na planilha oficial. Não retorna PII, respostas clínicas nem
 * resultado BDI-II ao navegador.
 *
 * A notificação por e-mail é idempotente e pode ser acionada por duas rotas:
 * 1) pela própria verificação positiva solicitada pelo navegador;
 * 2) pelo gatilho instalável onFormSubmit da planilha, como redundância.
 *
 * Deploy: Web App | executar como proprietário | acesso: qualquer pessoa.
 */
const CATS = Object.freeze({
  protocol: 'cats-persistence-v1',
  runtimeVersion: '2026.09.18-r4-bdi-email-private',
  formEditId: '1107fjdaiL42Zb0n2jNjKr0aiNNysyEADQCesdBTbD_E',
  sheetId: '1wQ0nc6TmCqqbu-ZqloIRLptO6iHqDhD00qrFLxP-fUk',
  sheetName: 'Respostas ao formulário 1',
  emailTo: 'ricmurtapsicologia@gmail.com',
  maxRowsToScan: 160,
});

const BDI_II = Object.freeze({
  headers: Object.freeze([
    'tristeza',
    'pessimismo',
    'perda de prazer',
    'fracasso passado',
    'sentimentos de culpa',
    'sentimentos de punicao',
    'auto estima',
    'autocritica',
    'pensamentos ou desejos suicidas',
    'choro',
    'agitacao',
    'perda de interesse',
    'indecisao',
    'desvalorizacao',
    'falta de energia',
    'alteracoes no padrao de sono',
    'irritabilidade',
    'alteracoes de apetite',
    'dificuldade de concentracao',
    'cansaco ou fadiga',
    'perda de interesse por sexo',
  ]),
  specialScores: Object.freeze({
    'alteracoes no padrao de sono': Object.freeze([0, 1, 1, 2, 2, 3, 3]),
    'alteracoes de apetite': Object.freeze([0, 1, 1, 2, 2, 3, 3]),
  }),
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
      // O resultado BDI-II é deliberadamente excluído deste retorno. O navegador
      // recebe apenas o estado técnico de persistência.
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
 * Envia uma única cópia integral da linha persistida. O BDI-II é calculado aqui,
 * no backend, e inserido somente no e-mail administrativo. O resultado nunca é
 * devolvido ao navegador.
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

    const bdi = computeBdiIi_(headers, values);
    const bdiScoreText = bdi.ok
      ? 'BDI-II: ' + bdi.total + '/63 — intensidade ' + bdi.label + ' (' + bdi.range + ').'
      : 'BDI-II: cálculo indisponível — ' + bdi.scored + '/21 itens reconhecidos.';
    const bdiMeaningText = bdi.ok
      ? 'Significado: faixa ' + bdi.label + ' de intensidade de sintomas depressivos no rastreio. Este resultado não equivale a diagnóstico clínico.'
      : 'Significado: não gerado, pois o cálculo automático não reconheceu os 21 itens necessários.';

    const textBody = [
      'CATS — nova resposta do pré-curso confirmada na planilha oficial',
      '',
      'Respondente: ' + name,
      'Registro: ' + timestamp,
      'Linha: ' + row,
      'Origem da notificação: ' + source,
      '',
      'RESULTADO BDI-II — USO RESTRITO À COORDENAÇÃO',
      bdiScoreText,
      bdiMeaningText,
      'Este resultado não é exibido ao respondente.',
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

    const bdiHtml = [
      '<div style="margin:16px 0;padding:14px 16px;border:1px solid #d1d5db;border-radius:10px;background:#f8fafc">',
      '<div style="font-size:12px;font-weight:700;letter-spacing:.04em;color:#475569">RESULTADO BDI-II — USO RESTRITO À COORDENAÇÃO</div>',
      '<p style="margin:8px 0 4px"><strong>' + htmlEscape_(bdiScoreText) + '</strong></p>',
      '<p style="margin:0;color:#475569">' + htmlEscape_(bdiMeaningText) + '</p>',
      '<p style="margin:6px 0 0;font-size:12px;color:#64748b">Este resultado não é exibido ao respondente.</p>',
      '</div>'
    ].join('');

    const htmlBody = [
      '<div style="font-family:Arial,sans-serif;color:#1f2937">',
      '<h2 style="margin:0 0 12px">CATS — nova resposta do pré-curso</h2>',
      '<p><strong>Persistência confirmada na planilha oficial.</strong></p>',
      '<p><strong>Respondente:</strong> ' + htmlEscape_(name) + '<br>',
      '<strong>Registro:</strong> ' + htmlEscape_(timestamp) + '<br>',
      '<strong>Linha:</strong> ' + row + '</p>',
      bdiHtml,
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

function computeBdiIi_(headers, values) {
  try {
    const headerIndexes = {};
    headers.forEach((header, i) => {
      const key = normalizeBdiKey_(header);
      if (key && headerIndexes[key] === undefined) headerIndexes[key] = i;
    });

    const form = FormApp.openById(CATS.formEditId);
    const items = {};
    form.getItems().forEach(item => {
      const key = normalizeBdiKey_(item.getTitle());
      if (key && items[key] === undefined) items[key] = item;
    });

    let total = 0;
    let scored = 0;
    const missing = [];

    BDI_II.headers.forEach(key => {
      const column = headerIndexes[key];
      const item = items[key];
      const selected = column === undefined ? '' : canonicalText_(values[column]);
      const choices = item ? formChoiceValues_(item) : [];
      if (column === undefined || !selected || !choices.length) {
        missing.push(key);
        return;
      }

      const selectedIndex = choices.findIndex(choice => canonicalText_(choice) === selected);
      if (selectedIndex < 0) {
        missing.push(key);
        return;
      }

      const special = BDI_II.specialScores[key];
      const points = special ? special[selectedIndex] : selectedIndex;
      if (!Number.isInteger(points) || points < 0 || points > 3) {
        missing.push(key);
        return;
      }

      total += points;
      scored += 1;
    });

    if (scored !== BDI_II.headers.length) {
      return { ok: false, total: null, scored: scored, missing: missing };
    }

    const band = bdiIiBand_(total);
    return {
      ok: true,
      total: total,
      max: 63,
      scored: scored,
      label: band.label,
      range: band.range,
    };
  } catch (err) {
    console.error('[CATS BDI-II] ' + String(err && err.message || err));
    return { ok: false, total: null, scored: 0, missing: [], error: String(err && err.message || err) };
  }
}

function formChoiceValues_(item) {
  switch (item.getType()) {
    case FormApp.ItemType.MULTIPLE_CHOICE:
      return item.asMultipleChoiceItem().getChoices().map(choice => choice.getValue());
    case FormApp.ItemType.LIST:
      return item.asListItem().getChoices().map(choice => choice.getValue());
    default:
      return [];
  }
}

function bdiIiBand_(score) {
  if (score <= 13) return { label: 'mínima', range: '0–13' };
  if (score <= 19) return { label: 'leve', range: '14–19' };
  if (score <= 28) return { label: 'moderada', range: '20–28' };
  return { label: 'grave', range: '29–63' };
}

function normalizeBdiKey_(value) {
  return String(value || '')
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()
    .replace(/\s+/g, ' ');
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
