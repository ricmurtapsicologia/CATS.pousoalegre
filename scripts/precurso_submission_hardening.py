from pathlib import Path

LEGACY = Path('legacy.html').read_text(encoding='utf-8')
PRECURSO = Path('precurso.html').read_text(encoding='utf-8')

errors: list[str] = []

def require(ok: bool, message: str) -> None:
    if not ok:
        errors.append(message)

# Somente validação: o estado correto deve estar versionado antes do CI.
require("$('#success').classList.add('show');\n    window.scrollTo" not in LEGACY,
        'legacy.html voltou a considerar iframe-load como confirmação final')
require("cpfField.value = cpfField.value.replace(/\\D/g, '').slice(0, 11);" in LEGACY,
        'CPF não é canonicalizado para 11 dígitos antes do POST')
require("$('#submitBtn').textContent = 'Confirmando gravação...';" in LEGACY,
        'estado intermediário de confirmação ausente')

require('notifyEmail:true' in PRECURSO,
        'payload de persistência perdeu o contrato notifyEmail')
require("function installPersistenceGuard" in PRECURSO,
        'guard de persistência ausente')
require("responseFrame.addEventListener('load'" in PRECURSO,
        'gatilho de verificação após resposta do Forms ausente')
require("cpfDigits(form.elements['entry.426148251']?.value)" in PRECURSO,
        'fingerprint não canonicaliza CPF')
require("success.dataset.persistenceConfirmed='true'" in PRECURSO,
        'confirmação positiva não está vinculada ao estado persistido')
require("#success:not([data-persistence-confirmed=\"true\"]){display:none!important}" in PRECURSO,
        'fail-closed visual da confirmação ausente')
require("OFFICIAL_FORM_EDIT_ID='1107fjdaiL42Zb0n2jNjKr0aiNNysyEADQCesdBTbD_E'" in PRECURSO,
        'formulário oficial divergente')
require("RESPONSE_SHEET_ID='1wQ0nc6TmCqqbu-ZqloIRLptO6iHqDhD00qrFLxP-fUk'" in PRECURSO,
        'planilha oficial divergente')

if errors:
    raise SystemExit('PRECURSO_HARDENING_DRIFT_FAIL:\n- ' + '\n- '.join(errors))

print('PRECURSO_HARDENING_DRIFT_PASS: estado canônico já versionado; nenhuma mutação executada.')
