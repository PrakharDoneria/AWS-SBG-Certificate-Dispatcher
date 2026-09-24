import { CREDENTIALS_KEY, GATE_KEY } from './storage.js';

const protectedPaths = ['/sbg-admin/dashboard', '/compose/new', '/sbg-admin/lists'];

export function initAuth() {
  if (window.location.pathname === '/sbg-admin' && localStorage.getItem(GATE_KEY) === 'true') {
    window.location.href = '/sbg-admin/dashboard';
    return;
  }
  if (protectedPaths.includes(window.location.pathname) && !localStorage.getItem(CREDENTIALS_KEY)) {
    window.location.href = '/sbg-admin/login';
  }

  const gate = document.getElementById('gate-form');
  gate?.addEventListener('submit', (event) => {
    event.preventDefault();
    const error = document.getElementById('gate-error');
    if (document.getElementById('gate-password').value === 'aws-sbgl-certs') {
      localStorage.setItem(GATE_KEY, 'true');
      window.location.href = '/sbg-admin/login';
    } else {
      error.textContent = 'That key does not match.';
    }
  });

  const login = document.getElementById('login-form');
  login?.addEventListener('submit', (event) => {
    event.preventDefault();
    localStorage.setItem(CREDENTIALS_KEY, JSON.stringify(Object.fromEntries(new FormData(login))));
    window.location.href = '/sbg-admin/dashboard';
  });

  document.getElementById('logout')?.addEventListener('click', () => {
    localStorage.removeItem(CREDENTIALS_KEY);
    window.location.href = '/sbg-admin';
  });
}