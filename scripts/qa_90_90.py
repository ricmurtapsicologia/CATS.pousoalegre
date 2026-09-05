from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
page = (ROOT / "index.html").read_text(encoding="utf-8")
auth = (ROOT / "cats-auth.js").read_text(encoding="utf-8")
auth_css = (ROOT / "cats-auth.css").read_text(encoding="utf-8")
pre = (ROOT / "precurso.html").read_text(encoding="utf-8")
legacy = (ROOT / "legacy.html").read_text(encoding="utf-8")
readme = (ROOT / "README.md").read_text(encoding="utf-8")

checks: list[tuple[str, bool]] = []
def add(name: str, condition: bool): checks.append((name, bool(condition)))

# 01–10 — identidade e informação
add("01 edição correta", "VIII CATS 2026" in page)
add("02 cidade correta", "Pouso Alegre" in page)
add("03 unidade local", "7ª Cia Ind" in page)
add("04 período", "21–25/09/2026" in page)
add("05 carga horária", "46 h/a" in page)
add("06 coordenador", "Capitão BM Lucas Antônio de Oliveira" in page)
add("07 título institucional", "Curso de Atendimento a Tentativas de Suicídio" in page)
add("08 sem edição antiga", "CATS VII" not in page)
add("09 sem local antigo", "Juiz de Fora" not in page)
add("10 ano de copyright", "© 2026" in page)

# 11–20 — oito módulos preservados
for n in range(1, 9): add(f"{10+n:02d} módulo {n} presente", page.count(f'data-module="{n}"') == 1)
add("19 oito ações de conclusão", page.count("Concluir módulo") == 8)
add("20 termômetro em oito módulos", "const TOTAL = 8" in page)

# 21–30 — aulas e extras
add("21 módulo 1", "Aspectos Gerais do Comportamento Suicida" in page)
add("22 módulo 2", "Psicopatologia do Comportamento Suicida" in page)
add("23 módulo 3", "Abordagem Técnica: Aspectos Gerais" in page)
add("24 módulo 4", "Abordagem Técnica: Aspectos Específicos" in page)
add("25 módulo 5", "Abordagem Técnica: Comunicação Dissuasiva" in page)
add("26 módulo 6", "Abordagem Tática" in page)
add("27 módulo 7", "Gestão em ATS" in page)
add("28 módulo 8", "Prevenção" in page)
add("29 podcast preservado", "https://ricmurtapsicologia.github.io/Podcast-ATS-CBMMG/" in page)
add("30 biblioteca adicionada", "https://ricmurtapsicologia.github.io/Curso-ATS/" in page)

# 31–40 — autenticação
add("31 sessão CATS isolada", 'curso_ats_auth_v3: "cats_pa_auth_v1"' in auth)
add("32 tentativas CATS isoladas", 'ats_login_attempts_v3: "cats_pa_login_attempts_v1"' in auth)
add("33 base canônica css", "Curso-ATS/auth.css?v=20260905-2" in page)
add("34 base canônica js", "Curso-ATS/auth.js?v=20260905-2" in page)
add("35 wrapper antes da base", page.find("cats-auth.js?v=20260905-1") < page.find("Curso-ATS/auth.js?v=20260905-2"))
add("36 sem botão de entrada", 'querySelector("#catsAuthSubmit")?.remove()' in auth)
add("37 matrícula 7", "length === 7" in auth)
add("38 CPF 11", "length === 11" in auth)
add("39 fail closed", "cats-auth-failed" in auth and "cats-auth-failed" in auth_css)
add("40 conteúdo pendente oculto", "cats-auth-pending" in page and "cats-auth-pending" in auth_css)

# 41–50 — segurança e privacidade
add("41 noindex", "noindex,nofollow,noarchive" in page)
add("42 sem lista crua de matrículas", "baseValidas" not in page)
add("43 sem lista nova de matrículas", "novasMatriculas" not in page)
add("44 sem credencial textual legada", "terapiadoesquema" not in page)
add("45 sem chat tawk", "embed.tawk.to" not in page)
add("46 sem tawk comentário", "Tawk.to" not in page)
add("47 sessão não em localStorage", "cats_pa_auth_v1" in auth and "sessionStorage" not in auth)
add("48 precurso protegido", "cats-auth.js?v=20260905-1" in pre)
add("49 legacy guard", "data-cats-legacy-guard" in legacy)
add("50 avaliação sem URL inventada", "A avaliação será disponibilizada" in page and "URL oficial" in page)

# 51–60 — acessibilidade
add("51 idioma", 'lang="pt-BR"' in page)
add("52 skip link", 'class="skip-link"' in page)
add("53 destino skip", 'id="conteudo"' in page)
add("54 foco skip", ".skip-link:focus" in page)
add("55 modal aria", 'aria-labelledby="modalTitle"' in page)
add("56 viewer aria", 'aria-labelledby="slidesTitle"' in page)
add("57 toast live", 'aria-live="polite"' in page)
add("58 imagens com alt", page.count('<img ') == page.count(' alt='))
add("59 reduced motion auth", "prefers-reduced-motion:reduce" in auth_css)
add("60 botão fechar com aria", 'aria-label="Fechar"' in page)

# 61–70 — responsividade e UX
add("61 viewport", 'name="viewport"' in page)
add("62 media queries", page.count("@media") >= 3)
add("63 grid responsiva", "grid-template-columns" in page)
add("64 tema persistente", "localStorage.getItem('theme')" in page)
add("65 progresso isolado", "cats_pa_progress_v1" in page)
add("66 onboarding isolado", "cats_pa_onboarded" in page)
add("67 navegação aulas", 'href="#aulas"' in page)
add("68 navegação materiais", 'href="#materiais"' in page)
add("69 navegação pré-curso", 'href="precurso.html"' in page)
add("70 navegação biblioteca", 'href="#recursos"' in page)

# 71–80 — integridade e manutenção
add("71 release meta", 'name="cats-release"' in page)
add("72 release valor", "viii-cats-pa-2026-r1" in page)
add("73 README edição", "VIII CATS 2026" in readme)
add("74 README coordenação", "Lucas Antônio de Oliveira" in readme)
add("75 README autenticação", "mesma base canônica" in readme)
add("76 pré-curso existe", (ROOT / "precurso.html").exists())
add("77 legacy existe", (ROOT / "legacy.html").exists())
add("78 auth js existe", (ROOT / "cats-auth.js").exists())
add("79 auth css existe", (ROOT / "cats-auth.css").exists())
add("80 links sem vazio", 'href=""' not in page and 'src=""' not in page)

# 81–90 — editorial, coerência e gate da prova
add("81 coordenador em campo dedicado", 'class="coordination-card"' in page)
add("82 rótulo coordenação", "Coordenação do VIII CATS 2026" in page)
add("83 recursos sem alterar contador", 'data-module="biblioteca"' in page and "const TOTAL = 8" in page)
add("84 podcast fora do contador", 'data-module="proj"' in page)
add("85 biblioteca fora do contador", 'data-module="biblioteca"' in page)
add("86 pré-curso no material", "Levantamento pré-curso e dados da turma" in page)
add("87 avaliação em seção própria", 'id="avaliacao"' in page)
add("88 avaliação não possui href", not re.search(r'id="avaliacao".*?<a\b', page, re.S))
add("89 sem linguagem de bastidor no acesso", "validado automaticamente" not in auth and "prompt" not in page.lower())
add("90 fechamento HTML", page.rstrip().endswith("</html>"))

assert len(checks) == 90, len(checks)
failed = [name for name, ok in checks if not ok]
for name, ok in checks:
    print(f"{'PASS' if ok else 'FAIL'} — {name}")
if failed:
    raise SystemExit("Auditoria 90/90 falhou: " + ", ".join(failed))
print("PASS: Auditoria 90/90 — 90 de 90 critérios aprovados.")
