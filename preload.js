// preload.js
const { contextBridge, ipcRenderer } = require('electron');

// Na razie nie wystawiamy żadnych funkcji do frontendu,
// ale ten plik musi istnieć, aby aplikacja się poprawnie załadowała.
contextBridge.exposeInMainWorld('electronAPI', {
  // W przyszłości można tu dodać funkcje do komunikacji
  // między oknem aplikacji a jej głównym procesem.
});