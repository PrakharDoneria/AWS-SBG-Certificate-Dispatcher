import { CREDENTIALS_KEY, readLists } from './storage.js';

async function renderExactPreview(file) {
  const form = new FormData();
  form.append('certificate', file);
  const response = await fetch('/api/preview-certificate', { method: 'POST', body: form });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error);
  document.getElementById('certificate-preview').innerHTML = `<img class="rendered-certificate" src="${data.image}" alt="Certificate rendered for Prakhar Doneria">`;
  document.getElementById('certificate-modal-image').src = data.image;
  return data.image;
}

export function initCompose() {
  const form = document.getElementById('compose-form');
  if (!form) return;
  const certificate = document.getElementById('certificate');
  const listSelect = document.getElementById('saved-list-select');
  const listInput = document.getElementById('list');
  const modal = document.getElementById('certificate-modal');
  let previewImage = '';

  certificate.addEventListener('change', async () => {
    if (!certificate.files[0]) return;
    try { previewImage = await renderExactPreview(certificate.files[0]); }
    catch (error) { document.getElementById('preview-result').textContent = error.message; }
  });

  listSelect.addEventListener('change', () => {
    if (listSelect.value) listInput.removeAttribute('required');
  });

  document.getElementById('preview-certificate').addEventListener('click', async () => {
    modal.setAttribute('aria-hidden', 'false');
    if (certificate.files[0] && !previewImage) previewImage = await renderExactPreview(certificate.files[0]);
    document.getElementById('preview-result').textContent = previewImage ? 'Rendered with certificate.py positioning.' : 'Upload a certificate template to generate the exact preview.';
  });
  modal.querySelectorAll('[data-close-modal]').forEach((element) => element.addEventListener('click', () => modal.setAttribute('aria-hidden', 'true')));

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const credentials = JSON.parse(localStorage.getItem(CREDENTIALS_KEY) || '{}');
    const data = new FormData(form);
    const selected = listSelect.value ? readLists()[Number(listSelect.value)] : null;
    if (selected) data.set('list', new File([selected.content], selected.name, { type: 'text/csv' }));
    data.set('sender_email', credentials.email || '');
    data.set('sender_password', credentials.password || '');
    data.set('sender_name', credentials.name || 'Prakhar Doneria');
    const result = document.getElementById('send-result');
    let progress = 8;
    result.innerHTML = `<span class="dispatch-spinner" aria-hidden="true"></span> Dispatching... ${progress}%`;
    const progressTimer = setInterval(() => {
      progress = Math.min(progress + 7, 92);
      result.innerHTML = `<span class="dispatch-spinner" aria-hidden="true"></span> Dispatching... ${progress}%`;
      document.title = `Dispatching... ${progress}% | SBG Dispatcher`;
    }, 700);
    try {
      const response = await fetch('/api/send', { method: 'POST', body: data });
      const responseData = await response.json();
      clearInterval(progressTimer);
      document.title = response.ok ? 'Dispatch complete | SBG Dispatcher' : 'Dispatch failed | SBG Dispatcher';
      result.textContent = response.ok ? `Sent ${responseData.sent} certificate${responseData.sent === 1 ? '' : 's'}.` : responseData.error;
    } catch { clearInterval(progressTimer); document.title = 'Dispatch failed | SBG Dispatcher'; result.textContent = 'Could not reach the dispatcher.'; }
  });
}