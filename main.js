const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let backendProcess;

function createWindow() {
  backendProcess = spawn(path.join(__dirname, 'backend/dist/main.exe'));

  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  mainWindow.loadFile(path.join(__dirname, 'frontend/dist/index.html'));

  mainWindow.on('closed', () => {
    if (backendProcess) backendProcess.kill();
    mainWindow = null;
  });
}

app.on('ready', createWindow);
app.on('window-all-closed', () => app.quit());