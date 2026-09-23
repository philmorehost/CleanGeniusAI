# CleanGenius AI

> AI-Powered Windows Disk Cleanup Utility with DeepSeek Integration

CleanGenius AI is a modern Windows disk cleanup application designed for developers and power users. Powered by AI models (DeepSeek, OpenAI, Claude, Gemini, Ollama), it automatically scans, analyzes, and provides conservative cleanup recommendations for temporary files, build caches (`node_modules`, `__pycache__`), logs, installers, and registry entries.

---

## 💻 How to Download and Install the `.exe` File

You do **not** need to compile the code locally to install CleanGenius AI on your Windows machine. GitHub automatically builds the `.exe` installer.

### Method 1: Download from GitHub Releases (Recommended)
1. Go to the **Releases** page on the right sidebar of the GitHub repository (or navigate to `https://github.com/yourusername/cleangenius-ai/releases`).
2. Download `CleanGenius-AI-Setup-1.0.0.exe` directly under **Assets**.
3. Double-click the downloaded `.exe` installer to run the setup wizard.

### Method 2: Download from Actions Tab (Artifacts)
1. Go to the **Actions** tab on GitHub.
2. Click on the latest run of **Build and Release CleanGenius AI Installer (.exe)** workflow.
3. Scroll down to the **Artifacts** section at the bottom of the summary page and click **CleanGenius-AI-Setup** to download the zip artifact.
4. Unzip `CleanGenius-AI-Setup.zip` to extract `CleanGenius-AI-Setup-1.0.0.exe`.

---

## 🚀 In-App Stage-by-Stage Onboarding Guide

When you launch CleanGenius AI for the first time, the application presents a **5-Stage Setup Wizard**:

- **Stage 1**: System Compatibility & Free Disk Space Diagnostic
- **Stage 2**: AI Engine & API Key Setup (Step-by-step guide to get a free DeepSeek API key)
- **Stage 3**: Default Scan Locations & Developer Exclusions
- **Stage 4**: Safety Policy & Instant Recovery Point Configuration
- **Stage 5**: Setup Complete & Trigger Initial Fast Scan

---

## 🌟 Key Features

- ⚡ **Multi-Engine Scanning**: Fast scan, Deep scan, Custom folder scan, and Registry analysis.
- 🤖 **Multi-Provider AI Analysis**: DeepSeek (default, cost-effective), OpenAI, Claude, Gemini, and Ollama local models.
- 🛡️ **3-Layer Safety Verification**: Protected path verification, active process lock checking, and system attribute detection.
- 🔄 **Instant Rollback Point**: Backs up deleted files to a recovery location before deletion so you can restore anytime.
- 📊 **Cost & Usage Dashboard**: Real-time monthly AI API cost tracking with budget limits.
- 💼 **IObitASC-Inspired Dark UI**: Custom frameless titlebar with dark aesthetic.

---

## 🛠️ Development & Building from Source

### Prerequisites
- Node.js (v18+)
- Python (3.10+)

```bash
# Clone repository
git clone https://github.com/yourusername/cleangenius-ai.git
cd cleangenius-ai

# Install dependencies
npm install
pip install -r requirements.txt

# Run development mode
npm run dev

# Compile standalone Windows .exe installer locally
npm run build
```

---

## 📖 Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design & internal flow.
- [API.md](API.md) - REST API specification for Python Flask backend.
- [CONTRIBUTING.md](CONTRIBUTING.md) - Developer guidelines & environment setup.
- [CHANGELOG.md](CHANGELOG.md) - Version history.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
