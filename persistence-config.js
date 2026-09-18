// CATS pré-curso — endpoint de verificação de persistência.
// FAIL-CLOSED: a interface só acusa preenchimento concluído após confirmação positiva deste verificador.
window.CATS_PERSISTENCE_VERIFY_URL = 'https://script.google.com/macros/s/AKfycbzOINm3ehG2ojEuSyFSYIuOfKciTGTg37GZ4lvC_AKfV0_00nU4GU8uxFwOpgefPTE/exec';

// Hotfix 2026-09-18: Google Forms -> Sheets pode ter consistência eventual.
// O verificador continua liberando sucesso assim que a linha aparece; este valor
// apenas amplia a janela máxima antes de declarar falta de confirmação.
window.__CATS_PERSISTENCE_VERIFY_TIMEOUT__ = 120000;
