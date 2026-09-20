from pathlib import Path
import re

pre = Path('precurso.html').read_text(encoding='utf-8')
legacy = Path('legacy.html').read_text(encoding='utf-8')
persist = Path('persistence-config.js').read_text(encoding='utf-8')
verifier = Path('apps-script/CATS_PersistenceVerifier.gs').read_text(encoding='utf-8')
e2e = Path('scripts/e2e_precurso.py').read_text(encoding='utf-8')
lighthouse = Path('.github/workflows/lighthouse-production.yml').read_text(encoding='utf-8')
spec = Path('docs/PRECURSO_E2E_FINAL_SPEC.md').read_text(encoding='utf-8')

FORM_PUBLIC_ID = '1FAIpQLScVj6HESm2cWDN3sNQCaoNOtWSKini7NbSHgiTXemwlyvqAXg'
FORM_EDIT_ID = '1107fjdaiL42Zb0n2jNjKr0aiNNysyEADQCesdBTbD_E'
SHEET_ID = '1wQ0nc6TmCqqbu-ZqloIRLptO6iHqDhD00qrFLxP-fUk'

checks = []
def gate(name, ok, evidence):
    checks.append((name, bool(ok), evidence))

# 1 — Integridade funcional do formulário.
# O E2E atual não usa inspeção meramente lexical do action: intercepta de fato
# o POST /formResponse, captura o payload e confirma os mappings críticos.
gate(
    'Integridade funcional',
    FORM_PUBLIC_ID in pre
    and 'formResponse' in pre
    and 'entry.500885681' in pre
    and 'entry.327261555' in pre
    and 'page.route("**/formResponse", capture_form_response)' in e2e
    and 'assert captured' in e2e
    and 'payload.get("entry.500885681") == "Nunca atendi."' in e2e
    and 'all(name in payload for name in names)' in e2e,
    'Form oficial, mappings críticos, POST real interceptado e payload clínico completo.'
)

# 2 — Persistência e rastreabilidade.
gate(
    'Persistência e rastreabilidade',
    FORM_EDIT_ID in pre
    and SHEET_ID in pre
    and 'installPersistenceGuard' in pre
    and 'persistenceConfirmed' in pre
    and 'keepUnconfirmedVisible' in pre
    and 'CATS_PERSISTENCE_VERIFY_URL' in persist
    and 'SpreadsheetApp.openById' in verifier
    and "persisted: true" in verifier,
    'Sucesso depende da Sheet oficial, IDs pinados e fingerprint.'
)

# 3 — Segurança, privacidade e minimização.
sensitive_local = re.search(r'(localStorage|sessionStorage)\.setItem\([^\n]*(cpf|clinical|entry\.)', pre + legacy, re.I)
gate(
    'Segurança, privacidade e minimização',
    'noindex,nofollow,noarchive' in pre
    and 'autocomplete="off"' in legacy
    and "credentials: 'omit'" in persist
    and sensitive_local is None
    and 'Não retorna PII' in verifier
    and 'respostas clínicas' in verifier
    and 'storage_dump' in e2e
    and 'assert "entry.626004811" not in storage_dump' in e2e
    and 'assert "bdi" not in storage_dump.lower()' in e2e,
    'Sem cache local de respostas sensíveis; verifier não devolve PII/BDI-II; E2E inspeciona storages.'
)

# 4 — UX, acessibilidade e responsividade.
gate(
    'UX, acessibilidade e responsividade',
    'lang="pt-BR"' in pre
    and 'aria-live="polite"' in pre
    and 'prefers-reduced-motion' in pre
    and '@media(max-width:420px)' in pre
    and 'scrollWidth <= document.documentElement.clientWidth + 2' in e2e
    and 'getBoundingClientRect().height >= 44' in e2e
    and '"Envio realizado" in pending_text' in e2e
    and '"Preenchimento confirmado" in success_text' in e2e
    and '"Dados gravados na planilha oficial de respostas." in success_text' in e2e
    and 'radio.locator("xpath=..").click()' in e2e,
    'Idioma, live region, reduced motion, mobile, alvo de toque, escolha visível e feedback pós-envio cobertos.'
)

# 5 — Robustez operacional e regressão.
gate(
    'Robustez operacional e regressão',
    'MAX_AUTO_RETRIES' in persist
    and 'AUTO_RETRY_DELAY_MS' in persist
    and 'network-error' in persist
    and "submittedAtEpochMs: 0" in persist
    and 'SHEET-ERRADA' in e2e
    and 'data-persistence-confirmed' in e2e
    and 'assert captured' in e2e
    and 'positive ?' in e2e
    and "$('#success').classList.add('show');\n    window.scrollTo" not in legacy,
    'Retry automático, clock-skew neutralizado, POST observado e falso positivo bloqueado.'
)

# 6 — Prontidão de entrega e canal de e-mail.
# Este gate prova a preparação do produto; a ativação/autorização do projeto Apps
# Script em produção é uma evidência operacional externa e não é inferida do Git.
gate(
    'Prontidão de entrega',
    'notifyEmail:true' in pre
    and 'emailSubmittedResponse' in verifier
    and 'MailApp.sendEmail' in verifier
    and 'ricmurtapsicologia@gmail.com' in verifier
    and 'computeBdiIi_(headers, values)' in verifier
    and 'RESULTADO BDI-II — USO RESTRITO À COORDENAÇÃO' in verifier
    and 'precurso.html' in lighthouse
    and 'Lighthouse' in lighthouse
    and 'runtime de e-mail' in spec,
    'E-mail e BDI-II privado implementados no backend-fonte; ativação do runtime continua evidência externa.'
)

print('GATES_FINAIS_PRECURSO_6_6')
for i, (name, ok, evidence) in enumerate(checks, 1):
    print(f'{i}/6 {"PASS" if ok else "FAIL"} | {name} | {evidence}')

failed = [name for name, ok, _ in checks if not ok]
if failed:
    raise SystemExit('GATES_6_6_FAIL: ' + ', '.join(failed))
print('GATES_6_6_PASS')
