from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
original = s

s = s.replace('content="viii-cats-pa-2026-r4"', 'content="viii-cats-pa-2026-r5"', 1)
s = s.replace('<h3 id="ob-title">Boas-vindas ao VIII CATS 2026</h3>', '<h3 id="ob-title">Caros(as) abordadores(as),</h3>', 1)

old_welcome = '''<div class="onboard-welcome">
        <p>Seja bem-vindo(a) ao VIII Curso de Atendimento a Tentativas de Suicídio. Este ambiente foi organizado para apoiar sua aprendizagem sem substituir a experiência presencial e a orientação dos instrutores.</p>
        <p>Ao longo da semana, avance no seu ritmo pela trilha, consulte somente o que precisar e use os materiais como apoio para transformar conhecimento em atuação técnica, segura e humanizada.</p>
        <span class="onboard-signature">Capitão BM Lucas Antônio de Oliveira<br>Coordenador do VIII CATS 2026</span>
      </div>'''
new_welcome = '''<div class="onboard-welcome">
        <p>Esta página reúne as aulas, os objetivos e os materiais de apoio do VIII Curso de Atendimento a Tentativas de Suicídio (CATS 2026), em Pouso Alegre. Use este ambiente como apoio à formação presencial e às orientações dos instrutores.</p>
        <p>A referência normativa primária é a ITO 30 em vigor. Conteúdos provenientes da minuta canônica mais recente da revisão da ITO 30 são utilizados somente como complemento, quando compatíveis com a norma vigente.</p>
        <span class="onboard-signature">Capitão BM Lucas Antônio de Oliveira<br>Coordenador do VIII CATS 2026</span>
      </div>'''
if old_welcome not in s:
    raise SystemExit('Bloco original do onboarding não localizado.')
s = s.replace(old_welcome, new_welcome, 1)

old_js = '''    /* ===== Splash ===== */
    window.addEventListener('load', ()=>{
      const splash = document.getElementById('splash');
      const end = ()=> splash && (splash.style.display='none');
      const fast = setTimeout(end, 800);
      setTimeout(()=>{ clearTimeout(fast); end(); onboarding(); }, 4000);
    });
    function onboarding(){
      if(!localStorage.getItem('cats_pa_onboarded_v2')){
        const ob = document.getElementById('onboard');
        const close = ()=>{ ob.style.display='none'; localStorage.setItem('cats_pa_onboarded_v2','1'); }
        ob.style.display='grid';
        document.getElementById('ob-skip').addEventListener('click', close);
        document.getElementById('ob-next').addEventListener('click', close);
      }
    }
'''
new_js = '''    /* ===== Splash + onboarding ===== */
    window.addEventListener('load', ()=>{
      const splash = document.getElementById('splash');
      setTimeout(()=>{
        if(splash) splash.style.display='none';
        onboarding();
      }, 800);
    });
    function onboarding(){
      const ob = document.getElementById('onboard');
      if(!ob) return;
      const skip = document.getElementById('ob-skip');
      const next = document.getElementById('ob-next');
      const close = ()=>{ ob.style.display='none'; document.body.style.overflow=''; };
      ob.style.display='grid';
      document.body.style.overflow='hidden';
      if(skip) skip.onclick = close;
      if(next){ next.onclick = close; setTimeout(()=>next.focus(), 0); }
    }
'''
if old_js not in s:
    raise SystemExit('Bloco original do JS de onboarding não localizado.')
s = s.replace(old_js, new_js, 1)

old_contact = '''      <div>
        <h4>Contato</h4>
        <p><strong>Email:</strong> <a href="mailto:richelmy.pinto@bombeiros.mg.gov.br">richelmy.pinto@bombeiros.mg.gov.br</a></p>
        <p><strong>Telefone:</strong> <a href="tel:+5535984640729">(35) 98464-0729</a></p>
      </div>'''
new_contact = '''      <div>
        <h4>Coordenação e contato</h4>
        <p><strong>Coordenador:</strong> Capitão BM Lucas Antônio de Oliveira</p>
        <p><strong>Email:</strong> <a href="mailto:lucas.oliveira@bombeiros.mg.gov.br">lucas.oliveira@bombeiros.mg.gov.br</a></p>
        <p><strong>Celular:</strong> <a href="tel:+5535997443464">(35) 99744-3464</a></p>
      </div>'''
if old_contact not in s:
    raise SystemExit('Bloco original de contato não localizado.')
s = s.replace(old_contact, new_contact, 1)

s = s.replace('Tenho%20uma%20dúvida%20sobre%20o%20CATS%202025.', 'Tenho%20uma%20dúvida%20sobre%20o%20VIII%20CATS%202026.', 1)

required = [
    '<body>', '</body>', '<main id="main">', '<footer id="contatos">',
    'Caros(as) abordadores(as),', 'lucas.oliveira@bombeiros.mg.gov.br',
    '(35) 99744-3464', 'wa.me/5535984640729', 'function onboarding()',
    'VIII CATS 2026'
]
missing = [item for item in required if item not in s]
if missing:
    raise SystemExit('Falha estrutural após patch: ' + repr(missing))
if len(s) < 150000:
    raise SystemExit(f'Arquivo possivelmente truncado: {len(s)} bytes.')
if s.count('<style>') != s.count('</style>'):
    raise SystemExit('Tags style desbalanceadas.')
if s.count('<script') != s.count('</script>'):
    raise SystemExit('Tags script desbalanceadas.')
if original == s:
    raise SystemExit('Nenhuma alteração aplicada.')

p.write_text(s, encoding='utf-8')
print(f'OK: {len(s)} bytes; onboarding e contato atualizados.')
