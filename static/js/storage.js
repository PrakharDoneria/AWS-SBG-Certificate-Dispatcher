export const CREDENTIALS_KEY = 'sbg-dispatcher-credentials';
export const LISTS_KEY = 'sbg-dispatcher-lists';
export const GATE_KEY = 'sbg-dispatcher-unlocked';

export function readLists() {
  return JSON.parse(localStorage.getItem(LISTS_KEY) || '[]');
}

export function saveLists(lists) {
  localStorage.setItem(LISTS_KEY, JSON.stringify(lists));
}