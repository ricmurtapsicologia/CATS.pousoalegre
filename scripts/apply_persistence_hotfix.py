from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRE = ROOT / "precurso.html"
E2E = ROOT / "scripts" / "e2e_precurso.py"
WORKFLOW = ROOT / ".github" / "workflows" / "precurso-smoke-e2e.yml"
SPEC = ROOT / "docs" / "precurso-persistence-spec.md"
CONFIG = ROOT / "persistence-config.js"
VERIFIER = ROOT / "apps-script" / "CATS_PersistenceVerifier.gs"

FORM_EDIT_ID = "1107fjdaiL42Zb0n2jNjKr0aiNNysyEADQCesdBTbD_E"
SHEET_ID = "1wQ0nc6TmCqqbu-ZqloIRLptO6iHqDhD00qrFLxP-fUk"
FORM_ACTION = "https://docs.google.com/forms/d/e/1FAIpQLScVj6HESm2cWDN3sNQCaoNOtWSKini7NbSHgiTXemwlyvqAXg/formResponse"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: esperado 1 match; encontrados {count}")
    return text.replace(old, new, 1)


def patch_precurso() -> None:
    text = PRE.read_text(encoding="utf-8")
    text = text.replace("2026.09.09-r6", "2026.09.18-r7-persistence")

    text = replace_once(
        text,
        '  <script defer src="cats-auth.js?v=20260909-2"></script>\n',
        '  <script defer src="cats-auth.js?v=20260909-2"></script>\n'
        '  <script src="persistence-config.js?v=20260918-1"></script>\n',
        "config script",
    )

    text = replace_once(
        text,
        f"  const FORM_ACTION='{FORM_ACTION}';\n",
        f"  const FORM_ACTION='{FORM_ACTION}';\n"
        f"  const OFFICIAL_FORM_EDIT_ID='{FORM_EDIT_ID}';\n"
        f"  const RESPONSE_SHEET_ID='{SHEET_ID}';\n"
        "  const VERIFY_POLL_MS=1200;\n"
        "  const VERIFY_TIMEOUT_MS=18000;\n",
        "official ids",
    )

    guard = r'''
  const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));

  function canonicalText(value){
    return String(value??'').trim().replace(/\s+/g,' ');
  }

  async function sha256Hex(value){
    const bytes=new TextEncoder().encode(value);
    const digest=await crypto.subtle.digest('SHA-256',bytes);
    return [...new Uint8Array(digest)].map(b=>b.toString(16).padStart(2,'0')).join('');
  }

  function fieldValue(form,name){
    return form.querySelector(`[name="${name}"]`)?.value??'';
  }

  async function buildPersistencePayload(form,submittedAtEpochMs){
    const canonical=[
      canonicalText(fieldValue(form,'entry.1067284683')).toUpperCase(),
      canonicalText(fieldValue(form,'entry.1556369182')).toLowerCase(),
      canonicalText(fieldValue(form,'entry.426148251')).replace(/\D/g,''),
      canonicalText(fieldValue(form,'entry.2092238618'))
    ].join('|');
    return {
      protocol:'cats-persistence-v1',
      formEditId:OFFICIAL_FORM_EDIT_ID,
      sheetId:RESPONSE_SHEET_ID,
      submittedAtEpochMs,
      fingerprint:await sha256Hex(canonical)
    };
  }

  async function callPersistenceVerifier(payload){
    if(typeof window.__CATS_PERSISTENCE_VERIFY__==='function'){
      return await window.__CATS_PERSISTENCE_VERIFY__(payload);
    }
    const endpoint=String(window.CATS_PERSISTENCE_VERIFY_URL||'').trim();
    if(!endpoint){
      return {persisted:false,terminal:true,reason:'verifier-not-configured'};
    }
    try{
      const response=await fetch(endpoint,{
        method:'POST',
        headers:{'Content-Type':'text/plain;charset=UTF-8'},
        body:JSON.stringify(payload),
        cache:'no-store',
        credentials:'omit',
        redirect:'follow'
      });
      if(!response.ok){
        return {persisted:false,terminal:false,reason:`http-${response.status}`};
      }
      return await response.json();
    }catch(error){
      console.warn('[CATS persistence] verifier request failed',error);
      return {persisted:false,terminal:false,reason:'network-error'};
    }
  }

  function isValidPersistenceConfirmation(result,payload){
    return result?.persisted===true
      && result?.protocol==='cats-persistence-v1'
      && result?.sheetId===RESPONSE_SHEET_ID
      && result?.formEditId===OFFICIAL_FORM_EDIT_ID
      && result?.fingerprint===payload.fingerprint;
  }

  async function verifyUntilPersisted(payload){
    const override=Number(window.__CATS_PERSISTENCE_VERIFY_TIMEOUT__||0);
    const timeout=Number.isFinite(override)&&override>0?override:VERIFY_TIMEOUT_MS;
    const deadline=Date.now()+timeout;
    let last={persisted:false,reason:'not-checked'};
    do{
      last=await callPersistenceVerifier(payload);
      if(isValidPersistenceConfirmation(last,payload))return {ok:true,result:last};
      if(last?.terminal===true)break;
      if(Date.now()<deadline)await sleep(VERIFY_POLL_MS);
    }while(Date.now()<=deadline);
    return {ok:false,result:last};
  }

  function installPersistenceGuard(doc,form){
    const responseFrame=doc.getElementById('google-response');
    const success=doc.getElementById('success');
    const submit=doc.getElementById('submitBtn');
    if(!responseFrame||!success||!submit)throw new Error('Guard de persistência: estrutura incompleta');

    const style=doc.createElement('style');
    style.id='catsPersistenceGuardStyle';
    style.textContent='#success:not([data-persistence-confirmed="true"]){display:none!important}';
    doc.head.append(style);

    const status=doc.createElement('div');
    status.id='catsPersistenceStatus';
    status.className='notice info';
    status.setAttribute('role','status');
    status.setAttribute('aria-live','polite');
    status.hidden=true;

    const actions=submit.closest('.actions');
    if(!actions)throw new Error('Guard de persistência: ações não encontradas');
    actions.parentNode.insertBefore(status,actions);

    const verifyAgain=doc.createElement('button');
    verifyAgain.type='button';
    verifyAgain.id='catsVerifyAgain';
    verifyAgain.className='btn btn-secondary';
    verifyAgain.textContent='Verificar gravação';
    verifyAgain.hidden=true;
    actions.insertBefore(verifyAgain,submit);

    let state=null;

    function keepUnconfirmedVisible(){
      success.removeAttribute('data-persistence-confirmed');
      success.classList.remove('show');
      form.style.display='';
    }

    function setPending(message){
      keepUnconfirmedVisible();
      status.hidden=false;
      status.className='notice info';
      status.textContent=message;
      verifyAgain.hidden=true;
    }

    function setUnconfirmed(){
      keepUnconfirmedVisible();
      status.hidden=false;
      status.className='notice warn';
      status.textContent='A tentativa de envio terminou, mas a gravação na planilha oficial NÃO foi confirmada. O preenchimento ainda não está concluído. Não feche esta página.';
      verifyAgain.hidden=false;
      submit.disabled=true;
      submit.textContent='Envio sem confirmação';
    }

    function setConfirmed(payload){
      status.hidden=true;
      verifyAgain.hidden=true;
      success.dataset.persistenceConfirmed='true';
      const h=success.querySelector('h2');
      const p=success.querySelector('p');
      if(h)h.textContent='Preenchimento confirmado';
      if(p)p.textContent='Dados gravados na planilha oficial de respostas.';
      form.style.display='none';
      success.classList.add('show');
      success.dataset.fingerprint=payload.fingerprint.slice(0,12);
    }

    async function runVerification(){
      if(!state||state.verifying)return;
      state.verifying=true;
      verifyAgain.disabled=true;
      setPending('Verificando a gravação na planilha oficial...');
      try{
        const payload=await state.payloadPromise;
        const verification=await verifyUntilPersisted(payload);
        if(verification.ok){
          state.confirmed=true;
          setConfirmed(payload);
        }else{
          setUnconfirmed();
        }
      }catch(error){
        console.error('[CATS persistence]',error);
        setUnconfirmed();
      }finally{
        state.verifying=false;
        verifyAgain.disabled=false;
      }
    }

    form.addEventListener('submit',event=>{
      if(event.defaultPrevented)return;
      const submittedAtEpochMs=Date.now();
      state={
        submittedAtEpochMs,
        payloadPromise:buildPersistencePayload(form,submittedAtEpochMs),
        verifying:false,
        confirmed:false
      };
      setPending('Enviando ao Google Forms. Aguardando confirmação da planilha oficial...');
    });

    responseFrame.addEventListener('load',()=>{
      if(!state||state.confirmed)return;
      // legacy.html trata qualquer load do iframe como sucesso. Este hotfix
      // reverte essa sinalização antes da pintura e só libera o sucesso
      // depois da confirmação independente da planilha.
      keepUnconfirmedVisible();
      runVerification();
    });

    verifyAgain.addEventListener('click',()=>runVerification());

    return {getState:()=>state,runVerification};
  }
'''

    text = replace_once(
        text,
        "  frame.addEventListener('load',()=>{\n",
        guard + "\n  frame.addEventListener('load',()=>{\n",
        "persistence guard helpers",
    )

    text = replace_once(
        text,
        "      form.dataset.formsLinked='true';\n",
        "      form.dataset.formsLinked='true';\n"
        "      form.dataset.persistenceGuard='strict';\n",
        "guard dataset",
    )

    text = replace_once(
        text,
        "      if(missing.length||temporary.length)throw new Error('Mapeamento do Google Forms incompleto');\n",
        "      if(missing.length||temporary.length)throw new Error('Mapeamento do Google Forms incompleto');\n"
        "      installPersistenceGuard(doc,form);\n",
        "guard install",
    )

    text = replace_once(
        text,
        "        if(h)h.textContent='Envio concluído';\n        if(p)p.textContent='As respostas foram encaminhadas ao formulário oficial.';\n",
        "        if(h)h.textContent='Confirmação pendente';\n        if(p)p.textContent='O preenchimento só será concluído após confirmação na planilha oficial.';\n",
        "neutral initial success copy",
    )

    PRE.write_text(text, encoding="utf-8")


def patch_e2e() -> None:
    text = E2E.read_text(encoding="utf-8")
    old = '''    # ------------------------------------------------------------------\n    # 10) Submissão ponta a ponta sem gravar dados falsos no formulário real.\n    # ------------------------------------------------------------------\n    frame.locator("#submitBtn").click()\n    frame.locator("#success").wait_for(state="visible", timeout=10000)\n    assert submitted["seen"]\n    assert "Envio concluído" in frame.locator("#success").inner_text()\n    assert "formulário oficial" in frame.locator("#success").inner_text()\n    assert form.is_hidden()\n    context.close()\n'''
    new = f'''    # ------------------------------------------------------------------\n    # 10) Gate de persistência: HTTP 200 do formResponse NÃO é sucesso.\n    # O sucesso só é liberado por confirmação independente da planilha\n    # oficial, com IDs e fingerprint exatos.\n    # ------------------------------------------------------------------\n    page.evaluate(\n        """() => {{\n          window.__catsVerifierMode = 'wrong-sheet';\n          window.__CATS_PERSISTENCE_VERIFY_TIMEOUT__ = 500;\n          window.__CATS_PERSISTENCE_VERIFY__ = async payload => ({{\n            protocol: 'cats-persistence-v1',\n            persisted: true,\n            terminal: true,\n            sheetId: window.__catsVerifierMode === 'positive'\n              ? '{SHEET_ID}'\n              : 'SHEET-ERRADA',\n            formEditId: '{FORM_EDIT_ID}',\n            fingerprint: payload.fingerprint\n          }});\n        }}"""\n    )\n\n    frame.locator("#submitBtn").click()\n    frame.locator("#catsPersistenceStatus").wait_for(state="visible", timeout=10000)\n    frame.wait_for_function(\n        "document.getElementById('catsPersistenceStatus').textContent.includes('NÃO foi confirmada')",\n        timeout=10000,\n    )\n    assert submitted["seen"]\n    assert frame.locator("#success").is_hidden()\n    assert form.is_visible()\n    assert frame.locator("#submitBtn").is_disabled()\n    assert frame.locator("#catsVerifyAgain").is_visible()\n\n    # Agora o verificador devolve confirmação da planilha correta.\n    page.evaluate("window.__catsVerifierMode = 'positive'")\n    frame.locator("#catsVerifyAgain").click()\n    frame.locator("#success").wait_for(state="visible", timeout=10000)\n    assert "Preenchimento confirmado" in frame.locator("#success").inner_text()\n    assert "planilha oficial" in frame.locator("#success").inner_text()\n    assert form.is_hidden()\n    assert frame.locator("#success").get_attribute("data-persistence-confirmed") == "true"\n    context.close()\n'''
    text = replace_once(text, old, new, "E2E persistence section")
    text = text.replace(
        'print("PASS: Smoke + E2E CATS — formulário pré-carregado, pós-login <1s, gate, 3 etapas, POST e mobile.")',
        'print("PASS: Smoke + E2E CATS — POST isolado não conclui; sucesso exige persistência confirmada na planilha oficial.")',
    )
    E2E.write_text(text, encoding="utf-8")


def patch_workflow() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    if "      - 'persistence-config.js'\n" not in text:
        text = replace_once(
            text,
            "      - 'precurso.html'\n",
            "      - 'precurso.html'\n      - 'persistence-config.js'\n",
            "workflow config path",
        )
    WORKFLOW.write_text(text, encoding="utf-8")


def write_config() -> None:
    CONFIG.write_text(
        "// CATS pré-curso — endpoint de verificação de persistência.\n"
        "// FAIL-CLOSED: enquanto vazio, a interface NUNCA acusa preenchimento concluído.\n"
        "window.CATS_PERSISTENCE_VERIFY_URL = '';\n",
        encoding="utf-8",
    )


def write_spec() -> None:
    SPEC.parent.mkdir(parents=True, exist_ok=True)
    SPEC.write_text(f'''# SPEC — CATS Pré-curso · confirmação de persistência\n\n## Pinpoint\n\n- Página pública: `precurso.html` (carrega `legacy.html` em iframe same-origin).\n- Google Form oficial informado pelo coordenador, ID de edição: `{FORM_EDIT_ID}`.\n- Endpoint publicado atualmente usado pela página: `{FORM_ACTION}`.\n- Planilha oficial de respostas: `{SHEET_ID}` · aba `Respostas ao formulário 1`.\n\n## Defeito raiz\n\n`legacy.html` tratava qualquer evento `load` do iframe `google-response` como sucesso. Um HTTP 200 sintético, uma página de erro ou qualquer resposta carregada no iframe era suficiente para esconder o formulário e mostrar “Envio concluído”. O E2E anterior repetia exatamente esse falso positivo: interceptava `/formResponse`, devolvia HTML 200 e considerava o fluxo aprovado, sem conferir Google Forms nem Google Sheets.\n\n## Invariantes do hotfix\n\n1. `load` de `formResponse` sozinho nunca libera sucesso.\n2. `#success` fica bloqueado por CSS enquanto não existir `data-persistence-confirmed="true"`.\n3. A confirmação positiva exige simultaneamente:\n   - `persisted === true`;\n   - protocolo `cats-persistence-v1`;\n   - `formEditId === {FORM_EDIT_ID}`;\n   - `sheetId === {SHEET_ID}`;\n   - `fingerprint` igual ao calculado no navegador para NOME + melhor e-mail + CPF + data de preenchimento.\n4. Ausência do verificador, erro de rede, timeout, ID divergente ou fingerprint divergente = **fail closed**: o formulário continua visível e a página declara explicitamente que o preenchimento NÃO está confirmado.\n5. O botão “Verificar gravação” repete apenas a conferência; não faz novo POST e não cria duplicidade.\n6. A mensagem “Preenchimento confirmado” só aparece depois de a planilha oficial conter a linha correspondente.\n\n## Contrato do verificador\n\nRequisição `POST text/plain`:\n\n```json\n{{\n  "protocol": "cats-persistence-v1",\n  "formEditId": "{FORM_EDIT_ID}",\n  "sheetId": "{SHEET_ID}",\n  "submittedAtEpochMs": 0,\n  "fingerprint": "sha256(...)"\n}}\n```\n\nResposta positiva:\n\n```json\n{{\n  "protocol": "cats-persistence-v1",\n  "persisted": true,\n  "formEditId": "{FORM_EDIT_ID}",\n  "sheetId": "{SHEET_ID}",\n  "fingerprint": "mesmo fingerprint"\n}}\n```\n\nO código de referência está em `apps-script/CATS_PersistenceVerifier.gs`. Ele também confere, via `FormApp.openById()`, se o Form oficial está efetivamente vinculado à planilha oficial antes de liberar qualquer resposta positiva.\n\n## Ativação positiva em produção\n\n1. Criar/deployar o Apps Script como Web App, executando como o proprietário e com acesso restrito ao necessário.\n2. Copiar a URL `/exec` do deployment.\n3. Preencher essa URL em `persistence-config.js`.\n4. Rodar `scripts/e2e_precurso.py` e o workflow `CATS Pré-curso — Smoke e E2E`.\n\nEnquanto `persistence-config.js` estiver vazio, o comportamento é deliberadamente fail-closed: o POST pode acontecer, mas a página não declara conclusão.\n\n## Gates\n\n- Smoke: IDs oficiais fixos, guard instalado, nenhum campo obrigatório sem `name`, nenhum `temp_`.\n- E2E negativo: `/formResponse` retorna HTTP 200, mas verificador aponta planilha errada → sucesso deve permanecer invisível.\n- E2E positivo: mesmo POST + confirmação com planilha/form/fingerprint corretos → sucesso visível e formulário oculto.\n''', encoding="utf-8")


def write_verifier() -> None:
    VERIFIER.parent.mkdir(parents=True, exist_ok=True)
    VERIFIER.write_text(r'''/**
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
''', encoding="utf-8")


def smoke() -> None:
    pre = PRE.read_text(encoding="utf-8")
    e2e = E2E.read_text(encoding="utf-8")
    wf = WORKFLOW.read_text(encoding="utf-8")
    assert FORM_EDIT_ID in pre
    assert SHEET_ID in pre
    assert "form.dataset.persistenceGuard='strict'" in pre
    assert "#success:not([data-persistence-confirmed=\"true\"])" in pre
    assert "isValidPersistenceConfirmation" in pre
    assert "Preenchimento confirmado" in pre
    assert "Envio concluído" not in pre
    assert "SHEET-ERRADA" in e2e
    assert "data-persistence-confirmed" in e2e
    assert "persistence-config.js" in wf


if __name__ == "__main__":
    patch_precurso()
    patch_e2e()
    patch_workflow()
    write_config()
    write_spec()
    write_verifier()
    smoke()
    print("PASS: hotfix de persistência aplicado e smoke estático aprovado")
