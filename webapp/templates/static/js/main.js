// Basic hooks; real logic (ask, upload, reindex) arrives in steps 6–9.
document.addEventListener('DOMContentLoaded', () => {
  console.debug('RAG Console UI ready');

  document.querySelectorAll('header nav a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href').slice(1);
      const el = document.getElementById(id);
      if (el) {
        e.preventDefault();
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
});
