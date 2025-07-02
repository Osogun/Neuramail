const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');
const http = require('http');

let mainWindow;
let backendProcess;
const exePath = path.join(__dirname, 'backend/dist/main.exe');

function waitForBackend(url, maxRetries = 20, delay = 500) {
  return new Promise((resolve, reject) => {
    let attempts = 0;

    const check = () => {
      const req = http.get(url, () => resolve());
      req.on('error', () => {
        attempts++;
        if (attempts >= maxRetries) return reject(new Error("Backend nie wstał na czas"));
        setTimeout(check, delay);
      });
    };

    check();
  });
}

function killBackend() {
  if (backendProcess) {
    exec(`taskkill /PID ${backendProcess.pid} /F /T`); //Systemowa komenda do zakończenia procesu backendu i wszystkich jego potomków (/T)
    // Zwykłe `backendProcess.kill()` może nie działać poprawnie w niektórych przypadkach, więc dla pewności używamy `exec` do wykonania polecenia systemowego
  }
}

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


  waitForBackend('http://127.0.0.1:8000/root')
    .then(() => {
      mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
          nodeIntegration: true,
          contextIsolation: false,
        },
      });

      mainWindow.loadFile(path.join(__dirname, 'frontend/dist/index.html'));
    })
    .catch((err) => {
      console.error("Bład przy ładowaniu frontendu: ", err);
    });

}

// Rejestracja zdarzeń aplikacji
app.on('ready', createWindow);

app.on('before-quit', () => {
  console.log("Zamykanie aplikacji...");
  killBackend();
  mainWindow = null;
});

app.on('window-all-closed', () => app.quit());