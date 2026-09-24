import { CREDENTIALS_KEY, readLists } from './storage.js';

const RESUME_KEY = 'sbg-dispatch-resume';

function dataUrlToFile(dataUrl, name) {
  const [header, encoded] = dataUrl.split(',');
  const mime = header.match(/data:(.*?);base64/)[1];
  const bytes = Uint8Array.from(atob(encoded), character => character.charCodeAt(0));
  return new File([bytes], name, { type: mime });
}

function fileToDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

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
  const result = document.getElementById('send-result');
  const resumeButton = document.getElementById('resume-dispatch');
  let previewImage = '';
  let resumeState = null;
  let savedResumeState = null;

  function loadResumeState() {
    try { savedResumeState = JSON.parse(localStorage.getItem(RESUME_KEY) || 'null'); }
    catch { savedResumeState = null; }
    resumeButton.hidden = !savedResumeState;
  }

  loadResumeState();

  resumeButton.addEventListener('click', () => {
    if (!savedResumeState) return;
    resumeState = savedResumeState;
    document.querySelector('[name="subject"]').value = resumeState.subject;
    document.querySelector('[name="event_name"]').value = resumeState.eventName;
    document.querySelector('[name="body"]').value = resumeState.body;
    result.textContent = 'Saved recipients loaded. Send to continue the interrupted dispatch.';
  });

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
    if (resumeState) {
      data.set('list', new File([resumeState.remainingCsv], 'remaining-recipients.csv', { type: 'text/csv' }));
      data.set('certificate', dataUrlToFile(resumeState.certificateDataUrl, resumeState.certificateName));
    }
    data.set('sender_email', credentials.email || '');
    data.set('sender_password', credentials.password || '');
    data.set('sender_name', credentials.name || 'Prakhar Doneria');
    result.innerHTML = '<span class="dispatch-spinner" aria-hidden="true"></span> Sending certificates...';
    document.title = 'Sending certificates | SBG Dispatcher';
    try {
      const response = await fetch('/api/send', { method: 'POST', body: data });
      let responseData;
      try {
        responseData = await response.json();
      } catch {
        throw new Error(`The dispatcher returned an invalid response (HTTP ${response.status}).`);
      }
      document.title = response.ok ? 'Dispatch complete | SBG Dispatcher' : 'Dispatch failed | SBG Dispatcher';
      if (response.ok && responseData.interrupted) {
        const certificateFile = data.get('certificate');
        if (!(certificateFile instanceof File)) throw new Error('The certificate file was unavailable while saving the resume state.');
        localStorage.setItem(RESUME_KEY, JSON.stringify({
          remainingCsv: responseData.remaining_csv,
          certificateDataUrl: await fileToDataUrl(certificateFile),
          certificateName: certificateFile.name,
          subject: data.get('subject'),
          eventName: data.get('event_name'),
          body: data.get('body'),
        }));
        resumeState = JSON.parse(localStorage.getItem(RESUME_KEY));
        resumeButton.hidden = false;
        result.textContent = `${responseData.message} ${responseData.sent} sent. The remaining recipients are saved in this browser.`;
      } else if (response.ok) {
        localStorage.removeItem(RESUME_KEY);
        resumeState = null;
        resumeButton.hidden = true;
        result.textContent = `Sent ${responseData.sent} of ${responseData.total} certificate${responseData.total === 1 ? '' : 's'} (100%).`;
      } else {
        throw new Error(responseData.error || `The dispatcher returned HTTP ${response.status}.`);
      }
    } catch (error) {
      document.title = 'Dispatch failed | SBG Dispatcher';
      result.textContent = error.message || 'Could not complete the dispatch.';
    }
  });
}