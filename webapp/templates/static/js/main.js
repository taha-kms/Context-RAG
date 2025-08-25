document.addEventListener('DOMContentLoaded', () => {
  console.debug('RAG Console UI ready');

  // Smooth scroll for header anchors
  document.querySelectorAll('header nav a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href').slice(1);
      const el = document.getElementById(id);
      if (el) { e.preventDefault(); el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    });
  });

  // Disable submit button on forms and optional confirm
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', (e) => {
      const btn = form.querySelector('input[type="submit"], button[type="submit"]');
      if (btn && btn.dataset.confirm) {
        const ok = window.confirm(btn.dataset.confirm);
        if (!ok) { e.preventDefault(); return; }
      }
      if (btn) {
        btn.disabled = true;
        btn.dataset._originalText = btn.value || btn.textContent;
        if (btn.value !== undefined) btn.value = 'Working...';
        else btn.textContent = 'Working...';
      }
    });
  });
});
