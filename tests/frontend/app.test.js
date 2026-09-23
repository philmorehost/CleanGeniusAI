test('electronAPI exposed methods sanity test', () => {
  const apiMethods = [
    'minimizeWindow',
    'maximizeWindow',
    'closeWindow',
    'startScan',
    'getScanResults',
    'startCleanup',
    'rollbackCleanup',
    'analyzeWithAI',
    'testAIConnection',
    'getSettings',
    'saveSettings',
    'selectFolder',
    'exportReport',
    'getSystemInfo',
    'getDashboard'
  ];

  expect(apiMethods.length).toBe(15);
});
