# CleanGenius AI

> AI-Powered Windows Disk Cleanup Utility with DeepSeek Integration

CleanGenius AI is a modern Windows disk cleanup application designed for developers and power users. Powered by AI models (DeepSeek, OpenAI, Claude, Gemini, Ollama), it automatically scans, analyzes, and provides conservative cleanup recommendations for temporary files, build caches (`node_modules`, `__pycache__`), logs, installers, and registry entries.

---

## 💻 How to Download and Install the `.exe` File

You do **not** need to compile the code locally to install CleanGenius AI on your Windows machine. GitHub automatically generates the `.exe` installer for every push and release.

### Step-by-Step Installation Guide

1. **Download the Executable (.exe)**:
   - Go to the **Actions** tab on the GitHub repository.
   - Click on the latest **Build and Release CleanGenius AI Installer (.exe)** workflow run.
   - Scroll down to the **Artifacts** section and download `CleanGenius-AI-Setup.zip`.
   - Extract the zip archive to find `CleanGenius-AI-Setup.exe`.

2. **Run the Installer**:
   - Double-click `CleanGenius-AI-Setup.exe`.
   - Windows SmartScreen may show a prompt; click **More info** -> **Run anyway**.
   - Follow the stage-by-stage installation setup wizard to select your installation directory and create desktop/start menu shortcuts.

3. **In-App Stage-by-Stage Onboarding Guide**:
   - Launch CleanGenius AI after installation.
   - The application opens the **5-Stage Guided Setup Wizard**:
     - **Stage 1**: System Compatibility Check
     - **Stage 2**: AI Provider & Free DeepSeek API Key Configuration Guide
     - **Stage 3**: Default Scan & Folder Exclusions Selection
     - **Stage 4**: Safety, Backup & Rollback Retention Setup
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

### Quick Commands

```bash
# Clone repository
git clone https://github.com/yourusername/cleangenius-ai.git
cd cleangenius-ai

# Install dependencies
npm install
pip install -r requirements.txt

# Run development mode
npm run dev

# Compile standalone Windows .exe installer
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
