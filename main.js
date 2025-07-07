// main.js - Wersja z Poprawnym Uruchamianiem Backendu
const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');

// Używamy wbudowanej funkcji, aby sprawdzić, czy aplikacja jest w trybie deweloperskim
const isDev = !app.isPackaged;

let backendProcess = null;

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  mainWindow.loadURL(
    isDev
      ? 'http://localhost:5173'
      : `file://${path.join(__dirname, 'frontend/dist/index.html')}`
  );

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }
}

function startBackend() {
  // --- POCZĄTEK KLUCZOWEJ ZMIANY ---
  // Sprawdzamy, na jakim systemie operacyjnym działa aplikacja
  const isWindows = process.platform === 'win32';
  const backendExecutable = isWindows ? 'main.exe' : 'main'; // Wybieramy właściwą nazwę pliku
  
  // Budujemy poprawną ścieżkę do pliku wykonywalnego
  const backendPath = isDev
    ? path.join(__dirname, 'backend', 'dist', backendExecutable)
    // W wersji produkcyjnej ścieżka jest inna, 'process.resourcesPath' jest kluczowe
    : path.join(process.resourcesPath, 'backend', backendExecutable);
  // --- KONIEC KLUCZOWEJ ZMIANY ---

  console.log(`[Electron] Uruchamianie backendu z: ${backendPath}`);

  try {
    backendProcess = spawn(backendPath, [], { detached: true, stdio: 'ignore' });
    backendProcess.unref(); // Pozwalamy głównemu procesowi zakończyć się bez czekania na backend

    backendProcess.on('error', (err) => {
      console.error('[Electron] Błąd uruchamiania backendu:', err);
    });

    backendProcess.on('close', (code) => {
      console.log(`[Electron] Proces backendu zakończony z kodem: ${code}`);
    });

  } catch (err) {
    console.error('[Electron] Nie udało się uruchomić procesu backendu:', err);
  }
}

app.whenReady().then(() => {
  // Uruchom backend tylko w wersji produkcyjnej (spakowanej)
  if (app.isPackaged) {
    startBackend();
  }
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('will-quit', () => {
  console.log('[Electron] Zamykanie aplikacji...');
  if (backendProcess) {
    console.log('[Electron] Zamykanie procesu backendu...');
    // Zamykanie procesu w sposób bezpieczny dla różnych systemów
    if (process.platform === 'win32') {
      exec(`taskkill /PID ${backendProcess.pid} /F /T`);
    } else {
      process.kill(-backendProcess.pid, 'SIGKILL');
    }
  }
});