const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');

let mainWindow;
let backendProcess;
const exePath = path.join(__dirname, 'backend/dist/main.exe');

function createWindow() {
  backendProcess = spawn(exePath);

  backendProcess.stdout.on('data', (data) => {
    console.log(`[BACKEND STDOUT] ${data}`);
  });
  // Obsługa standardowego wyjścia backendu, przekierowuje dane z backendu do konsoli

  backendProcess.stderr.on('data', (data) => {
    console.error(`[BACKEND ERROR] ${data}`);
  });
  // Obsługa standardowego błędu backendu, przekierowuje błędy z backendu do konsoli

  backendProcess.on('exit', (code) => {
    console.error(`[BACKEND EXIT] Kod zakończenia: ${code}`);
  });
  // Obsługa zdarzenia zakończenia procesu backendu, loguje kod zakończenia


  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },

  });

  mainWindow.loadFile(path.join(__dirname, 'frontend/dist/index.html'));


app.on('before-quit', () => {
  if (backendProcess) {
    exec(`taskkill /PID ${backendProcess.pid} /F /T`); //Systemowa komenda do zakończenia procesu backendu i wszystkich jego potomków (/T)
    // Zwykłe `backendProcess.kill()` może nie działać poprawnie w niektórych przypadkach, więc dla pewności używamy `exec` do wykonania polecenia systemowego
    mainWindow = null;
  }
});
}

app.on('ready', createWindow);
app.on('window-all-closed', () => app.quit());