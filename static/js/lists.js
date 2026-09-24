import { LISTS_KEY, readLists, saveLists } from './storage.js';

function renderSavedLists() {
  const target = document.getElementById('saved-list-items');
  if (!target) return;
  const lists = readLists();
  document.getElementById('list-count').textContent = `${lists.length} list${lists.length === 1 ? '' : 's'}`;
  if (lists.length) {
    target.innerHTML = lists.map((list, index) => `<div class="saved-row"><div><b>${list.name}</b><small>${list.added}</small></div><div class="saved-actions"><button type="button" data-view-list="${index}">View</button><button type="button" data-download-list="${index}">Download</button><button type="button" data-delete-list="${index}" aria-label="Delete ${list.name}">Delete</button></div></div>`).join('');
    target.querySelectorAll('[data-view-list]').forEach((button) => button.addEventListener('click', () => {
      const list = readLists()[Number(button.dataset.viewList)];
      const preview = document.getElementById('list-preview');
      preview.textContent = list.content;
      preview.hidden = false;
    }));
    target.querySelectorAll('[data-download-list]').forEach((button) => button.addEventListener('click', () => {
      const list = readLists()[Number(button.dataset.downloadList)];
      const link = document.createElement('a');
      link.href = URL.createObjectURL(new Blob([list.content], { type: 'text/csv' }));
      link.download = list.name;
      link.click();
      URL.revokeObjectURL(link.href);
    }));
    target.querySelectorAll('[data-delete-list]').forEach((button) => button.addEventListener('click', () => {
      const lists = readLists();
      lists.splice(Number(button.dataset.deleteList), 1);
      saveLists(lists);
      renderSavedLists();
    }));
  }
}

export function initLists() {
  const upload = document.getElementById('list-upload');
  if (upload) {
    upload.addEventListener('change', () => {
      const file = upload.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {
        const lists = readLists();
        lists.push({ name: file.name, content: reader.result, added: new Date().toLocaleDateString() });
        saveLists(lists);
        renderSavedLists();
      };
      reader.readAsText(file);
    });
  }
  if (document.getElementById('saved-list-select')) {
    const select = document.getElementById('saved-list-select');
    readLists().forEach((list, index) => select.add(new Option(list.name, String(index))));
  }
  renderSavedLists();
}