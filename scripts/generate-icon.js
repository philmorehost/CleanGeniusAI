#!/usr/bin/env node
/**
 * Generates a valid multi-resolution Windows .ico file
 * using pure JS libraries (no native deps, no ImageMagick,
 * no .NET Bitmap bugs). Works identically on Windows/Linux/Mac/CI.
 */

const fs = require('fs');
const path = require('path');
const { PNG } = require('pngjs');
const rawPngToIco = require('png-to-ico');
const pngToIco = typeof rawPngToIco === 'function' ? rawPngToIco : (rawPngToIco.default || rawPngToIco.imagesToIco);

const ICONS_DIR = path.join(__dirname, '..', 'resources', 'icons');
const SIZE = 256;

function drawIcon() {
  const png = new PNG({ width: SIZE, height: SIZE });
  const cx = SIZE / 2;
  const cy = SIZE / 2;
  const radius = SIZE / 3;

  for (let y = 0; y < SIZE; y++) {
    for (let x = 0; x < SIZE; x++) {
      const idx = (SIZE * y + x) << 2;
      const dx = x - cx;
      const dy = y - cy;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist <= radius) {
        // White circle (foreground)
        png.data[idx] = 255;
        png.data[idx + 1] = 255;
        png.data[idx + 2] = 255;
        png.data[idx + 3] = 255;
      } else {
        // Brand blue background
        png.data[idx] = 45;
        png.data[idx + 1] = 91;
        png.data[idx + 2] = 255;
        png.data[idx + 3] = 255;
      }
    }
  }
  return png;
}

async function generateIcon() {
  console.log('🎨 Generating application icon...');

  if (!fs.existsSync(ICONS_DIR)) {
    fs.mkdirSync(ICONS_DIR, { recursive: true });
  }

  const pngPath = path.join(ICONS_DIR, 'icon.png');
  const icoPath = path.join(ICONS_DIR, 'icon.ico');

  // 1. Write a valid PNG using pngjs (pure JS PNG encoder)
  const png = drawIcon();
  const pngBuffer = PNG.sync.write(png);
  fs.writeFileSync(pngPath, pngBuffer);
  console.log(`   ✓ Created ${pngPath}`);

  // 2. Convert PNG -> valid multi-res ICO using png-to-ico
  const icoBuffer = await pngToIco([pngPath]);
  fs.writeFileSync(icoPath, icoBuffer);
  console.log(`   ✓ Created ${icoPath}`);

  // 3. Sanity check the ICO header (first bytes must be 00 00 01 00)
  const header = fs.readFileSync(icoPath).subarray(0, 4);
  const valid = header[0] === 0 && header[1] === 0 && header[2] === 1 && header[3] === 0;
  if (!valid) {
    throw new Error('Generated icon.ico failed header validation!');
  }
  console.log('   ✓ icon.ico header validated (valid ICO format)');

  console.log('✅ Icon generation complete!\n');
}

generateIcon().catch((err) => {
  console.error('❌ Icon generation failed:', err);
  process.exit(1);
});
