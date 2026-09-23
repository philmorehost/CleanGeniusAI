let currentScanId = null;
let savedApiKeys = { deepseek: '', openai: '', claude: '', gemini: '', ollama: '' };

// Frameless Titlebar Controls
document.getElementById('btn-minimize')?.addEventListener('click', () => window.electronAPI.minimizeWindow());
document.getElementById('btn-maximize')?.addEventListener('click', () => window.electronAPI.maximizeWindow());
document.getElementById('btn-close')?.addEventListener('click', () => window.electronAPI.closeWindow());

// Navigation Router
const pages = {
  dashboard: 'pages/dashboard.html',
  scan: 'pages/scan.html',
  cleanup: 'pages/cleanup.html',
  schedule: 'pages/schedule.html',
  history: 'pages/history.html',
  settings: 'pages/settings.html',
  onboarding: 'pages/onboarding.html',
};

async function navigate(page) {
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const targetNav = document.querySelector(`[data-page="${page}"]`);
  if (targetNav) targetNav.classList.add('active');

  const content = document.getElementById('main-content');
  try {
    const html = await fetch(pages[page]).then(r => r.text());
    content.innerHTML = html;
    if (page === 'dashboard') loadDashboardData();
    if (page === 'settings') loadSettingsData();
    if (page === 'onboarding' && window.initWiz) window.initWiz();
  } catch (err) {
    content.innerHTML = `<div class="card"><h2>Error loading page ${page}</h2></div>`;
  }
}

document.querySelectorAll('.nav-item').forEach(a => {
  a.addEventListener('click', e => {
    e.preventDefault();
    navigate(a.getAttribute('data-page'));
  });
});

async function loadDashboardData() {
  try {
    const res = await window.electronAPI.getDashboard();
    if (res && res.success && res.data) {
      const info = res.data.system_info || {};
      document.getElementById('dash-total-space').innerText = (info.total_space_gb || 0) + ' GB';
      document.getElementById('dash-free-space').innerText = (info.free_space_gb || 0) + ' GB';

      const latest = res.data.latest_scan || {};
      const cleanable = ((latest.total_size_bytes || 0) / (1024 ** 3)).toFixed(2);
      document.getElementById('dash-cleanable').innerText = cleanable + ' GB';

      const badge = document.getElementById('health-score-badge');
      if (badge) badge.innerText = (res.data.health_score || 95) + '%';

      const actLog = document.getElementById('activity-log');
      if (actLog) {
        const list = res.data.recent_activity || [];
        if (list.length === 0) {
          actLog.innerHTML = '<p>No recent activity.</p>';
        } else {
          actLog.innerHTML = list.map(a => `<div style="padding: 6px 0; border-bottom: 1px solid var(--border-color);"><strong>${a.title}:</strong> ${a.detail} <span style="color: var(--text-muted); font-size: 11px;">(${a.timestamp})</span></div>`).join('');
        }
      }
    }
  } catch (e) {
    console.error(e);
  }
}

async function startQuickScan() {
  await navigate('scan');
  runScan('fast');
}

async function runScan(mode) {
  const pCard = document.getElementById('scan-progress-card');
  const rCard = document.getElementById('scan-results-card');
  if (pCard) pCard.style.display = 'block';
  if (rCard) rCard.style.display = 'none';

  const msgElem = document.getElementById('scan-status-msg');
  if (msgElem) msgElem.innerText = 'Initializing scan session...';

  const barElem = document.getElementById('scan-progress-bar');
  if (barElem) barElem.style.width = '1%';

  const aiEnabled = document.getElementById('chk-enable-ai')?.checked ?? true;

  try {
    const res = await window.electronAPI.startScan({
      mode,
      options: { find_duplicates: true, ai_analysis: aiEnabled }
    });
    if (res && res.success && res.scan_id) {
      currentScanId = res.scan_id;
      pollScanStatus(res.scan_id);
    } else {
      if (msgElem) msgElem.innerText = `Scan error: ${res?.error || 'Failed to start scan server worker'}`;
    }
  } catch (err) {
    if (msgElem) msgElem.innerText = `Scan error: Backend server unreachable (${err.message})`;
  }
}

async function pollScanStatus(scanId) {
  const timer = setInterval(async () => {
    try {
      const statusRes = await window.electronAPI.getScanResults(scanId);
      if (statusRes && statusRes.success) {
        const p = Math.max(statusRes.progress || 0, 1);
        const bar = document.getElementById('scan-progress-bar');
        const msg = document.getElementById('scan-status-msg');

        if (bar) bar.style.width = p + '%';
        if (msg) msg.innerText = statusRes.message || `Scanning files (${p}%)...`;

        if (statusRes.status === 'completed' || p >= 100) {
          clearInterval(timer);
          displayScanResults(statusRes.results);
        } else if (statusRes.status === 'failed') {
          clearInterval(timer);
          if (msg) msg.innerText = `Scan failed: ${statusRes.error || statusRes.message || 'Unknown error'}`;
        }
      }
    } catch (err) {
      clearInterval(timer);
      const msg = document.getElementById('scan-status-msg');
      if (msg) msg.innerText = `Connection lost: ${err.message}`;
    }
  }, 500);
}

function toggleAllCategories(checked) {
  document.querySelectorAll('.cat-select-chk').forEach(c => c.checked = checked);
}

function displayScanResults(results) {
  document.getElementById('scan-progress-card').style.display = 'none';
  document.getElementById('scan-results-card').style.display = 'block';

  const container = document.getElementById('scan-results-content');
  if (!results) {
    container.innerHTML = '<p>No scan results found.</p>';
    return;
  }

  const gb = ((results.total_size_bytes || 0) / (1024 ** 3)).toFixed(2);
  let html = `<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
    <p style="margin: 0; font-size: 15px;">Scan Complete. Total Unwanted Space: <strong style="color: var(--accent-green);">${gb} GB</strong> (${results.total_files || 0} files)</p>
    <div>
      <a href="#" onclick="toggleAllCategories(true); return false;" style="color: var(--primary-blue); font-size: 12px; margin-right: 10px;">Select All</a>
      <a href="#" onclick="toggleAllCategories(false); return false;" style="color: var(--text-muted); font-size: 12px;">Deselect All</a>
    </div>
  </div>`;

  if (results.categories) {
    html += '<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 16px;">';
    for (const [cat, data] of Object.entries(results.categories)) {
      const catGb = ((data.size_bytes || 0) / (1024 ** 3)).toFixed(2);
      html += `<div style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 6px; border: 1px solid var(--border-color); display: flex; align-items: center; gap: 10px;">
        <input type="checkbox" class="cat-select-chk" value="${cat}" checked style="transform: scale(1.2);">
        <div style="flex-grow: 1;">
          <strong style="color: var(--text-main); font-size: 14px;">${cat}</strong>
          <div style="color: var(--text-muted); font-size: 12px;">${data.count} files • ${catGb} GB</div>
        </div>
      </div>`;
    }
    html += '</div>';
  }

  if (results.ai_recommendations && results.ai_recommendations.recommendations) {
    html += '<h4 style="margin: 16px 0 8px 0; color: var(--primary-blue);">💡 Safety Insights & Recommendations:</h4>';
    results.ai_recommendations.recommendations.forEach(r => {
      html += `<div style="background: rgba(45,91,255,0.08); padding: 10px; border-radius: 6px; margin-bottom: 8px;">
        <strong>Category:</strong> ${r.category} | <strong>Action:</strong> ${r.action.toUpperCase()} | <strong>Safety Score:</strong> ${r.safety_score}/10<br>
        <span style="color: var(--text-muted); font-size: 12px;">${r.reasoning}</span>
      </div>`;
    });
  }

  container.innerHTML = html;
}

async function cleanAllScannedFiles() {
  if (!currentScanId) {
    alert('Please run a disk scan first.');
    return;
  }
  if (confirm('Are you sure you want to remove ALL scanned junk files?')) {
    executeCleanup(null);
  }
}

async function cleanSelectedCategories() {
  if (!currentScanId) {
    alert('Please run a disk scan first.');
    return;
  }
  const selected = [];
  document.querySelectorAll('.cat-select-chk:checked').forEach(cb => selected.push(cb.value));

  if (selected.length === 0) {
    alert('Please select at least one category to clean.');
    return;
  }
  executeCleanup(selected);
}

async function executeCleanup(categories = null) {
  if (!currentScanId) {
    alert('Please run a disk scan first.');
    return;
  }

  const cCard = document.getElementById('cleanup-status-card');
  if (cCard) cCard.style.display = 'block';

  const recycle = document.getElementById('chk-recycle')?.checked ?? true;
  const shred = document.getElementById('chk-shred')?.checked ?? false;

  try {
    const payload = {
      scan_id: currentScanId,
      options: { recycle_bin: recycle, secure_shred: shred }
    };
    if (categories && categories.length > 0) {
      payload.categories = categories;
    }

    const res = await window.electronAPI.startCleanup(payload);

    if (res && res.success && res.cleanup_id) {
      pollCleanupStatus(res.cleanup_id);
    } else {
      alert(`Cleanup start failed: ${res?.error || 'Unknown error'}`);
    }
  } catch (err) {
    alert(`Cleanup connection error: ${err.message}`);
  }
}

async function pollCleanupStatus(cleanupId) {
  const timer = setInterval(async () => {
    try {
      const statusRes = await fetch(`http://127.0.0.1:5000/api/cleanup/${cleanupId}`).then(r => r.json());
      if (statusRes && statusRes.success) {
        const p = statusRes.progress || 0;
        const bar = document.getElementById('cleanup-progress-bar');
        const msg = document.getElementById('cleanup-status-msg');

        if (bar) bar.style.width = p + '%';
        if (msg) msg.innerText = statusRes.message || `Cleaning (${p}%)...`;

        if (statusRes.status === 'completed' || p >= 100) {
          clearInterval(timer);
          alert(`Cleanup finished! Freed ${statusRes.result?.space_freed_gb?.toFixed(2) || 0} GB.`);
        } else if (statusRes.status === 'failed') {
          clearInterval(timer);
          alert(`Cleanup failed: ${statusRes.error || 'Unknown error'}`);
        }
      }
    } catch (err) {
      clearInterval(timer);
      console.error(err);
    }
  }, 500);
}

function updateProviderFields() {
  const provider = document.getElementById('setting-provider')?.value || 'deepseek';
  const input = document.getElementById('setting-api-key');
  if (input) {
    input.value = savedApiKeys[provider] || '';
    if (provider === 'ollama') {
      input.placeholder = 'Local server http://localhost:11434 (No API key required)';
    } else {
      input.placeholder = 'Enter ' + provider.toUpperCase() + ' API key (sk-...)';
    }
  }
}

function onKeyInput(val) {
  const provider = document.getElementById('setting-provider')?.value || 'deepseek';
  savedApiKeys[provider] = val;
}

async function loadSettingsData() {
  try {
    const res = await window.electronAPI.getSettings();
    if (res) {
      if (res.apiKeys) {
        savedApiKeys = { ...savedApiKeys, ...res.apiKeys };
      }
      if (res.provider && document.getElementById('setting-provider')) {
        document.getElementById('setting-provider').value = res.provider;
      }
      updateProviderFields();
    }
  } catch (e) {
    console.error(e);
  }
}

async function saveAISettings() {
  const provider = document.getElementById('setting-provider').value;
  const apiKey = document.getElementById('setting-api-key').value;
  savedApiKeys[provider] = apiKey;

  const res = await window.electronAPI.saveSettings({ provider, apiKey, apiKeys: savedApiKeys });
  const feedback = document.getElementById('conn-test-feedback');
  if (feedback) {
    feedback.innerHTML = '<span style="color: var(--accent-green);">✅ Settings saved and synced with backend!</span>';
  } else {
    alert('Settings saved successfully!');
  }
}

async function testAIConn() {
  const provider = document.getElementById('setting-provider').value;
  const apiKey = document.getElementById('setting-api-key').value;
  savedApiKeys[provider] = apiKey;

  const feedback = document.getElementById('conn-test-feedback');
  if (feedback) {
    feedback.innerHTML = `<span style="color: var(--primary-blue);">🔌 Testing connection to ${provider}...</span>`;
  }

  const res = await window.electronAPI.testAIConnection({ provider, apiKey });
  if (feedback) {
    if (res.success) {
      feedback.innerHTML = `<span style="color: var(--accent-green);">✅ ${res.message || 'Connected successfully!'} (${res.response_time || 0}s)</span>`;
    } else {
      feedback.innerHTML = `<span style="color: var(--accent-red);">❌ Connection failed: ${res.message || res.error || 'Error'}</span>`;
    }
  } else {
    alert(res.success ? `Connection to ${provider} successful!` : `Connection failed: ${res.message || 'Error'}`);
  }
}

// Initial navigation load
navigate('dashboard');
