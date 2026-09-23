const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('Building PyInstaller backend executable...');

const pyinstallerCmd = `pyinstaller --onefile --name cleangenius-backend ` +
  `--distpath dist-backend ` +
  `--hidden-import=win32api ` +
  `--hidden-import=win32con ` +
  `--hidden-import=psutil ` +
  `--hidden-import=flask_cors ` +
  `--hidden-import=software.software_manager ` +
  `--hidden-import=rules.rules_engine ` +
  `--hidden-import=recommendation_service ` +
  `src/backend/main.py`;

try {
  execSync(pyinstallerCmd, { stdio: 'inherit' });
  console.log('Backend executable built successfully in dist-backend/');
} catch (err) {
  console.error('PyInstaller build failed:', err.message);
  process.exit(1);
}
