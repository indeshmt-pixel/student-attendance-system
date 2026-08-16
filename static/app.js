document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.querySelector('.sidebar');
  const menu = document.querySelector('.mobile-menu');
  if (menu && sidebar) {
    menu.addEventListener('click', () => sidebar.classList.toggle('open'));
  }

  const clock = document.querySelector('[data-clock]');
  const date = document.querySelector('[data-date]');

  function tick() {
    const now = new Date();
    if (clock) {
      clock.textContent = now.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    }
    if (date) {
      date.textContent = now.toLocaleDateString([], {
        weekday: 'short',
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      });
    }
  }
  tick();
  setInterval(tick, 1000);

  document.querySelectorAll('[data-counter]').forEach((el) => {
    const target = Number(el.dataset.counter || 0);
    let current = 0;
    const step = Math.max(1, Math.ceil(target / 25));
    function run() {
      current = Math.min(target, current + step);
      el.textContent = current;
      if (current < target) requestAnimationFrame(run);
    }
    run();
  });

  // Remove accidental spaces from email fields before the browser validates them.
  document.querySelectorAll('input[name="email"]').forEach((input) => {
    input.addEventListener('blur', () => {
      input.value = input.value.trim().toLowerCase();
    });
  });

  // PWA install support.
  let deferredInstallPrompt = null;
  const installButton = document.getElementById('installAppBtn');

  window.addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault();
    deferredInstallPrompt = event;
    if (installButton) installButton.hidden = false;
  });

  if (installButton) {
    installButton.addEventListener('click', async () => {
      if (!deferredInstallPrompt) return;
      deferredInstallPrompt.prompt();
      await deferredInstallPrompt.userChoice;
      deferredInstallPrompt = null;
      installButton.hidden = true;
    });
  }

  window.addEventListener('appinstalled', () => {
    if (installButton) installButton.hidden = true;
    deferredInstallPrompt = null;
  });

  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/sw.js').catch(() => {});
  }
});
