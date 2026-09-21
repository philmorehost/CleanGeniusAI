const fs = require('fs');
const path = require('path');

const dirs = [
  'src/main',
  'src/renderer',
  'resources/icons',
  'config',
  'build',
  'dist'
];

const files = {
  'LICENSE': 'MIT License\n\nCopyright (c) 2024 CleanGenius AI\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software...',
  'README.md': '# CleanGenius AI\n\nAI-powered Windows disk cleanup utility.',
  'build/installer.nsh': '!macro customInstall\n  DetailPrint "Configuring CleanGenius AI..."\n!macroend\n'
};

// Ensure directories exist
dirs.forEach(dir => {
  const fullPath = path.join(__dirname, '..', dir);
  if (!fs.existsSync(fullPath)) {
    fs.mkdirSync(fullPath, { recursive: true });
    console.log(`Created directory: ${dir}`);
  }
});

// Ensure placeholder files exist
Object.entries(files).forEach(([file, content]) => {
  const fullPath = path.join(__dirname, '..', file);
  if (!fs.existsSync(fullPath)) {
    fs.writeFileSync(fullPath, content);
    console.log(`Created file: ${file}`);
  }
});

// Create placeholder icon file if missing
const iconPath = path.join(__dirname, '../resources/icons/icon-placeholder.txt');
if (!fs.existsSync(iconPath)) {
  fs.writeFileSync(iconPath, 'CleanGenius AI icon resources');
}

console.log('✅ Build preparation complete!');
