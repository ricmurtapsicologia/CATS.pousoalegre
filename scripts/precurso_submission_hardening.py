from pathlib import Path

LEGACY = Path('legacy.html')
PRECURSO = Path('precurso.html')

OLD_LEGACY = '''  $('#google-response').addEventListener('load', () => {
    if(!submitted) return;
    $('#catsForm').style.display = 'none';
    $('#success').classList.add('show');
    window.scrollTo({top: 0, behavior: 'smooth'});
  });'''

NEW_LEGACY = '''  $('#google-response').addEventListener('load', () => {
    if(!submitted) return;
    // O load do iframe confirma apenas que o Google respondeu ao POST.
    // Sucesso só pode ser exibido após confirmação independente da linha
    // materializada na planilha oficial, feita por precurso.html.
    $('#submitBtn').textContent = 'Confirmando gravação...';
  });'''

BUILD_OLD = '2026.09.18-r9-auto'
BUILD_NEW = '2026.09.18-r10-persist'
AUTH_JS_OLD = 'cats-auth.js?v=20260909-2'
AUTH_JS_NEW = 'cats-auth.js?v=20260918-submit-feedback-r1'


def patch_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f'Padrão não localizado: {label}')
    return text.replace(old, new, 1)


legacy = LEGACY.read_text(encoding='utf-8')
legacy = patch_once(legacy, OLD_LEGACY, NEW_LEGACY, 'legacy false-positive success')
LEGACY.write_text(legacy, encoding='utf-8')

pre = PRECURSO.read_text(encoding='utf-8')
pre = pre.replace(f'<meta name="cats-build" content="{BUILD_OLD}">', f'<meta name="cats-build" content="{BUILD_NEW}">')
pre = pre.replace(f'src="legacy.html?v={BUILD_OLD}"', f'src="legacy.html?v={BUILD_NEW}"')
pre = pre.replace(f"const BUILD='{BUILD_OLD}';", f"const BUILD='{BUILD_NEW}';")
pre = pre.replace(AUTH_JS_OLD, AUTH_JS_NEW)

payload_old = '''      sheetId:RESPONSE_SHEET_ID,
      submittedAtEpochMs,
      fingerprint:await sha256Hex(canonical)'''
payload_new = '''      sheetId:RESPONSE_SHEET_ID,
      submittedAtEpochMs,
      notifyEmail:true,
      fingerprint:await sha256Hex(canonical)'''
if payload_new not in pre:
    pre = patch_once(pre, payload_old, payload_new, 'notifyEmail persistence payload')

PRECURSO.write_text(pre, encoding='utf-8')

# Gates locais do hotfix: nenhuma confirmação visual baseada só em iframe-load.
check_legacy = LEGACY.read_text(encoding='utf-8')
check_pre = PRECURSO.read_text(encoding='utf-8')
assert "$('#success').classList.add('show');\n    window.scrollTo" not in check_legacy
assert "notifyEmail:true" in check_pre
assert 'legacy.html?v=' + BUILD_NEW in check_pre
assert AUTH_JS_NEW in check_pre
assert 'function installPersistenceGuard' in check_pre
assert 'responseFrame.addEventListener' in check_pre
print('PRECURSO_SUBMISSION_HARDENING_OK')
