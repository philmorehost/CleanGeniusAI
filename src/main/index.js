const { app, BrowserWindow, ipcMain, Menu, Tray, shell, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const Store = require('electron-store');
const log = require('electron-log');
const { autoUpdater } = require('electron-updater');

const store = new Store({
  encryptionKey: 'cleangenius-secure-key-2024'
});

log.transports.file.level = 'info';
autoUpdater.logger = log;

class CleanGeniusApp {
  constructor() {
    this.mainWindow = null;
    this.pythonProcess = null;
    this.tray = null;
    this.isQuitting = false;
  }

  async initialize() {
    app.on('ready', () => this.onReady());
    app.on('window-all-closed', () => this.onWindowAllClosed());
    app.on('activate', () => this.onActivate());
    app.on('before-quit', () => { this.isQuitting = true; });

    const gotTheLock = app.requestSingleInstanceLock();
    if (!gotTheLock) {
      app.quit();
      return;
    }

    app.on('second-instance', () => {
      if (this.mainWindow) {
        if (this.mainWindow.isMinimized()) this.mainWindow.restore();
        this.mainWindow.focus();
      }
    });
  }

  async onReady() {
    this.createMainWindow();
    await this.startPythonBackend().catch(err => log.error('Failed to start Python backend:', err));
    this.setupIPC();
    this.createTray();
    this.checkForUpdates();
    this.loadUserPreferences();
  }

  createMainWindow() {
    this.mainWindow = new BrowserWindow({
      width: 1400,
      height: 900,
      minWidth: 1200,
      minHeight: 700,
      frame: false,
      backgroundColor: '#0F1419',
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, '../preload.js'),
        devTools: process.env.NODE_ENV === 'development'
      },
      show: false
    });

    this.mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));

    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow.show();
      if (process.env.NODE_ENV === 'development') {
        this.mainWindow.webContents.openDevTools();
      }
    });

    this.mainWindow.on('close', (event) => {
      if (!this.isQuitting && store.get('minimizeToTray', true)) {
        event.preventDefault();
        this.mainWindow.hide();
      }
    });

    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
    });

    this.setupWindowControls();
  }

  setupWindowControls() {
    ipcMain.on('window-minimize', () => {
      if (this.mainWindow) this.mainWindow.minimize();
    });

    ipcMain.on('window-maximize', () => {
      if (!this.mainWindow) return;
      if (this.mainWindow.isMaximized()) {
        this.mainWindow.unmaximize();
      } else {
        this.mainWindow.maximize();
      }
    });

    ipcMain.on('window-close', () => {
      if (this.mainWindow) this.mainWindow.close();
    });
  }

  async startPythonBackend() {
    return new Promise((resolve, reject) => {
      const pythonPath = process.env.NODE_ENV === 'development' || !process.resourcesPath
        ? 'python3'
        : path.join(process.resourcesPath, 'backend', 'main.py');

      const scriptPath = path.join(__dirname, '../backend/main.py');

      log.info('Starting Python backend:', pythonPath, scriptPath);

      this.pythonProcess = spawn(pythonPath, [scriptPath], {
        env: { ...process.env, PYTHONUNBUFFERED: '1' }
      });

      let resolved = false;

      this.pythonProcess.stdout.on('data', (data) => {
        const output = data.toString();
        log.info('Python:', output);
        if (output.includes('http://127.0.0.1:5000') && !resolved) {
          resolved = true;
          resolve();
        }
      });

      this.pythonProcess.stderr.on('data', (data) => {
        log.error('Python Error:', data.toString());
      });

      this.pythonProcess.on('close', (code) => {
        log.info('Python process exited with code', code);
      });

      setTimeout(() => {
        if (!resolved) {
          resolve(); // Resolve anyway after 3s
        }
      }, 3000);
    });
  }

  setupIPC() {
    ipcMain.handle('start-scan', async (event, options) => {
      const response = await fetch('http://127.0.0.1:5000/api/scan/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(options)
      });
      return await response.json();
    });

    ipcMain.handle('get-scan-results', async (event, scanId) => {
      const response = await fetch(`http://127.0.0.1:5000/api/scan/${scanId}`);
      return await response.json();
    });

    ipcMain.handle('start-cleanup', async (event, options) => {
      const response = await fetch('http://127.0.0.1:5000/api/cleanup/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(options)
      });
      return await response.json();
    });

    ipcMain.handle('rollback-cleanup', async (event, sessionId) => {
      const response = await fetch(`http://127.0.0.1:5000/api/cleanup/rollback/${sessionId}`, {
        method: 'POST'
      });
      return await response.json();
    });

    ipcMain.handle('ai-analyze', async (event, data) => {
      const response = await fetch('http://127.0.0.1:5000/api/ai/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      return await response.json();
    });

    ipcMain.handle('test-ai-connection', async (event, provider) => {
      const response = await fetch(`http://127.0.0.1:5000/api/ai/test/${provider}`);
      return await response.json();
    });

    ipcMain.handle('get-settings', () => {
      return store.store;
    });

    ipcMain.handle('save-settings', (event, settings) => {
      Object.keys(settings).forEach(key => {
        store.set(key, settings[key]);
      });
      return { success: true };
    });

    ipcMain.handle('select-folder', async () => {
      const result = await dialog.showOpenDialog(this.mainWindow, {
        properties: ['openDirectory']
      });
      return result.filePaths[0];
    });

    ipcMain.handle('export-report', async (event, data) => {
      const { filePath } = await dialog.showSaveDialog(this.mainWindow, {
        defaultPath: `CleanGenius_Report_${new Date().toISOString().split('T')[0]}.pdf`,
        filters: [
          { name: 'PDF', extensions: ['pdf'] },
          { name: 'CSV', extensions: ['csv'] },
          { name: 'JSON', extensions: ['json'] }
        ]
      });

      if (filePath) {
        const response = await fetch('http://127.0.0.1:5000/api/reports/export', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ...data, filePath })
        });
        return await response.json();
      }
      return { cancelled: true };
    });

    ipcMain.handle('get-system-info', async () => {
      const response = await fetch('http://127.0.0.1:5000/api/system/info');
      return await response.json();
    });

    ipcMain.handle('get-dashboard', async () => {
      const response = await fetch('http://127.0.0.1:5000/api/dashboard');
      return await response.json();
    });
  }

  createTray() {
    try {
      this.tray = new Tray(path.join(__dirname, '../../resources/icons/icon.ico'));
      const contextMenu = Menu.buildFromTemplate([
        { label: 'Show CleanGenius AI', click: () => this.mainWindow.show() },
        { label: 'Quit', click: () => { this.isQuitting = true; app.quit(); } }
      ]);
      this.tray.setToolTip('CleanGenius AI');
      this.tray.setContextMenu(contextMenu);
    } catch (e) {
      // Icon missing in dev environment gracefully ignored
    }
  }

  checkForUpdates() {
    if (process.env.NODE_ENV !== 'development') {
      autoUpdater.checkForUpdatesAndNotify();
    }
  }

  loadUserPreferences() {
    const preferences = {
      theme: store.get('theme', 'dark'),
      autoScan: store.get('autoScan', false),
      minimizeToTray: store.get('minimizeToTray', true)
    };
    if (this.mainWindow) {
      this.mainWindow.webContents.send('load-preferences', preferences);
    }
  }

  onWindowAllClosed() {
    if (process.platform !== 'darwin') {
      app.quit();
    }
  }

  onActivate() {
    if (this.mainWindow === null) {
      this.createMainWindow();
    }
  }

  async shutdown() {
    if (this.pythonProcess) {
      this.pythonProcess.kill();
    }
    if (this.tray) {
      this.tray.destroy();
    }
  }
}

const cleanGeniusApp = new CleanGeniusApp();
cleanGeniusApp.initialize();

app.on('will-quit', async () => {
  await cleanGeniusApp.shutdown();
});
