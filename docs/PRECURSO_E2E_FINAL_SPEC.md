# VIII CATS Pouso Alegre — Pré-curso E2E final

## AS-IS

Fluxo atual: `precurso.html` prepara `legacy.html`, normaliza os nomes `entry.*`, faz POST no endpoint oficial `formResponse` do Google Forms em iframe oculto e, de forma independente, consulta um Web App Apps Script para confirmar que a resposta apareceu na planilha oficial.

A planilha oficial é `1wQ0nc6TmCqqbu-ZqloIRLptO6iHqDhD00qrFLxP-fUk`, aba `Respostas ao formulário 1`. O formulário público usa o ID `1FAIpQLScVj6HESm2cWDN3sNQCaoNOtWSKini7NbSHgiTXemwlyvqAXg` e o Form edit ID pinado no verificador é `1107fjdaiL42Zb0n2jNjKr0aiNNysyEADQCesdBTbD_E`.

O verificador não retorna CPF nem respostas clínicas. A identidade da submissão é confirmada por fingerprint SHA-256 de nome + e-mail + CPF + data, comparada à linha já persistida.

## PINPOINT

1. `legacy.html` ainda possuía sucesso visual acionado apenas pelo `load` do iframe do Google. Isso é falso positivo: load comprova resposta HTTP/navegação do iframe, não persistência na Sheet.
2. A confirmação independente já existe, mas precisa ser a única fonte de verdade para o estado final da interface.
3. O cliente deve repetir a confirmação automaticamente quando a materialização Forms → Sheets atrasar; o participante não deve clicar em “verificar”.
4. A rotina de e-mail existe no Apps Script, porém historicamente dependia de gatilho instalável `onFormSubmit`. Fonte no GitHub, sozinha, não prova que o gatilho está instalado no projeto Apps Script em produção.
5. O gate global do portal ficou bloqueado por um diálogo de consentimento de analytics que intercepta o clique do teste de onboarding; isso é independente da persistência do pré-curso e deve ser tratado no harness E2E.
6. O E2E do formulário deve interceptar o POST para não inserir respostas clínicas sintéticas em produção. Persistência real é verificada pelo Web App contra fixture histórica conhecida e por evidência da planilha oficial.

## TARGET / HOTFIX

### Envio

- Um único clique em “Enviar formulário”.
- POST automático ao `formResponse` oficial.
- Todos os obrigatórios possuem `name=entry.*` válido antes do envio.
- `entry.500885681` e `entry.327261555` permanecem mapeados explicitamente.

### Persistência

- Nunca mostrar sucesso por `iframe.load`.
- Após o POST, estado “confirmando gravação”.
- Verificar a Sheet automaticamente pelo Web App.
- Repetir automaticamente em caso de consistência eventual/rede transitória.
- Só ocultar o formulário e exibir “Preenchimento confirmado” após `persisted=true` com `formEditId`, `sheetId` e fingerprint correspondentes.

### E-mail

- A notificação ao coordenador só pode partir de uma resposta já persistida.
- Destino: `ricmurtapsicologia@gmail.com`.
- O mecanismo deve ser idempotente para não duplicar mensagens.
- O e-mail pode conter a resposta integral; a API pública de verificação não pode retornar PII ou respostas clínicas.
- O envio via Apps Script requer autorização do projeto publicado. O gate distingue “código presente” de “runtime de e-mail comprovado”.

### Privacidade

- Não persistir CPF ou respostas clínicas em `localStorage`/`sessionStorage`.
- Não expor conteúdo clínico no endpoint de verificação.
- Manter `noindex,nofollow,noarchive`.

## CRITÉRIOS DE ACEITE

1. POST oficial intacto e mapeamentos completos.
2. Zero falso positivo baseado em iframe.
3. Confirmação automática sem ação humana.
4. Verificador live: fingerprint inexistente → negativo; fixture persistida → positivo.
5. 30/30 aprovado.
6. 90/90 aprovado.
7. 6/6 aprovado.
8. QEP: 24 dimensões / 397 slots canônicos, sem inventar redação histórica ausente; controles críticos aplicáveis aprovados.
9. E2E dedicado do pré-curso aprovado em Chromium/mobile.
10. Lighthouse em produção executado para `/precurso.html`, com resultados registrados.
11. GitHub Pages publicado somente após os gates de código aplicáveis.
12. O runtime de e-mail só será declarado “comprovado” se houver evidência de gatilho/execução no Apps Script ou mensagem efetivamente recebida; a presença do código não basta.

## 6 GATES FINAIS

1. Integridade funcional do formulário.
2. Persistência e rastreabilidade Forms → Sheet.
3. Segurança, privacidade e minimização de exposição.
4. UX, acessibilidade e responsividade.
5. Robustez operacional, regressão e performance.
6. Prontidão de entrega: CI/E2E/Lighthouse e estado verificável do canal de e-mail.
