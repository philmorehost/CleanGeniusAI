let currentWizStep = 1;

const wizStages = {
  1: {
    title: "Stage 1: Welcome & System Compatibility",
    subtitle: "Checking system requirements and environment readiness",
    render: async () => {
      let sysInfo = { total_space_gb: 0, free_space_gb: 0, os: "Windows" };
      try {
        const res = await window.electronAPI.getSystemInfo();
        if (res.success) sysInfo = res.data;
      } catch (e) {}

      return `
        <div style="text-align: center; padding: 20px 0;">
          <div style="font-size: 48px; margin-bottom: 12px;">🚀</div>
          <h3 style="font-size: 20px; font-weight: 700; margin-bottom: 8px;">Welcome to CleanGenius AI</h3>
          <p style="color: var(--text-muted); font-size: 14px; max-width: 500px; margin: 0 auto 24px auto;">
            CleanGenius AI combines multi-engine disk scanning with DeepSeek AI intelligence to keep your system clean, fast, and organized.
          </p>

          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; max-width: 500px; margin: 0 auto; text-align: left;">
            <div style="background: rgba(255,255,255,0.03); padding: 12px 16px; border-radius: 8px; border: 1px solid var(--border-color);">
              <div style="color: var(--text-muted); font-size: 12px;">Detected OS</div>
              <div style="font-weight: 600; font-size: 15px;">${sysInfo.os || 'Windows 10/11'}</div>
            </div>
            <div style="background: rgba(255,255,255,0.03); padding: 12px 16px; border-radius: 8px; border: 1px solid var(--border-color);">
              <div style="color: var(--text-muted); font-size: 12px;">Free Disk Space</div>
              <div style="font-weight: 600; font-size: 15px; color: var(--accent-green);">${sysInfo.free_space_gb || 0} GB Free</div>
            </div>
          </div>
        </div>
      `;
    }
  },

  2: {
    title: "Stage 2: AI Provider & Free API Key Guide",
    subtitle: "Connect your DeepSeek, OpenAI, Claude, Gemini, or Ollama API key",
    render: async () => {
      return `
        <div>
          <h4 style="font-size: 16px; font-weight: 600; margin-bottom: 12px;">Select Primary AI Engine</h4>

          <div class="form-group">
            <label class="form-label">AI Provider</label>
            <select class="form-select" id="wiz-provider" onchange="wizToggleApiKeyGroup()">
              <option value="deepseek" selected>DeepSeek AI (Recommended - Generous Free API)</option>
              <option value="gemini">Google Gemini (Free Tier)</option>
              <option value="openai">OpenAI (GPT-3.5 / GPT-4)</option>
              <option value="claude">Anthropic Claude</option>
              <option value="ollama">Ollama (100% Offline Local Model)</option>
            </select>
          </div>

          <div class="form-group" id="wiz-api-key-group">
            <label class="form-label">API Key</label>
            <input type="password" class="form-input" id="wiz-api-key" placeholder="sk-...">
            <p style="color: var(--text-muted); font-size: 12px; margin-top: 6px;">
              💡 <strong>How to get a Free DeepSeek API key:</strong><br>
              1. Visit <a href="#" onclick="window.electronAPI.openFileLocation && alert('Visit platform.deepseek.com'); return false;" style="color: var(--primary-blue);">platform.deepseek.com</a><br>
              2. Sign up and copy your API key from API Keys section<br>
              3. Paste key above (or leave empty to use Gemini/Local fallback mode)
            </p>
          </div>
        </div>
      `;
    }
  },

  3: {
    title: "Stage 3: Scanning & Exclusion Customization",
    subtitle: "Select disk areas and folder exclusions for safety",
    render: async () => {
      return `
        <div>
          <h4 style="font-size: 16px; font-weight: 600; margin-bottom: 12px;">Default Scan Targets</h4>
          <div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px;">
            <label style="display: flex; align-items: center; gap: 10px; font-size: 14px;">
              <input type="checkbox" checked disabled> Windows System Temp & User AppData Temp
            </label>
            <label style="display: flex; align-items: center; gap: 10px; font-size: 14px;">
              <input type="checkbox" id="wiz-scan-dev" checked> Developer Caches (node_modules, __pycache__, build/dist)
            </label>
            <label style="display: flex; align-items: center; gap: 10px; font-size: 14px;">
              <input type="checkbox" id="wiz-scan-browser" checked> Web Browser Web Caches & Session Media
            </label>
            <label style="display: flex; align-items: center; gap: 10px; font-size: 14px;">
              <input type="checkbox" id="wiz-scan-dupes" checked> Smart Duplicate File Analyzer
            </label>
          </div>
        </div>
      `;
    }
  },

  4: {
    title: "Stage 4: Safety, Backup & Rollback Setup",
    subtitle: "Configure deletion safety thresholds and instant recovery points",
    render: async () => {
      return `
        <div>
          <h4 style="font-size: 16px; font-weight: 600; margin-bottom: 12px;">Safety & Recovery Policy</h4>

          <div style="background: rgba(16,185,129,0.1); border: 1px solid var(--accent-green); padding: 16px; border-radius: 8px; margin-bottom: 20px;">
            <h5 style="color: var(--accent-green); margin-bottom: 6px; font-size: 15px;">🛡️ 3-Layer Safety Protection Active</h5>
            <p style="font-size: 13px; color: var(--text-main); margin: 0;">
              CleanGenius AI verifies protected Windows system paths, checks active process file locks, and creates an instant recovery point backup prior to cleanup.
            </p>
          </div>

          <div class="form-group">
            <label style="display: flex; align-items: center; gap: 10px; font-size: 14px;">
              <input type="checkbox" id="wiz-enable-rollback" checked> Enable Instant Rollback (Recommended)
            </label>
          </div>
        </div>
      `;
    }
  },

  5: {
    title: "Stage 5: Setup Complete!",
    subtitle: "CleanGenius AI is fully configured and ready",
    render: async () => {
      return `
        <div style="text-align: center; padding: 20px 0;">
          <div style="font-size: 56px; margin-bottom: 12px;">🎉</div>
          <h3 style="font-size: 22px; font-weight: 700; margin-bottom: 8px; color: var(--accent-green);">Configuration Complete!</h3>
          <p style="color: var(--text-muted); font-size: 14px; max-width: 500px; margin: 0 auto 24px auto;">
            Your disk cleanup assistant is initialized. You can now launch your first AI-guided fast scan.
          </p>
          <button class="btn" onclick="wizFinishAndScan()" style="font-size: 16px; padding: 12px 32px;">⚡ Run Initial Fast Scan Now</button>
        </div>
      `;
    }
  }
};

async function renderWizStep() {
  const step = wizStages[currentWizStep];
  if (!step) return;

  document.getElementById('wizard-step-title').innerText = step.title;
  document.getElementById('wizard-step-subtitle').innerText = step.subtitle;
  document.getElementById('wizard-step-counter').innerText = `Step ${currentWizStep} of 5`;

  for (let i = 1; i <= 5; i++) {
    const bar = document.getElementById(`wiz-bar-${i}`);
    if (bar) {
      bar.style.backgroundColor = i <= currentWizStep ? 'var(--primary-blue)' : 'var(--border-color)';
    }
  }

  const content = document.getElementById('wizard-stage-content');
  content.innerHTML = await step.render();

  const prevBtn = document.getElementById('wiz-btn-prev');
  const nextBtn = document.getElementById('wiz-btn-next');

  prevBtn.style.display = currentWizStep === 1 ? 'none' : 'block';
  nextBtn.innerText = currentWizStep === 5 ? 'Go to Dashboard' : 'Next Step →';
}

function wizPrevStep() {
  if (currentWizStep > 1) {
    currentWizStep--;
    renderWizStep();
  }
}

async function wizNextStep() {
  if (currentWizStep === 2) {
    const provider = document.getElementById('wiz-provider')?.value || 'deepseek';
    const apiKey = document.getElementById('wiz-api-key')?.value || '';
    if (window.electronAPI && window.electronAPI.saveSettings) {
      await window.electronAPI.saveSettings({ provider, apiKey });
    }
  }

  if (currentWizStep < 5) {
    currentWizStep++;
    renderWizStep();
  } else {
    navigate('dashboard');
  }
}

function wizToggleApiKeyGroup() {
  const provider = document.getElementById('wiz-provider')?.value;
  const grp = document.getElementById('wiz-api-key-group');
  if (grp) {
    grp.style.display = (provider === 'ollama') ? 'none' : 'block';
  }
}

async function wizFinishAndScan() {
  await navigate('scan');
  runScan('fast');
}

// Global initialization
window.initWiz = renderWizStep;
