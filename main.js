// main.js
const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');

const isDev = !app.isPackaged;
let backendProcess = null;

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  mainWindow.loadURL(
    isDev
      ? 'http://localhost:5173'
      : `file://${path.join(__dirname, 'frontend', 'dist', 'index.html')}`
  );

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }
}

function startBackend() {
  const isWindows = process.platform === 'win32';
  const backendExecutable = isWindows ? 'main.exe' : 'main';
  
  const backendPath = isDev
    ? path.join(__dirname, 'backend', 'dist', backendExecutable)
    : path.join(process.resourcesPath, 'backend', backendExecutable);

  console.log(`[Electron] Uruchamianie backendu z: ${backendPath}`);
  try {
    backendProcess = spawn(backendPath, []);
    backendProcess.on('error', (err) => console.error('[Electron] Błąd backendu:', err));
  } catch (err) {
    console.error('[Electron] Nie udało się uruchomić backendu:', err);
  }
}

app.whenReady().then(() => {
  if (app.isPackaged || !isDev) {
    startBackend();
  }
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('will-quit', () => {
  if (backendProcess) {
    console.log('[Electron] Zamykanie backendu...');
    backendProcess.kill();
  }
});