const { app, BrowserWindow, ipcMain, Menu, Tray, shell, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
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
    await this.startPythonBackend().catch(err => log.error('Failed to start backend process:', err));
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
      let backendCmd;
      let backendArgs;

      const bundledExePath = path.join(process.resourcesPath || '', 'backend', 'cleangenius-backend.exe');
      const bundledSrcPath = path.join(process.resourcesPath || '', 'backend-src', 'main.py');

      if (process.env.NODE_ENV !== 'development' && fs.existsSync(bundledExePath)) {
        // Production: run standalone PyInstaller compiled exe
        backendCmd = bundledExePath;
        backendArgs = [];
      } else if (process.env.NODE_ENV !== 'development' && fs.existsSync(bundledSrcPath)) {
        // Fallback: run Python script in resources/backend-src/
        const isWin = process.platform === 'win32';
        backendCmd = isWin ? 'python' : 'python3';
        backendArgs = [bundledSrcPath];
      } else {
        // Development environment
        const isWin = process.platform === 'win32';
        backendCmd = isWin ? 'python' : 'python3';
        backendArgs = [path.join(__dirname, '../backend/main.py')];
      }

      log.info('Starting backend engine process:', backendCmd, backendArgs);

      try {
        this.pythonProcess = spawn(backendCmd, backendArgs, {
          env: { ...process.env, PYTHONUNBUFFERED: '1' }
        });
      } catch (err) {
        log.error('Spawn exception:', err);
        return resolve();
      }

      let resolved = false;

      this.pythonProcess.stdout.on('data', (data) => {
        const output = data.toString();
        log.info('Backend stdout:', output);
        if (output.includes('http://127.0.0.1:5000') && !resolved) {
          resolved = true;
          resolve();
        }
      });

      this.pythonProcess.stderr.on('data', (data) => {
        log.error('Backend stderr:', data.toString());
      });

      this.pythonProcess.on('error', (err) => {
        log.error('Backend process error:', err);
        if (!resolved) {
          resolved = true;
          resolve();
        }
      });

      this.pythonProcess.on('close', (code) => {
        log.info('Backend process exited with code', code);
      });

      setTimeout(() => {
        if (!resolved) {
          resolved = true;
          resolve();
        }
      }, 5000);
    });
  }

  setupIPC() {
    const safeFetchJson = async (url, options = {}) => {
      try {
        const response = await fetch(url, options);
        return await response.json();
      } catch (err) {
        log.error(`API fetch error on ${url}:`, err);
        return { success: false, error: `Backend API server unreachable (${err.message})` };
      }
    };

    ipcMain.handle('start-scan', async (event, options) => {
      return await safeFetchJson('http://127.0.0.1:5000/api/scan/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(options)
      });
    });

    ipcMain.handle('get-scan-results', async (event, scanId) => {
      return await safeFetchJson(`http://127.0.0.1:5000/api/scan/${scanId}`);
    });

    ipcMain.handle('start-cleanup', async (event, options) => {
      return await safeFetchJson('http://127.0.0.1:5000/api/cleanup/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(options)
      });
    });

    ipcMain.handle('rollback-cleanup', async (event, sessionId) => {
      return await safeFetchJson(`http://127.0.0.1:5000/api/cleanup/rollback/${sessionId}`, {
        method: 'POST'
      });
    });

    ipcMain.handle('ai-analyze', async (event, data) => {
      return await safeFetchJson('http://127.0.0.1:5000/api/ai/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
    });

    ipcMain.handle('test-ai-connection', async (event, data) => {
      const provider = typeof data === 'string' ? data : data.provider;
      const apiKey = typeof data === 'object' ? data.apiKey : null;
      return await safeFetchJson(`http://127.0.0.1:5000/api/ai/test/${provider}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey })
      });
    });

    ipcMain.handle('get-settings', () => {
      return store.store;
    });

    ipcMain.handle('save-settings', async (event, settings) => {
      Object.keys(settings).forEach(key => {
        store.set(key, settings[key]);
      });
      // Sync settings with Flask backend
      await safeFetchJson('http://127.0.0.1:5000/api/ai/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: settings.provider,
          api_key: settings.apiKey,
          keys: settings.apiKeys || {}
        })
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
        return await safeFetchJson('http://127.0.0.1:5000/api/reports/export', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ...data, filePath })
        });
      }
      return { cancelled: true };
    });

    ipcMain.handle('get-system-info', async () => {
      return await safeFetchJson('http://127.0.0.1:5000/api/system/info');
    });

    ipcMain.handle('get-dashboard', async () => {
      return await safeFetchJson('http://127.0.0.1:5000/api/dashboard');
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
