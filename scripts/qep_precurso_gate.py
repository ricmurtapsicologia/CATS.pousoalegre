from pathlib import Path
import re

pre = Path('precurso.html').read_text(encoding='utf-8')
legacy = Path('legacy.html').read_text(encoding='utf-8')
persist = Path('persistence-config.js').read_text(encoding='utf-8')
verifier = Path('apps-script/CATS_PersistenceVerifier.gs').read_text(encoding='utf-8')
workflow = Path('.github/workflows/precurso-smoke-e2e.yml').read_text(encoding='utf-8')

# O QEP canônico possui 24 dimensões / 397 slots. A redação literal histórica
# de todos os 397 subitens não está disponível; portanto este gate NÃO inventa
# critérios. Ele cruza as 24 dimensões recuperadas com evidências objetivas da
# superfície de pré-curso e falha nos controles críticos aplicáveis.

checks = []
def q(dim, name, ok, detail):
    checks.append((dim, name, bool(ok), detail))

q(1, 'Integridade editorial e conteúdo', 'VIII CATS 2026' in pre and 'CATS' in legacy, 'identidade/escopo presentes')
q(2, 'Arquitetura da informação', 'data-step="1"' in legacy and 'data-step="2"' in legacy and 'data-step="3"' in legacy, 'fluxo em três etapas')
q(3, 'Qualidade textual', 'Envio concluído' in pre and 'planilha oficial' in pre, 'mensagens operacionais explícitas')
q(4, 'Hierarquia visual', '<h1>' in legacy and '<h2>' in legacy, 'hierarquia semântica básica')
q(5, 'Tipografia e microtipografia', 'font-family' in pre and 'font-family' in legacy, 'pilha tipográfica definida')
q(6, 'Grid, composição e editoração', '@media(max-width:720px)' in legacy, 'grid responsivo')
q(7, 'Direção de arte e identidade visual', '--cats-navy' in pre and '--cats-gold' in pre, 'tokens institucionais')
q(8, 'Capa/hero', 'hero-card' in pre and 'hero-copy' in pre, 'hero identificado')
q(9, 'UX e navegação', 'progressBar' in legacy and 'data-next' in legacy and 'data-prev' in legacy, 'progresso e navegação')
q(10, 'Experiência pedagógica', 'Habilidades prévias' in legacy and 'Levantamento clínico' in legacy, 'sequenciamento de contexto')
q(11, 'Metodologia ativa/formulário', 'required' in legacy and 'validateCurrent' in legacy, 'validação antes do envio')
q(12, 'Multimídia', True, 'não crítica para formulário de pré-curso')
q(13, 'Acessibilidade', 'lang="pt-BR"' in pre and 'aria-live="polite"' in pre and 'prefers-reduced-motion' in pre, 'idioma, live region e reduced motion')
q(14, 'Responsividade e compatibilidade', 'viewport-fit=cover' in pre and '@media(max-width:420px)' in pre, 'mobile explícito')
q(15, 'Performance técnica', 'persistence-config.js' in pre and 'defer src=' in pre, 'carregamento controlado')
q(16, 'Integridade funcional', 'formResponse' in pre and 'installPersistenceGuard' in pre and 'CATS_PERSISTENCE_VERIFY_URL' in persist, 'POST + confirmação independente')
q(17, 'Documento estático', True, 'N/A funcional; formulário web')
q(18, 'EPUB', True, 'N/A; formulário web')
q(19, 'Interatividade documental', True, 'N/A; formulário web')
q(20, 'Segurança e privacidade', 'noindex,nofollow,noarchive' in pre and 'autocomplete="off"' in legacy and 'credentials: \'omit\'' in persist, 'não indexação, CPF sem autocomplete, verifier sem credenciais')
q(21, 'Metadados e SEO editorial', '<link rel="canonical"' in pre and 'og:title' in pre and 'twitter:card' in pre, 'metadados completos embora noindex')
q(22, 'Robustez e QA técnico', 'e2e_precurso.py' in workflow and 'Smoke de produção' in workflow, 'E2E local + smoke de produção')
q(23, 'Excelência editorial', 'Confirmação segura' in pre or 'Aguardando confirmação' in pre, 'estado operacional informado')
q(24, 'Consistência cross-format', 'FORM_ACTION' in pre and 'FORM_ID' in verifier and 'sheetId' in verifier, 'IDs oficiais rastreáveis')

# Controles transversais críticos específicos desta superfície.
critical = {
    'sem falso positivo por iframe': "$('#success').classList.add('show');\n    window.scrollTo" not in legacy,
    'mapeamento ocorrência': "entry.500885681" in pre,
    'mapeamento irritabilidade': "entry.327261555" in pre,
    'form oficial': '1FAIpQLScVj6HESm2cWDN3sNQCaoNOtWSKini7NbSHgiTXemwlyvqAXg' in pre,
    'sheet oficial': '1wQ0nc6TmCqqbu-ZqloIRLptO6iHqDhD00qrFLxP-fUk' in pre,
    'verificação fail-closed': 'persistenceConfirmed' in pre and 'keepUnconfirmedVisible' in pre,
    'e-mail solicitado no protocolo': 'notifyEmail:true' in pre,
    'backend com rotina de e-mail': 'emailSubmittedResponse' in verifier and 'MailApp.sendEmail' in verifier,
    'sem armazenamento local de respostas clínicas': not re.search(r'(localStorage|sessionStorage)\.setItem\([^\n]*(cpf|clinical|entry\.)', pre + legacy, re.I),
}

failed = [(d,n,detail) for d,n,ok,detail in checks if not ok]
crit_failed = [name for name,ok in critical.items() if not ok]

print('QEP_PRECURSO_CROSSWALK')
print('CANON=24 dimensões / 397 slots; subitens literais ausentes não foram inventados')
for dim, name, ok, detail in checks:
    print(f'D{dim:02d}={"PASS" if ok else "FAIL"} | {name} | {detail}')
for name, ok in critical.items():
    print(f'CRITICAL={"PASS" if ok else "FAIL"} | {name}')

if failed or crit_failed:
    raise SystemExit(f'QEP_PRECURSO_FAIL dimensions={len(failed)} critical={len(crit_failed)}')
print('QEP_PRECURSO_PASS')
