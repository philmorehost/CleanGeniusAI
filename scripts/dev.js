const { spawn } = require('child_process');
const path = require('path');

console.log('Starting CleanGenius AI Development Environment...');

const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';

const pyProc = spawn(pythonCmd, [path.join(__dirname, '../src/backend/main.py')], {
  stdio: 'inherit',
  env: { ...process.env, PYTHONUNBUFFERED: '1' }
});

pyProc.on('error', (err) => {
  console.error('Failed to start Python backend:', err);
});

process.on('SIGINT', () => {
  pyProc.kill();
  process.exit();
});
