const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  minimizeWindow: () => ipcRenderer.send('window-minimize'),
  maximizeWindow: () => ipcRenderer.send('window-maximize'),
  closeWindow: () => ipcRenderer.send('window-close'),

  startScan: (options) => ipcRenderer.invoke('start-scan', options),
  getScanResults: (scanId) => ipcRenderer.invoke('get-scan-results', scanId),

  startCleanup: (options) => ipcRenderer.invoke('start-cleanup', options),
  rollbackCleanup: (sessionId) => ipcRenderer.invoke('rollback-cleanup', sessionId),

  analyzeWithAI: (data) => ipcRenderer.invoke('ai-analyze', data),
  testAIConnection: (provider) => ipcRenderer.invoke('test-ai-connection', provider),

  getSettings: () => ipcRenderer.invoke('get-settings'),
  saveSettings: (settings) => ipcRenderer.invoke('save-settings', settings),

  selectFolder: () => ipcRenderer.invoke('select-folder'),
  exportReport: (data) => ipcRenderer.invoke('export-report', data),

  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
  getDashboard: () => ipcRenderer.invoke('get-dashboard'),

  onLoadPreferences: (callback) => {
    ipcRenderer.on('load-preferences', (event, preferences) => callback(preferences));
  }
});

contextBridge.exposeInMainWorld('appInfo', {
  version: '1.0.0',
  platform: process.platform
});
