from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
page = (ROOT / "index.html").read_text(encoding="utf-8")
auth = (ROOT / "cats-auth.js").read_text(encoding="utf-8")
auth_css = (ROOT / "cats-auth.css").read_text(encoding="utf-8")
portal_css = (ROOT / "portal-ui.css").read_text(encoding="utf-8")
portal_js = (ROOT / "portal-ui.js").read_text(encoding="utf-8")
pre = (ROOT / "precurso.html").read_text(encoding="utf-8")
legacy = (ROOT / "legacy.html").read_text(encoding="utf-8")
readme = (ROOT / "README.md").read_text(encoding="utf-8")

checks: list[tuple[str, bool]] = []
def add(name: str, condition: bool): checks.append((name, bool(condition)))

# 01–10 — identidade e fonte curricular
add("01 edição", "VIII CATS 2026" in page)
add("02 cidade", "Pouso Alegre" in page)
add("03 unidade", "7ª Cia Ind" in page)
add("04 período", "21–25/09/2026" in page)
add("05 carga", "46 h/a" in page)
add("06 coordenador", "Capitão BM Lucas Antônio de Oliveira" in page)
add("07 curso", "Curso de Atendimento a Tentativas de Suicídio" in page)
add("08 sem edição VII", not re.search(r'CATS\)? VII(?!I)', page))
add("09 sem JF/4BBM", "Juiz de Fora" not in page and "4º BBM" not in page)
add("10 fonte declarada", "Plano de Ensino CATS 2026" in readme and "QTS CATS 2026" in readme)

# 11–22 — malha completa de 12 unidades
for n in range(1, 13):
    add(f"{10+n:02d} unidade {n}", page.count(f'data-module="{n}"') == 1)

# 23–30 — unidades teóricas atuais
add("23 aspectos gerais", "Aspectos Gerais do Comportamento Suicida" in page)
add("24 psicopatologia", "Psicopatologia do Comportamento Suicida" in page)
add("25 abordagem geral", "Abordagem Técnica: Aspectos Gerais" in page)
add("26 abordagem específica", "Abordagem Técnica: Aspectos Específicos" in page)
add("27 comunicação", "Abordagem Técnica: Comunicação Dissuasiva" in page)
add("28 tática", "Abordagem Tática" in page)
add("29 gestão", "Gestão em ATS" in page)
add("30 prevenção unidade 12", 'data-module="12"' in page and "Prevenção ao comportamento suicida" in page)

# 31–40 — práticas, progresso, recursos e avaliação
add("31 prática conversação", "Prática de conversação em ATS" in page)
add("32 prática incêndio", "Risco de incêndio/explosão" in page)
add("33 prática precipitação", "Risco de precipitação" in page)
add("34 prática afogamento", "Risco de afogamento" in page)
add("35 progresso 12", "const TOTAL = 12" in page and "/12</span>" in page)
add("36 12 conclusões", page.count('class="btn small complete"') == 12)
add("37 podcast", "https://ricmurtapsicologia.github.io/Podcast-ATS-CBMMG/" in page)
add("38 biblioteca", "https://ricmurtapsicologia.github.io/Curso-ATS/" in page)
add("39 recursos fora do currículo", 'data-module="proj"' in page and 'data-module="biblioteca"' in page)
avaliacao = re.search(r'<section class="container" id="avaliacao".*?</section>', page, re.S)
add("40 avaliação sem link", bool(avaliacao) and '<a ' not in avaliacao.group(0))

# 41–50 — autenticação, privacidade e superfície de risco
add("41 sessão isolada", 'curso_ats_auth_v3: "cats_pa_auth_v1"' in auth)
add("42 tentativas isoladas", 'ats_login_attempts_v3: "cats_pa_login_attempts_v1"' in auth)
add("43 auth css canônico", "Curso-ATS/auth.css?v=20260905-2" in page)
add("44 auth js canônico", "Curso-ATS/auth.js?v=20260905-2" in page)
add("45 wrapper antes base", page.find("cats-auth.js?v=20260905-1") < page.find("Curso-ATS/auth.js?v=20260905-2"))
add("46 fail closed", "cats-auth-failed" in auth and "cats-auth-failed" in auth_css)
add("47 noindex", "noindex,nofollow,noarchive" in page)
add("48 sem credencial crua", all(x not in page for x in ("baseValidas", "novasMatriculas", "terapiadoesquema")))
add("49 sem Tawk", "embed.tawk.to" not in page and "Tawk.to" not in page)
add("50 precurso/legacy protegidos", "cats-auth.js?v=20260905-1" in pre and "data-cats-legacy-guard" in legacy)

# 51–60 — onboarding e ergonomia afetiva
add("51 boas-vindas", "Boas-vindas ao VIII CATS 2026" in page)
add("52 fala coordenador", "Seja bem-vindo(a) ao VIII Curso" in page)
add("53 assinatura coordenador", "Coordenador do VIII CATS 2026" in page)
add("54 texto justificado", "text-align:justify" in portal_css)
add("55 hifenização", "hyphens:auto" in portal_css)
add("56 onboarding rolável", "max-height:90dvh" in portal_css and "overflow:auto" in portal_css)
add("57 CTA afetivo", "Entrar na trilha" in page)
add("58 orientação sem excesso", page.count('class="onboard-list"') == 1)
add("59 mensagem de autonomia", "avance no seu ritmo" in page)
add("60 vínculo com segurança", "segurança das práticas" in page)

# 61–70 — mobile-first e ergonomia cognitiva
add("61 css mobile-first", "@media(min-width:761px)" in portal_css)
add("62 hero reduzido mobile", ".hero-card{display:none}" in portal_css)
add("63 info sob demanda", "courseInfoToggle" in page and 'id="mobileCoursePanel" hidden' in page)
add("64 cards compactos", ".course-card .content{display:none" in portal_css)
add("65 abertura por botão", "lesson-toggle" in portal_js and 'aria-expanded", "false"' in portal_js)
add("66 uma unidade por vez", "closeOtherCourseCards" in portal_js)
add("67 imagens teóricas ocultas mobile", ".course-card .media{display:none}" in portal_css)
add("68 ações empilhadas", ".course-card .actions{display:grid" in portal_css)
add("69 fabs removidos mobile", ".fab,.to-top{display:none}" in portal_css)
add("70 logout integrado", "moveLogoutIntoNav" in portal_js and "position:static!important" in portal_css)

# 71–80 — navegabilidade, cascatas e acessibilidade
add("71 menu mobile", 'id="mobileMenuBtn"' in page and 'aria-controls="mainNavLinks"' in page)
add("72 menu fechado inicial", ".nav-links{display:none" in portal_css)
add("73 materiais por botão", 'aria-controls="materialsPanel"' in page and 'id="materialsPanel" hidden' in page)
add("74 vídeos por botão", 'id="videosToggle"' in page and 'id="videosGrid" hidden' in page)
add("75 avaliação por botão", 'aria-controls="assessmentPanel"' in page and 'id="assessmentPanel" hidden' in page)
add("76 sem details antigo", '<details class="materials">' not in page)
add("77 skip link", 'class="skip-link"' in page and 'id="conteudo"' in page)
add("78 diálogos rotulados", 'aria-labelledby="modalTitle"' in page and 'aria-labelledby="slidesTitle"' in page)
add("79 live region", 'aria-live="polite"' in page)
add("80 reduced motion", "prefers-reduced-motion:reduce" in portal_css and "prefers-reduced-motion:reduce" in auth_css)

# 81–90 — manutenção, coerência editorial e publicação
add("81 release r3", 'content="viii-cats-pa-2026-r3"' in page)
add("82 progresso v2", "cats_pa_progress_v2" in page)
add("83 onboarding v2", "cats_pa_onboarded_v2" in page)
add("84 css experiência", "portal-ui.css?v=20260905-1" in page)
add("85 js experiência", "portal-ui.js?v=20260905-1" in page)
add("86 README 12 unidades", "12 unidades formativas" in readme)
add("87 README práticas", all(x in readme for x in ("conversação", "incêndio/explosão", "precipitação", "afogamento")))
add("88 links não vazios", 'href=""' not in page and 'src=""' not in page)
add("89 sem linguagem manutenção", "Em manutenção" not in page)
add("90 fechamento HTML", page.rstrip().endswith("</html>"))

assert len(checks) == 90, len(checks)
failed = [name for name, ok in checks if not ok]
for name, ok in checks:
    print(f"{'PASS' if ok else 'FAIL'} — {name}")
if failed:
    raise SystemExit("Auditoria 90/90 falhou: " + ", ".join(failed))
print("PASS: Auditoria 90/90 — 90 de 90 critérios aprovados.")
